import os
import re
import json
import math
import fcntl
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import yaml

from hangar.records import Record

class ResearchUnavailable(Exception):
    pass

def public_brief(rec: Record, unknown_id: str) -> str:
    unknown = next((u for u in rec.unknowns if u["id"] == unknown_id), None)
    if unknown is None:
        raise KeyError(f"Unknown {unknown_id} not found")
    
    lines = [rec.question, unknown["text"], unknown["how"]]
    
    # Get option order from rec.options
    option_map = {opt["id"]: opt for opt in rec.options}
    for opt_id in unknown.get("affects", []):
        if opt_id in option_map:
            opt = option_map[opt_id]
            lines.append(opt["label"])
            for fact in opt.get("facts", []):
                lines.append(fact["text"])
                
    lines.append("Find a PUBLIC source that states this value.")
    return "\n".join(lines)

def _norm_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Cf")
    text = re.sub(r"\s+", " ", text)
    return text.strip().casefold()


_NUM_TOKEN = re.compile(
    r"(?<![0-9A-Za-z.])"
    r"([+-]?(?:\d{1,3}(?:[, ]\d{3})+|\d+)(?:\.\d+)?(?:[eE][+-]?\d+)?)"
    r"(?![0-9A-Za-z.])"
)


def _parse_number_token(token: str):
    try:
        value = float(token.replace(" ", "").replace(",", ""))
    except ValueError:
        return None
    if not math.isfinite(value):
        return None
    return value


def _whole_string_number(text: str):
    stripped = text.strip()
    if not re.fullmatch(r"[+-]?(?:\d{1,3}(?:[, ]\d{3})+|\d+)(?:\.\d+)?(?:[eE][+-]?\d+)?", stripped):
        return None
    return _parse_number_token(stripped)


def _collect_private(node, labels: list, phrases: list, numbers: list, key=None) -> None:
    if isinstance(key, str) and "transcript" in key.casefold():
        return
    if isinstance(node, dict):
        for child_key, child in node.items():
            if child_key == "label" and isinstance(child, str):
                labels.append(child)
            else:
                _collect_private(child, labels, phrases, numbers, key=child_key)
    elif isinstance(node, list):
        for child in node:
            _collect_private(child, labels, phrases, numbers, key=key)
    elif isinstance(node, str):
        parsed = _whole_string_number(node)
        if parsed is not None:
            numbers.append(parsed)
        else:
            phrases.append(node)
    elif isinstance(node, bool):
        return
    elif isinstance(node, (int, float)) and math.isfinite(float(node)):
        numbers.append(float(node))


def assert_public(text: str, private_dir: str | None, record=None) -> None:
    if private_dir is None and record is None:
        return

    labels: list[str] = []
    phrases: list[str] = []
    numbers: list[float] = []
    if private_dir is not None:
        mission_file = Path(private_dir) / "mission.yaml"
        if mission_file.exists():
            try:
                loaded = yaml.safe_load(mission_file.read_text(encoding="utf-8"))
            except Exception as exc:
                raise ValueError("mission.yaml cannot be parsed") from exc
            _collect_private(loaded, labels, phrases, numbers)

    if record is not None:
        for attr in ("positions", "history", "decision"):
            _collect_private(getattr(record, attr, None), labels, phrases, numbers)

    folded = _norm_text(text)
    for label in labels:
        secret = _norm_text(label)
        if len(secret) < 2:
            continue
        if re.search(rf"(?<![0-9a-z]){re.escape(secret)}(?![0-9a-z])", folded):
            raise ValueError(f"Private label leak: {label}")
    for phrase in phrases:
        secret = _norm_text(phrase)
        if len(secret) >= 4 and secret in folded:
            raise ValueError(f"Private text leak: {phrase}")
    if not numbers:
        return
    for match in _NUM_TOKEN.finditer(folded):
        parsed = _parse_number_token(match.group(1))
        if parsed is None:
            continue
        for secret in numbers:
            if math.isclose(parsed, secret, rel_tol=1e-9, abs_tol=1e-9):
                raise ValueError(f"Private weight leak: {secret}")

