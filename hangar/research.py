import os
import re
import json
import tempfile
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

def assert_public(text: str, private_dir: str | None) -> None:
    if private_dir is None:
        return
    
    p_dir = Path(private_dir)
    mission_file = p_dir / "mission.yaml"
    if not mission_file.exists():
        return
    
    try:
        with open(mission_file, "r") as f:
            data = yaml.safe_load(f)
    except Exception:
        return

    if not isinstance(data, dict):
        return

    # Check pilot labels
    pilots = data.get("pilots", [])
    if isinstance(pilots, list):
        for pilot in pilots:
            label = pilot.get("label")
            if isinstance(label, str) and len(label) >= 3:
                pattern = rf"(?<![A-Za-z0-9]){re.escape(label)}(?![A-Za-z0-9])"
                if re.search(pattern, text, re.IGNORECASE):
                    raise ValueError(f"Private label leak: {label}")

    # Check weights
    def check_weights(val):
        if isinstance(val, (int, float)):
            # repr(float) might be 133.37 or 133.0
            s = repr(float(val))
            if s.endswith(".0"):
                s = s[:-2]
            pattern = rf"(?<![0-9.]){re.escape(s)}(?![0-9])"
            if re.search(pattern, text):
                raise ValueError(f"Private weight leak: {val}")
        elif isinstance(val, list):
            for item in val:
                check_weights(item)

    check_weights(data.get("bags_lb"))
    if isinstance(pilots, list):
        for pilot in pilots:
            check_weights(pilot.get("lb"))

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

def queue_job(private_dir: str, rec: Record, unknown_id: str, now: str | None = None) -> dict:
    unknown = next((u for u in rec.unknowns if u["id"] == unknown_id), None)
    if unknown is None:
        raise KeyError(f"Unknown {unknown_id} not found")
    if unknown["state"] != "open":
        raise ValueError(f"Unknown {unknown_id} is not open")
    
    # Check for existing jobs
    existing_jobs = list(Path(private_dir).glob("research/*.json"))
    for j_path in existing_jobs:
        try:
            with open(j_path, "r") as f:
                j = json.load(f)
                if j["record_id"] == rec.id and j["unknown_id"] == unknown_id:
                    if j["state"] in ("queued", "running", "proposed"):
                        raise ValueError(f"Job for {rec.id} and {unknown_id} already exists")
        except (json.JSONDecodeError, KeyError, IOError):
            continue

    brief = public_brief(rec, unknown_id)
    assert_public(brief, private_dir)

    # Sanitize ID
    clean_rec_id = re.sub(r"[^A-Za-z0-9._-]", "-", rec.id)
    clean_unk_id = re.sub(r"[^A-Za-z0-9._-]", "-", unknown_id)
    
    count = 0
    for j_path in existing_jobs:
        try:
            with open(j_path, "r") as f:
                j = json.load(f)
                if j["record_id"] == rec.id and j["unknown_id"] == unknown_id:
                    count += 1
        except: continue
    
    job_id = f"{clean_rec_id}--{clean_unk_id}--{count + 1}"
    
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
    if not re.match(r"^[A-Za-z0-9][A-Za-z0-9._-]*$", job_id) or ".." in job_id:
        raise KeyError("Invalid job id")
    
    path = Path(private_dir) / "research" / f"{job_id}.json"
    if not path.exists():
        raise KeyError(f"Job {job_id} not found")
    
    with open(path, "r") as f:
        return json.load(f)

def run_job(private_dir: str, job_id: str, lane_fn, spotcheck_fn) -> dict:
    job = load_job(private_dir, job_id)
    if job["state"] != "queued":
        raise ValueError(f"Job {job_id} is {job['state']}, not queued")
    
    job["state"] = "running"
    _save_job(Path(private_dir) / "research" / f"{job_id}.json", job)
    
    try:
        proposal = lane_fn(job["brief"])
    except Exception as e:
        job["state"] = "failed"
        job["error"] = f"{type(e).__name__}: {e}"
        _save_job(Path(private_dir) / "research" / f"{job_id}.json", job)
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
        _save_job(Path(private_dir) / "research" / f"{job_id}.json", job)
        return job

    try:
        spotcheck = spotcheck_fn(proposal)
    except Exception as e:
        job["state"] = "failed"
        job["error"] = str(e)
        _save_job(Path(private_dir) / "research" / f"{job_id}.json", job)
        return job

    job["state"] = "proposed"
    job["proposal"] = proposal
    job["spotcheck"] = spotcheck
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
            with urllib.request.urlopen(req) as response:
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
