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
import urllib.parse
from dataclasses import asdict
from datetime import date, datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import yaml

import guide.schema
from hangar import council
from hangar.council import CouncilUnavailable
from hangar.records import DATA_ROOT, dump_record, load_record, load_records, validate

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

            # Success
            today = date.today().isoformat()
            updated = copy.deepcopy(data)
            updated["status"] = "decided"
            cleaned = reason.strip()
            updated["decision"] = {"picks": picks, "date": today, "reason": cleaned}
            
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
            cleaned = reason.strip()
            history = list(updated.get("history") or [])
            history.append(
                {"date": today, "from": "decided", "to": "reopened", "reason": cleaned}
            )
            updated["history"] = history
            if self._commit(path, updated):
                return
        self._send_json(200, {"ok": True})


def make_server(
    site: Path,
    port: int,
    private_dir: Path,
    records_root: Path = DATA_ROOT,
    council: Any = council.ask,
    allow_origins: tuple[str, ...] = (),
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