def _save_job(path: Path, job_dict: dict):
    tmp_fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(tmp_fd, 'w') as f:
            json.dump(job_dict, f)
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise

def _sanitize_id(raw: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "-", raw)


def _id_ok(value) -> bool:
    """One filename rule for queue_job and load_job: no traversal and no sanitizer alias."""
    if not isinstance(value, str) or "/" in value or "\\" in value or ".." in value:
        return False
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value):
        return False
    return _sanitize_id(value) == value


def queue_job(private_dir: str, rec: Record, unknown_id: str, now: str | None = None) -> dict:
    unknown = next((u for u in rec.unknowns if u["id"] == unknown_id), None)
    if unknown is None:
        raise KeyError(f"Unknown {unknown_id} not found")
    if unknown["state"] != "open":
        raise ValueError(f"Unknown {unknown_id} is not open")
    if not _id_ok(rec.id) or not _id_ok(unknown_id):
        raise ValueError(f"Invalid id for {rec.id} and {unknown_id}")

    # Check for existing jobs
    existing_jobs = list(Path(private_dir).glob("research/*.json"))
    known_ids = set()
    count = 0
    for j_path in existing_jobs:
        try:
            with open(j_path, "r", encoding="utf-8") as handle:
                loaded = json.load(handle)
        except (json.JSONDecodeError, KeyError, OSError):
            continue
        if loaded.get("record_id") != rec.id:
            continue
        other = loaded.get("unknown_id")
        if isinstance(other, str):
            known_ids.add(other)
        if other == unknown_id:
            count += 1
            if loaded.get("state") in ("queued", "running", "proposed"):
                raise ValueError(f"Job for {rec.id} and {unknown_id} already exists")
    if any(other != unknown_id and _sanitize_id(other) == _sanitize_id(unknown_id) for other in known_ids):
        raise ValueError(f"Job id for {unknown_id} collides with an existing id")

    brief = public_brief(rec, unknown_id)
    assert_public(brief, private_dir, record=rec)

    job_id = f"{rec.id}--{unknown_id}--{count + 1}"
    
    job = {
        "id": job_id,
        "record_id": rec.id,
        "unknown_id": unknown_id,
        "state": "queued",
        "created": now or datetime.now(timezone.utc).isoformat(),
        "brief": brief,
        "proposal": None,
        "spotcheck": None,
        "error": None,
        "note": None
    }
    
    target_dir = Path(private_dir) / "research"
    target_dir.mkdir(parents=True, exist_ok=True)
    _save_job(target_dir / f"{job_id}.json", job)
    return job

def list_jobs(private_dir: str, record_id: str | None = None) -> list[dict]:
    p_dir = Path(private_dir) / "research"
    if not p_dir.exists():
        return []
    
    jobs = []
    for f in sorted(p_dir.glob("*.json")):
        try:
            with open(f, "r") as jf:
                j = json.load(jf)
                if record_id is None or j.get("record_id") == record_id:
                    jobs.append(j)
        except:
            continue
    return sorted(jobs, key=lambda x: x["id"])

def load_job(private_dir: str, job_id: str) -> dict:
    if not _id_ok(job_id):
        raise KeyError("Invalid job id")
    
    path = Path(private_dir) / "research" / f"{job_id}.json"
    if not path.exists():
        raise KeyError(f"Job {job_id} not found")
    
    with open(path, "r") as f:
        return json.load(f)

