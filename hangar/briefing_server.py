"""Loopback briefing companion.

Serves a built guide site plus the briefing JSON API. Record edits are
re-validated and swapped into place with ``os.replace``. Transcripts stay
under the private directory, never in the repository.
"""

from __future__ import annotations

import argparse
from urllib.parse import urlsplit
import copy
import json
import os
import sys
import tempfile
import threading
import traceback
import urllib.parse
from dataclasses import asdict
from datetime import date, datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import yaml

import guide.schema
from hangar import council, research
from hangar.council import CouncilUnavailable
from hangar.matrix import matrix_for_effect
from hangar.matrix_extra import matrix_digest, private_matrix
from hangar.records import DATA_ROOT, dump_record, load_record, load_records, validate
from hangar.reopen import flag_reopen
from hangar.spotcheck import apply_patch, register_source, spotcheck_url

_ACCEPT_FAILED = "accept failed"
_WORKER_FAILED = "research worker failed"
_SCORE_FAILED = "an option's loading effect could not be scored"

_REPO_ROOT = Path(__file__).resolve().parents[1]
_LOOPBACK = "127.0.0.1"


def _normalize(value: Any) -> Any:
    """Turn date objects into ISO strings so the file round-trips as text."""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _normalize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    return value


def _atomic_write(
    path: Path, data: dict[str, Any], graph: Any, records_root: Path
) -> list[str]:
    """Validate ``data`` and replace ``path``.

    Returns validator errors (the destination is left untouched). Raises after
    deleting the temp file if the write itself fails.
    """
    fd, tmp_name = tempfile.mkstemp(prefix=".record-", suffix=".tmp", dir=path.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(dump_record(_normalize(data)))
        try:
            rec = load_record(tmp)
        except ValueError as exc:
            return [str(exc)]
        all_ids = set(load_records(records_root))
        errors = validate(rec, graph, all_ids)
        if errors:
            return list(errors)
        os.replace(tmp, path)
        return []
    finally:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass


def _find_record(root: Path, record_id: str) -> Path | None:
    found: Path | None = None
    for path in sorted(root.glob("*/decisions/*.yaml")):
        try:
            loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError):
            continue
        if isinstance(loaded, dict) and loaded.get("id") == record_id:
            found = path
    return found