def _execute_job(path: Path, job: dict, lane_fn, spotcheck_fn) -> dict:
    try:
        proposal = lane_fn(job["brief"])
    except Exception as e:
        job["state"] = "failed"
        job["error"] = f"{type(e).__name__}: {e}"
        _save_job(path, job)
        return job

    # Validate proposal
    err = None
    if not isinstance(proposal, dict):
        err = "Proposal must be a dictionary"
    elif not isinstance(proposal.get("claim"), str) or not proposal["claim"]:
        err = "claim must be a non-empty string"
    elif not isinstance(proposal.get("url"), str) or not (proposal["url"].startswith("http://") or proposal["url"].startswith("https://")):
        err = "url must be a string starting with http:// or https://"
    elif not isinstance(proposal.get("quote"), str) or not proposal["quote"]:
        err = "quote must be a non-empty string"
    elif not isinstance(proposal.get("title"), str):
        err = "title must be a string"
    elif not (isinstance(proposal.get("value"), (int, float)) or proposal.get("value") is None) or isinstance(proposal.get("value"), bool):
        err = "value must be a number or null"

    if err:
        job["state"] = "failed"
        job["error"] = err
        job["proposal"] = None
        _save_job(path, job)
        return job

    try:
        spotcheck = spotcheck_fn(proposal)
    except Exception as e:
        job["state"] = "failed"
        job["error"] = str(e)
        _save_job(path, job)
        return job

    job["state"] = "proposed"
    job["proposal"] = proposal
    job["spotcheck"] = spotcheck
    _save_job(path, job)
    return job


def run_job(private_dir: str, job_id: str, lane_fn, spotcheck_fn) -> dict:
    if not _id_ok(job_id):
        raise KeyError("Invalid job id")
    path = Path(private_dir) / "research" / f"{job_id}.json"
    lock_path = path.with_name(path.name + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "a+", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            job = load_job(private_dir, job_id)
            if job["state"] != "queued":
                raise ValueError(f"Job {job_id} is {job['state']}, not queued")
            job["state"] = "running"
            _save_job(path, job)
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)

    try:
        return _execute_job(path, job, lane_fn, spotcheck_fn)
    finally:
        # BaseException, including KeyboardInterrupt, must not leave the job running.
        if job.get("state") == "running":
            job["state"] = "failed"
            if not job.get("error"):
                job["error"] = "interrupted"
            _save_job(path, job)

def abandon_job(private_dir: str, job_id: str, error: str) -> dict:
    """Fail a queued or running job. Finished jobs are left untouched. The write is atomic."""
    job = load_job(private_dir, job_id)
    if job.get("state") not in ("queued", "running"):
        return job
    job["state"] = "failed"
    job["error"] = error
    _save_job(Path(private_dir) / "research" / f"{job_id}.json", job)
    return job


def finish_job(private_dir: str, job_id: str, state: str, note: str | None = None) -> dict:
    if state not in ("accepted", "dismissed"):
        raise ValueError(f"Invalid state: {state}")
    
    job = load_job(private_dir, job_id)
    if job["state"] != "proposed":
        raise ValueError(f"Job {job_id} is {job['state']}, not proposed")
    
    job["state"] = state
    job["note"] = note
    _save_job(Path(private_dir) / "research" / f"{job_id}.json", job)
    return job

def default_lane(brief: str, post=None, timeout_s=120) -> dict:
    url = os.environ.get("HANGAR_RESEARCH_URL")
    model = os.environ.get("HANGAR_RESEARCH_MODEL")
    key = os.environ.get("HANGAR_RESEARCH_KEY")
    
    if not url or not model:
        raise ResearchUnavailable("Environment variables missing")
    
    headers = {}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    
    system_msg = (
        "you are a research assistant; you only see public text; "
        "return ONLY one JSON object with the keys claim, value, unit, url, title, quote; "
        "the url must be a public web page you can name; the quote must be copied verbatim from that page; "
        "value is a number or null; if you cannot find a source return {\"claim\": \"\", \"url\": \"\", \"quote\": \"\"}"
    )
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": brief}
        ],
        "temperature": 0.1
    }

    if post:
        try:
            resp = post(payload, headers)
        except Exception as e:
            raise ResearchUnavailable(str(e))
    else:
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=timeout_s) as response:
                resp = json.loads(response.read().decode("utf-8"))
        except Exception as e:
            raise ResearchUnavailable(str(e))

    try:
        content = resp["choices"][0]["message"]["content"]
        # Find first JSON object in content
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            raise ValueError("No JSON found")
        result = json.loads(match.group(0))
        return result
    except Exception as e:
        raise ResearchUnavailable(str(e))