def _read_mapping(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError("record file is not a mapping")
    return loaded


def _option_ids(data: dict[str, Any]) -> set[Any]:
    found: set[Any] = set()
    options = data.get("options") or []
    if not isinstance(options, list):
        return found
    for opt in options:
        if isinstance(opt, dict) and "id" in opt:
            found.add(opt["id"])
    return found


def _blank(value: object) -> bool:
    return not isinstance(value, str) or value.strip() == ""


def _transcript_path(private_dir: Path, record_id: str) -> Path:
    root = (Path(private_dir) / "transcripts").resolve()
    if (
        not record_id
        or record_id in {".", ".."}
        or "/" in record_id
        or "\\" in record_id
        or "\x00" in record_id
    ):
        raise ValueError("bad record id")
    path = (root / f"{record_id}.jsonl").resolve()
    if not path.is_relative_to(root):
        raise ValueError("bad record id")
    return path


def _load_turns(private_dir: Path, record_id: str) -> list[Any]:
    try:
        path = _transcript_path(private_dir, record_id)
    except ValueError:
        return []
    if not path.is_file():
        return []
    turns: list[Any] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            turns.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return turns


def _history_from(turns: list[Any]) -> list[dict[str, str]]:
    history: list[dict[str, str]] = []
    for turn in turns:
        if not isinstance(turn, dict):
            continue
        message = turn.get("message", "")
        reply = turn.get("reply")
        reply_text = reply.get("reply_text", "") if isinstance(reply, dict) else ""
        if not isinstance(message, str):
            message = "" if message is None else str(message)
        if not isinstance(reply_text, str):
            reply_text = "" if reply_text is None else str(reply_text)
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": reply_text})
    return history


def _reply_payload(reply: object) -> dict[str, Any]:
    positions = getattr(reply, "positions", None) or []
    unknowns = getattr(reply, "unknowns", None) or []
    reply_text = getattr(reply, "reply_text", "") or ""
    if not isinstance(reply_text, str):
        reply_text = str(reply_text)
    return {
        "positions": list(positions),
        "reply_text": reply_text,
        "unknowns": list(unknowns),
        "error": getattr(reply, "error", None),
    }


def _id_unknowns(data: dict[str, Any]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for row in data.get("unknowns") or []:
        if isinstance(row, dict) and isinstance(row.get("id"), str) and row["id"]:
            found.append(row)
    return found


def _open_unknown_ids(data: dict[str, Any]) -> list[str]:
    return [row["id"] for row in _id_unknowns(data) if row.get("state") in ("open", "researching")]


def _loadings_record(data: dict[str, Any]) -> bool:
    scoring = data.get("scoring")
    return isinstance(scoring, dict) and scoring.get("kind") == "loadings"


def _counted_option(opt: dict[str, Any]) -> bool:
    """Book and candidate options are scored. Dropped and unavailable are not."""
    return opt.get("kind") in ("book", "candidate")


def _unscored_ids(data: dict[str, Any]) -> list[str]:
    """A loadings option with no effect, or an effect that will not score, is an unknown matrix."""
    if not _loadings_record(data):
        return []
    found: list[str] = []
    for opt in data.get("options") or []:
        if not isinstance(opt, dict) or not _counted_option(opt):
            continue
        oid = opt.get("id")
        if not isinstance(oid, str):
            continue
        effect = opt.get("effect")
        if not isinstance(effect, dict):
            found.append(oid)
            continue
        try:
            matrix_for_effect(effect)
        except Exception:
            found.append(oid)
    return found


def _matrix_has_unknown_cells(data: dict[str, Any]) -> bool:
    if not _loadings_record(data):
        return False
    for opt in data.get("options") or []:
        if not isinstance(opt, dict) or opt.get("kind") in ("dropped", "unavailable"):
            continue
        effect = opt.get("effect")
        if not isinstance(effect, dict):
            continue
        try:
            made = matrix_for_effect(effect)
        except Exception:
            continue
        if made.get("unknown_cells", 0):
            return True
    return False


def _other_than_new_source(errors: list[str], source_id: str) -> list[str]:
    needle = f"unknown source id {source_id!r}"
    return [item for item in errors if needle not in item]


def _validation_errors(data: dict[str, Any], graph: Any, records_root: Path) -> list[str]:
    """Dry-run the record validator. The destination file is not touched."""
    fd, name = tempfile.mkstemp(prefix=".record-", suffix=".yaml")
    tmp = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(dump_record(_normalize(data)))
        try:
            rec = load_record(tmp)
        except ValueError as exc:
            return [str(exc)]
        ids: set[str] = set()
        for path in Path(records_root).glob("*/decisions/*.yaml"):
            try:
                loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, yaml.YAMLError):
                continue
            if isinstance(loaded, dict) and isinstance(loaded.get("id"), str):
                ids.add(loaded["id"])
        ids.add(rec.id)
        return list(validate(rec, graph, ids))
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass


def _preview_source_id(registry: Path, proposal: dict[str, Any], today: str) -> str:
    """The id register_source would assign, written only to a throwaway copy of the registry."""
    fd, name = tempfile.mkstemp(prefix=".registry-", suffix=".yaml")
    os.close(fd)
    tmp = Path(name)
    lock = tmp.with_name(tmp.name + ".lock")
    try:
        tmp.write_bytes(registry.read_bytes())
        return register_source(tmp, proposal, today)
    finally:
        for item in (tmp, lock):
            try:
                if item.exists():
                    item.unlink()
            except OSError:
                pass


class _Snap:
    """Bytes of the files an accept may change, so a later failure can put them back."""

    def __init__(self) -> None:
        self.files: dict[Path, bytes | None] = {}
        self.roots: list[Path] = []

    def keep(self, path: Path) -> None:
        path = Path(path)
        try:
            key = path.resolve()
        except OSError:
            key = path
        if key in self.files:
            return
        self.files[key] = path.read_bytes() if path.is_file() else None

    def keep_tree(self, root: Path) -> None:
        root = Path(root)
        try:
            key = root.resolve()
        except OSError:
            key = root
        self.roots.append(key)
        if not root.exists():
            return
        for path in root.rglob("*"):
            if path.is_file():
                self.keep(path)

    def restore(self) -> None:
        for path, data in self.files.items():
            if data is None:
                try:
                    if path.is_file():
                        path.unlink()
                except OSError:
                    pass
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        for root in self.roots:
            if not root.exists():
                continue
            for path in list(root.rglob("*")):
                if path.is_file() and path.resolve() not in self.files:
                    try:
                        path.unlink()
                    except OSError:
                        pass


def _patch_target(server: BriefingServer, data: dict[str, Any], proposal: dict[str, Any]) -> Path | None:
    patch = proposal.get("patch")
    if not isinstance(patch, dict):
        return None
    filename = patch.get("file")
    if filename not in ("powerplants.yaml", "mission.yaml"):
        return None
    data_dir = server.data_dir
    if data_dir is None:
        data_dir = Path(server.records_root) / str(data.get("spot") or "")
    return Path(data_dir) / str(filename)


def _log_skips() -> None:
    from hangar import mission as mission_mod
    from hangar import reopen as reopen_mod

    for line in list(mission_mod.last_errors) + list(reopen_mod.last_errors):
        print(line, file=sys.stderr)


def _find_unknown(data: dict[str, Any], unknown_id: object) -> dict[str, Any] | None:
    if not isinstance(unknown_id, str) or not unknown_id:
        return None
    for row in data.get("unknowns") or []:
        if isinstance(row, dict) and row.get("id") == unknown_id:
            return row
    return None


def _newest_job(jobs: list[dict[str, Any]], unknown_id: object) -> dict[str, Any] | None:
    if not isinstance(unknown_id, str):
        return None
    matched = [job for job in jobs if job.get("unknown_id") == unknown_id]
    if not matched:
        return None
    return max(matched, key=lambda job: (str(job.get("created") or ""), str(job.get("id") or "")))


def _reopen_unknown(server: BriefingServer, path: Path, unknown_id: str) -> None:
    """Put a researching unknown back to open. Raises if the record cannot be written."""
    with server.write_lock:
        data = _read_mapping(path)
        changed = False
        for row in data.get("unknowns") or []:
            if isinstance(row, dict) and row.get("id") == unknown_id and row.get("state") == "researching":
                row["state"] = "open"
                changed = True
        if not changed:
            return
        errors = _atomic_write(path, data, server.graph, server.records_root)
        if errors:
            raise ValueError("record rejected")


def _research_worker(server: BriefingServer, path: Path, unknown_id: str, job_id: str) -> None:
    """Run one queued job. Any failure abandons the job and puts the unknown back to open."""
    try:
        job = research.run_job(str(server.private_dir), job_id, server.research_lane, server.spotcheck)
        if not isinstance(job, dict) or job.get("state") != "failed":
            return
        _reopen_unknown(server, path, unknown_id)
    except Exception:
        traceback.print_exc(file=sys.stderr)
        try:
            research.abandon_job(str(server.private_dir), job_id, _WORKER_FAILED)
        except Exception:
            traceback.print_exc(file=sys.stderr)
        try:
            _reopen_unknown(server, path, unknown_id)
        except Exception:
            traceback.print_exc(file=sys.stderr)
            print("research worker could not reopen the unknown", file=sys.stderr)


def _recover_research(private_dir: Path, records_root: Path, graph: Any) -> None:
    """Abandon queued and running jobs left behind by a dead process, and reopen their unknowns."""
    try:
        jobs = research.list_jobs(str(private_dir))
    except Exception:
        return
    reopen_ids: dict[str, set[str]] = {}
    for job in jobs:
        if not isinstance(job, dict) or job.get("state") not in ("queued", "running"):
            continue
        job_id = job.get("id")
        if not isinstance(job_id, str):
            continue
        try:
            research.abandon_job(str(private_dir), job_id, "server restarted")
        except Exception:
            continue
        record_id = job.get("record_id")
        unknown_id = job.get("unknown_id")
        if isinstance(record_id, str) and isinstance(unknown_id, str):
            reopen_ids.setdefault(record_id, set()).add(unknown_id)
    if not reopen_ids:
        return
    for path in sorted(Path(records_root).glob("*/decisions/*.yaml")):
        try:
            data = _read_mapping(path)
        except Exception:
            continue
        record_id = data.get("id")
        if not isinstance(record_id, str) or record_id not in reopen_ids:
            continue
        wanted = reopen_ids[record_id]
        changed = False
        for row in data.get("unknowns") or []:
            if isinstance(row, dict) and row.get("id") in wanted and row.get("state") == "researching":
                row["state"] = "open"
                changed = True
        if not changed:
            continue
        try:
            _atomic_write(path, data, graph, records_root)
        except Exception:
            continue


def _dismiss_job(private_dir: str, job_id: str) -> dict:
    """Dismiss a proposed or failed job. Accept stays on the proposed-only path."""
    job = research.load_job(private_dir, job_id)
    state = job.get("state")
    if state == "proposed":
        return research.finish_job(private_dir, job_id, "dismissed")
    if state != "failed":
        raise ValueError(f"Job {job_id} is {state}, not proposed")
    job["state"] = "dismissed"
    job["note"] = None
    research._save_job(Path(private_dir) / "research" / f"{job_id}.json", job)
    return job


def _drop_new_jobs(private_dir: Path, before: set[str]) -> None:
    folder = Path(private_dir) / "research"
    if not folder.is_dir():
        return
    for path in folder.glob("*.json"):
        if path.name not in before:
            try:
                path.unlink()
            except OSError:
                pass


def _restore_bytes(path: Path, payload: bytes) -> None:
    fd, name = tempfile.mkstemp(prefix=".record-", suffix=".tmp", dir=path.parent)
    tmp = Path(name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass


def _refuse_private_dir(private_dir: Path, site: Path | None = None) -> None:
    resolved = Path(private_dir).resolve()
    if resolved.is_relative_to(_REPO_ROOT) or (site is not None and (
            resolved.is_relative_to(Path(site).resolve()) or Path(site).resolve().is_relative_to(resolved))):
        print("HANGAR_PRIVATE_DIR resolves inside the repository", file=sys.stderr)
        raise SystemExit(2)


class BriefingServer(ThreadingHTTPServer):
    """Threading server with the council callable looked up per request."""

    daemon_threads = True

    def __init__(
        self,
        port: int,
        handler: type[SimpleHTTPRequestHandler],
        *,
        site: Path,
        council_fn: Any,
        private_dir: Path,
        records_root: Path,
        graph: Any,
    ) -> None:
        self.site = site
        self.council = council_fn
        self.private_dir = private_dir
        self.records_root = records_root
        self.graph = graph
        self.write_lock = threading.Lock()
        super().__init__((_LOOPBACK, port), handler)


class BriefingHandler(SimpleHTTPRequestHandler):
    """Static site plus the briefing JSON routes."""

    server: BriefingServer

    def __init__(
        self, request: Any, client_address: Any, server: BriefingServer
    ) -> None:
        super().__init__(request, client_address, server, directory=str(server.site))

    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def send_response(self, code: int, message: str | None = None) -> None:
        self._responded = True
        super().send_response(code, message)

    def handle_one_request(self) -> None:
        try:
            super().handle_one_request()
        except Exception as exc:
            try:
                self._send_json(500, {"error": str(exc)})
            except Exception:
                return

    _MAX_BODY = 64 * 1024

    def _local_only(self) -> bool:
        """Refuse foreign Host (DNS rebinding) and foreign Origin (cross-site requests)."""
        port = self.server.server_address[1]
        allow = getattr(self.server, "allow_origins", ())
        hosts = {f"127.0.0.1:{port}", f"localhost:{port}"} | {urlsplit(o).netloc for o in allow}
        if self.headers.get("Host", "") not in hosts:
            self._send_json(403, {"error": "forbidden host"})
            return False
        origin = self.headers.get("Origin")
        if origin and origin not in {f"http://127.0.0.1:{port}", f"http://localhost:{port}", *allow}:
            self._send_json(403, {"error": "forbidden origin"})
            return False
        return True

    def list_directory(self, path):  # no directory listings
        self.send_error(404)
        return None

    def do_GET(self) -> None:
        if not self._local_only():
            return
        try:
            self._get()
        except Exception as exc:
            self._send_json(500, {"error": str(exc)})

    def do_POST(self) -> None:
        if not self._local_only():
            return
        if not self.headers.get("Content-Type", "").lower().startswith("application/json"):
            self._send_json(415, {"error": "content-type must be application/json"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
        except ValueError:
            length = 0
        if length > self._MAX_BODY:
            self._send_json(413, {"error": "body too large"})
            return
        try:
            self._post()
        except Exception as exc:
            self._send_json(500, {"error": str(exc)})

    def _send_json(self, code: int, payload: object, no_store: bool = False) -> None:
        if getattr(self, "_responded", False):
            return
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        if no_store:
            self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _get(self) -> None:
        path = urllib.parse.urlparse(self.path).path
        if path == "/api/health":
            self._send_json(200, {"ok": True})
            return
        if path == "/api/records":
            records = load_records(self.server.records_root)
            self._send_json(200, {rid: asdict(rec) for rid, rec in records.items()})
            return
        pp = "/api/pilots/"
        if path.startswith(pp):
            self._pilots(urllib.parse.unquote(path[len(pp) :]))
            return
        prefix = "/api/transcript/"
        if path.startswith(prefix):
            record_id = urllib.parse.unquote(path[len(prefix) :])
            self._send_json(200, _load_turns(self.server.private_dir, record_id))
            return
        matrix_prefix = "/api/matrix/"
        if path.startswith(matrix_prefix):
            self._matrix(urllib.parse.unquote(path[len(matrix_prefix) :]))
            return
        research_prefix = "/api/research/"
        if path.startswith(research_prefix):
            self._research_index(urllib.parse.unquote(path[len(research_prefix) :]))
            return
        if path.startswith("/api/"):
            self._send_json(404, {"error": "not found"})
            return
        super().do_GET()

    def _pilots(self, record_id: str) -> None:
        """Private per-owner margins for each option that declares an `effect`; empty when no pilots are configured. Never written to a record."""
        rec_path = self._record_path(record_id)
        if rec_path is None:
            self._send_json(404, {"error": "unknown record"})
            return
        from hangar import mission as _m

        data = _read_mapping(rec_path)
        by_label: dict[str, dict] = {}
        for opt in data.get("options") or []:
            if not isinstance(opt, dict) or not isinstance(opt.get("effect"), dict):
                continue
            try:
                engine, extras, plants = _m.apply_effect(opt["effect"])
                rows = _m.score_pilots(engine, extras=extras, plants=plants, private_dir=self.server.private_dir)
                err = None
            except Exception:  # a malformed effect must not 500 or echo anything private
                rows, err = [], "bad effect"
            if err:
                for label in {r["label"] for r in _m.score_pilots("rotax-912is", private_dir=self.server.private_dir)}:
                    entry = by_label.setdefault(label, {"label": label, "options": []})
                    entry["options"].append({"option": opt.get("id"), "error": err})
                continue
            for row in rows:
                entry = by_label.setdefault(row["label"], {"label": row["label"], "options": []})
                entry["options"].append({"option": opt.get("id"), **{k: row[k] for k in ("solo", "two_up_with", "two_up")}})
        self._send_json(200, {"pilots": list(by_label.values())}, no_store=True)

    def _read_json(self) -> dict[str, Any] | None:
        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
        except (TypeError, ValueError):
            length = 0
        raw = self.rfile.read(length) if length > 0 else b""
        try:
            body = json.loads(raw.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            return None
        if not isinstance(body, dict):
            return None
        return body

    def _post(self) -> None:
        path = urllib.parse.urlparse(self.path).path
        body = self._read_json()
        if path == "/api/brief":
            if body is None:
                self._send_json(400, {"error": "body is not JSON"})
                return
            self._brief(body)
            return
        if path == "/api/decide":
            if body is None:
                self._send_json(400, {"error": "body is not JSON"})
                return
            self._decide(body)
            return
        if path == "/api/reopen":
            if body is None:
                self._send_json(400, {"error": "body is not JSON"})
                return
            self._reopen(body)
            return
        if path == "/api/research":
            if body is None:
                self._send_json(400, {"error": "body is not JSON"})
                return
            self._research(body)
            return
        if path == "/api/research/resolve":
            if body is None:
                self._send_json(400, {"error": "body is not JSON"})
                return
            self._resolve(body)
            return
        self._send_json(404, {"error": "not found"})

    def _record_path(self, record_id: object) -> Path | None:
        if not isinstance(record_id, str) or not record_id:
            return None
        return _find_record(self.server.records_root, record_id)

    def _commit(self, path: Path, data: dict[str, Any]) -> bool:
        """Persist ``data``. Return True when an error response was sent."""
        try:
            errors = _atomic_write(
                path, data, self.server.graph, self.server.records_root
            )
        except Exception as exc:
            self._send_json(500, {"error": str(exc)})
            return True
        if errors:
            self._send_json(409, {"errors": errors})
            return True
        return False

    def _append_turn(self, record_id: str, message: str, reply: dict[str, Any]) -> None:
        path = _transcript_path(self.server.private_dir, record_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        line = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "message": message,
            "reply": {
                "positions": reply["positions"],
                "reply_text": reply["reply_text"],
                "unknowns": reply["unknowns"],
                "error": reply["error"],
            },
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(line) + "\n")

    def _brief(self, body: dict[str, Any]) -> None:
        message = body.get("message")
        if not isinstance(message, str) or message.strip() == "":
            self._send_json(400, {"error": "message is empty"})
            return
        path = self._record_path(body.get("record_id"))
        if path is None:
            self._send_json(404, {"error": "unknown record"})
            return
        rec = load_record(path)
        history = _history_from(_load_turns(self.server.private_dir, rec.id))
        try:
            reply = self.server.council(rec, message, history)
        except CouncilUnavailable as exc:
            self._send_json(503, {"error": str(exc)})
            return
        payload = _reply_payload(reply)
        with self.server.write_lock:
            self._append_turn(rec.id, message, payload)
            data = _read_mapping(path)
            if payload["error"] is None and payload["positions"] and data.get("status") != "decided":
                data["positions"] = copy.deepcopy(list(payload["positions"]))
                # The owner still gets the council's answer when the record can't take the positions;
                # the record stays byte-identical and the reason travels back as record_error.
                try:
                    errs = _atomic_write(path, data, self.server.graph, self.server.records_root)
                except Exception as exc:  # noqa: BLE001 - reported, never swallowed
                    errs = [str(exc)]
                if errs:
                    payload = dict(payload, record_error=list(errs))
        self._send_json(200, payload)

    def _decide(self, body: dict[str, Any]) -> None:
        path = self._record_path(body.get("record_id"))
        if path is None:
            self._send_json(404, {"error": "unknown record"})
            return
        with self.server.write_lock:
            data = _read_mapping(path)
            picks = body.get("picks")
            reason = body.get("reason")

            # Validation
            if not isinstance(picks, dict) or not picks:
                self._send_json(400, {"error": "decision rejected"})
                return
            if not isinstance(reason, str) or _blank(reason):
                self._send_json(400, {"error": "decision rejected"})
                return
            if data.get("status") == "decided":
                self._send_json(400, {"error": "decision rejected"})
                return

            # Check axes and options
            axes = data.get("axes", [])
            if not isinstance(axes, list):
                self._send_json(400, {"error": "decision rejected"})
                return

            # Map axis_id -> options_list
            axis_map = {a["id"]: a.get("options", []) for a in axes if isinstance(a, dict) and "id" in a}
            
            # 1. Check if all axes in record have a pick
            if len(picks) != len(axis_map):
                self._send_json(400, {"error": "decision rejected"})
                return
            
            # 2. Check if every pick is a valid axis and valid option
            for axis_id, option_id in picks.items():
                if axis_id not in axis_map:
                    self._send_json(400, {"error": "decision rejected"})
                    return
                
                options = axis_map[axis_id]
                if not isinstance(options, list):
                    self._send_json(400, {"error": "decision rejected"})
                    return
                
                # Check if option_id is a string in the options list
                kind = next((o.get("kind") for o in (data.get("options") or []) if isinstance(o, dict) and o.get("id") == option_id), None)
                if (
                    not isinstance(option_id, str)
                    or option_id not in options
                    or kind in ("dropped", "unavailable")
                ):
                    self._send_json(400, {"error": "decision rejected"})
                    return

            unscored = _unscored_ids(data)
            if unscored or _matrix_has_unknown_cells(data):
                required = _open_unknown_ids(data)
                acknowledged = body.get("acknowledged_unknowns")
                if not isinstance(acknowledged, list):
                    acknowledged = []
                missing = [item for item in required if item not in acknowledged]
                if missing:
                    payload: dict[str, Any] = {
                        "error": "unknown cells not acknowledged",
                        "unknowns": missing,
                    }
                    if unscored:
                        payload["unscored"] = unscored
                    self._send_json(409, payload)
                    return

            # Success
            today = date.today().isoformat()
            updated = copy.deepcopy(data)
            updated["status"] = "decided"
            cleaned = reason.strip()
            decision: dict[str, Any] = {"picks": picks, "date": today, "reason": cleaned}
            if _id_unknowns(data):
                decision["over_unknowns"] = _open_unknown_ids(data)
            scoring = data.get("scoring")
            if isinstance(scoring, dict) and scoring.get("kind") == "loadings":
                digest: dict[str, str] = {}
                try:
                    for opt in data.get("options") or []:
                        if (
                            isinstance(opt, dict)
                            and isinstance(opt.get("effect"), dict)
                            and isinstance(opt.get("id"), str)
                            and opt.get("kind") not in ("dropped", "unavailable")
                        ):
                            digest[opt["id"]] = matrix_digest(opt["effect"])
                except Exception:
                    self._send_json(409, {"error": _SCORE_FAILED})
                    return
                decision["matrix_digest"] = digest
            updated["decision"] = decision
            
            history = list(updated.get("history") or [])
            history.append(
                {
                    "date": today,
                    "from": data.get("status"),
                    "to": "decided",
                    "reason": cleaned,
                    "picks": picks,
                }
            )
            updated["history"] = history
            if self._commit(path, updated):
                return
        self._send_json(200, {"ok": True})

    def _reopen(self, body: dict[str, Any]) -> None:
        path = self._record_path(body.get("record_id"))
        if path is None:
            self._send_json(404, {"error": "unknown record"})
            return
        with self.server.write_lock:
            data = _read_mapping(path)
            reason = body.get("reason")
            if data.get("status") != "decided" or _blank(reason):
                self._send_json(400, {"error": "reopen rejected"})
                return
            if not isinstance(reason, str):
                self._send_json(400, {"error": "reopen rejected"})
                return
            today = date.today().isoformat()
            updated = copy.deepcopy(data)
            updated["status"] = "reopened"
            updated.pop("reopen_flag", None)
            cleaned = reason.strip()
            history = list(updated.get("history") or [])
            history.append(
                {"date": today, "from": "decided", "to": "reopened", "reason": cleaned}
            )
            updated["history"] = history
            if self._commit(path, updated):
                return
        self._send_json(200, {"ok": True})

    def _matrix(self, record_id: str) -> None:
        path = self._record_path(record_id)
        if path is None:
            self._send_json(404, {"error": "unknown record"})
            return
        data = _read_mapping(path)
        jobs = research.list_jobs(str(self.server.private_dir), record_id)
        loadings = _loadings_record(data)
        options = []
        for opt in data.get("options") or []:
            if not isinstance(opt, dict):
                continue
            entry: dict[str, Any] = {
                "option": opt.get("id"),
                "label": opt.get("label") if isinstance(opt.get("label"), str) else "",
                "public": None,
                "private": None,
            }
            effect = opt.get("effect")
            if loadings and _counted_option(opt) and not isinstance(effect, dict):
                entry["unscored"] = True
            elif isinstance(effect, dict):
                try:
                    entry["public"] = matrix_for_effect(effect)
                except Exception:
                    entry["public"] = None
                    entry["error"] = "bad effect"
                    entry["private"] = None
                else:
                    try:
                        entry["private"] = private_matrix(effect, self.server.private_dir)
                    except Exception:
                        entry["private"] = None
            options.append(entry)
        unknowns = []
        for row in data.get("unknowns") or []:
            if not isinstance(row, dict):
                continue
            item = {
                "id": row.get("id"),
                "text": row.get("text"),
                "how": row.get("how"),
                "state": row.get("state"),
                "affects": row.get("affects") if isinstance(row.get("affects"), list) else [],
                "job": _newest_job(jobs, row.get("id")),
            }
            if "source" in row:
                item["source"] = row["source"]
            unknowns.append(item)
        self._send_json(200, {"record_id": record_id, "options": options, "unknowns": unknowns}, no_store=True)

    def _research_index(self, record_id: str) -> None:
        jobs = research.list_jobs(str(self.server.private_dir), record_id)
        self._send_json(200, {"jobs": jobs}, no_store=True)

    def _research(self, body: dict[str, Any]) -> None:
        path = self._record_path(body.get("record_id"))
        if path is None:
            self._send_json(404, {"error": "unknown record"})
            return
        unknown_id = body.get("unknown_id")
        with self.server.write_lock:
            data = _read_mapping(path)
            unknown = _find_unknown(data, unknown_id)
            if unknown is None:
                self._send_json(400, {"error": "unknown unknown"})
                return
            if unknown.get("state") != "open":
                self._send_json(400, {"error": "unknown is not open"})
                return
            rec = load_record(path)
            original = path.read_bytes()
            unknown["state"] = "researching"
            if self._commit(path, data):
                return
            research_dir = Path(self.server.private_dir) / "research"
            before_jobs = {item.name for item in research_dir.glob("*.json")} if research_dir.is_dir() else set()

            def _undo(code: int, error: str) -> None:
                _restore_bytes(path, original)
                _drop_new_jobs(Path(self.server.private_dir), before_jobs)
                self._send_json(code, {"error": error})

            try:
                job = research.queue_job(str(self.server.private_dir), rec, unknown_id)
            except KeyError as exc:
                _undo(400, str(exc))
                return
            except ValueError as exc:
                text = str(exc)
                _undo(409 if "already" in text else 400, text)
                return
            except Exception:
                _undo(409, "research could not be queued")
                return
        threading.Thread(
            target=_research_worker,
            args=(self.server, path, unknown_id, job["id"]),
            daemon=True,
        ).start()
        self._send_json(202, {"job": job})

    def _resolve(self, body: dict[str, Any]) -> None:
        outcome = body.get("outcome")
        if outcome not in ("accept", "dismiss", "unsourceable"):
            self._send_json(400, {"error": "bad outcome"})
            return
        job_id = body.get("job_id")
        if not isinstance(job_id, str):
            self._send_json(404, {"error": "unknown job"})
            return
        try:
            job = research.load_job(str(self.server.private_dir), job_id)
        except KeyError:
            self._send_json(404, {"error": "unknown job"})
            return
        path = self._record_path(job.get("record_id"))
        if path is None:
            self._send_json(404, {"error": "unknown record"})
            return
        if outcome == "accept":
            self._accept(path, job)
            return
        self._close_research(path, job, "unsourceable" if outcome == "unsourceable" else "open")

    def _accept(self, path: Path, job: dict[str, Any]) -> None:
        from core.sources import load_registry
        from hangar.mission import write_scores

        with self.server.write_lock:
            try:
                job = research.load_job(str(self.server.private_dir), job["id"])
            except KeyError:
                self._send_json(404, {"error": "unknown job"})
                return
            spot = job.get("spotcheck")
            if job.get("state") != "proposed" or not (isinstance(spot, dict) and spot.get("matched") is True):
                reason = "job is not proposed" if job.get("state") != "proposed" else "spot-check did not match"
                self._send_json(409, {"error": reason})
                return
            proposal = job.get("proposal")
            if not isinstance(proposal, dict):
                self._send_json(409, {"error": "job has no proposal"})
                return
            registry = Path(self.server.registry_path)
            today = date.today().isoformat()
            try:
                source_id = _preview_source_id(registry, proposal, today)
                data = _read_mapping(path)
                updated = copy.deepcopy(data)
                unknown = _find_unknown(updated, job.get("unknown_id"))
                if unknown is None:
                    self._send_json(409, {"error": _ACCEPT_FAILED})
                    return
                unknown["state"] = "sourced"
                unknown["source"] = source_id
                if _other_than_new_source(
                    _validation_errors(updated, self.server.graph, self.server.records_root), source_id
                ):
                    self._send_json(409, {"error": _ACCEPT_FAILED})
                    return
            except Exception:
                traceback.print_exc(file=sys.stderr)
                self._send_json(409, {"error": _ACCEPT_FAILED})
                return

            snap = _Snap()
            snap.keep(registry)
            target = _patch_target(self.server, data, proposal)
            if target is not None:
                snap.keep(target)
            snap.keep(Path(self.server.private_dir) / "research" / f"{job['id']}.json")
            snap.keep_tree(self.server.records_root)
            try:
                source_id = register_source(registry, proposal, today)
                load_registry.cache_clear()
                unknown["source"] = source_id
                if _validation_errors(updated, self.server.graph, self.server.records_root):
                    raise RuntimeError("record rejected")
                patch = proposal.get("patch")
                if patch is not None:
                    data_dir = self.server.data_dir
                    if data_dir is None:
                        data_dir = self.server.records_root / str(data.get("spot") or "")
                    apply_patch(data_dir, patch, source_id)
                errors = _atomic_write(path, updated, self.server.graph, self.server.records_root)
                if errors:
                    raise RuntimeError("record rejected")
                finished = research.finish_job(str(self.server.private_dir), job["id"], "accepted")
                write_scores(self.server.records_root)
                reopened = flag_reopen(self.server.records_root)
                _log_skips()
            except Exception:
                traceback.print_exc(file=sys.stderr)
                try:
                    snap.restore()
                except Exception:
                    traceback.print_exc(file=sys.stderr)
                try:
                    load_registry.cache_clear()
                except Exception:
                    traceback.print_exc(file=sys.stderr)
                self._send_json(409, {"error": _ACCEPT_FAILED})
                return
        self._send_json(200, {"ok": True, "job": finished, "reopened": reopened})

    def _close_research(self, path: Path, job: dict[str, Any], unknown_state: str) -> None:
        with self.server.write_lock:
            try:
                fresh = research.load_job(str(self.server.private_dir), job["id"])
                finished = _dismiss_job(str(self.server.private_dir), fresh["id"])
            except (KeyError, ValueError) as exc:
                self._send_json(409, {"error": str(exc)})
                return
            data = _read_mapping(path)
            unknown = _find_unknown(data, job.get("unknown_id"))
            if unknown is not None:
                unknown["state"] = unknown_state
                if self._commit(path, data):
                    return
        self._send_json(200, {"ok": True, "job": finished, "reopened": []})


def make_server(
    site: Path,
    port: int,
    private_dir: Path,
    records_root: Path = DATA_ROOT,
    council: Any = council.ask,
    allow_origins: tuple[str, ...] = (),
    research_lane: Any = None,
    spotcheck: Any = None,
    registry_path: Path | None = None,
    data_dir: Path | None = None,
) -> ThreadingHTTPServer:
    """Bind the briefing service on loopback and return it (not yet serving).

    ``allow_origins`` adds origins (``scheme://host[:port]``) of a private reverse proxy in front of the
    loopback socket; their host is accepted in ``Host`` too. The socket itself stays loopback-only."""
    _refuse_private_dir(private_dir, site)
    graph = guide.schema.load_graph(_REPO_ROOT / "guide" / "graph")
    server = BriefingServer(
        port,
        BriefingHandler,
        site=Path(site),
        council_fn=council,
        private_dir=Path(private_dir),
        records_root=Path(records_root),
        graph=graph,
    )
    server.allow_origins = tuple(allow_origins)
    server.research_lane = research.default_lane if research_lane is None else research_lane
    server.spotcheck = spotcheck_url if spotcheck is None else spotcheck
    server.registry_path = (
        _REPO_ROOT / "data" / "sources" / "registry.yaml" if registry_path is None else Path(registry_path)
    )
    server.data_dir = None if data_dir is None else Path(data_dir)
    _recover_research(Path(private_dir), Path(records_root), graph)
    return server


def main(argv: list[str] | None = None) -> None:
    """Parse ``--site`` / ``--port`` and serve until interrupted."""
    parser = argparse.ArgumentParser(description="Hangar briefing companion")
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8097)
    parser.add_argument("--allow-origin", action="append", default=[],
                        help="origin of a private reverse proxy, e.g. https://host:port (repeatable)")
    args = parser.parse_args(argv)
    private = os.environ.get("HANGAR_PRIVATE_DIR")
    if private is None or not str(private).strip():
        print("HANGAR_PRIVATE_DIR is unset", file=sys.stderr)
        raise SystemExit(2)
    make_server(args.site, args.port, Path(str(private).strip()),
                allow_origins=tuple(o.rstrip("/") for o in args.allow_origin)).serve_forever()


if __name__ == "__main__":
    main()
