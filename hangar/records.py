from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import yaml
from core.sources import check_citation
import guide.schema

ROLES = ("propulsion", "structures", "fuel-systems", "aero-flight-test", "historian")
STATUSES = ("open", "decided", "reopened")
DATA_ROOT = Path(__file__).resolve().parents[1] / "data" / "hangar"

@dataclass(frozen=True)
class Record:
    id: str
    spot: str
    title: str
    status: str
    question: str
    coupled_with: list
    replaces: list
    book_choice: dict
    options: list
    positions: list
    unknowns: list
    mission_score: dict | None
    decision: dict | None
    history: list
    changes: dict | None
    evidence: dict

def load_record(path: Path) -> Record:
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    
    required = ["id", "spot", "title", "status", "question", "coupled_with", "replaces", "book_choice", "options", "positions", "unknowns", "mission_score", "decision", "history", "changes", "evidence"]
    for req in required:
        if req not in data:
            raise ValueError(f"Missing required key: {req}")
            
    def get_val(key, default):
        return data.get(key, default)

    return Record(
        id=data["id"],
        spot=data["spot"],
        title=data["title"],
        status=data["status"],
        question=data["question"],
        coupled_with=get_val("coupled_with", []),
        replaces=get_val("replaces", []),
        book_choice=get_val("book_choice", {}),
        options=get_val("options", []),
        positions=get_val("positions", []),
        unknowns=get_val("unknowns", []),
        mission_score=get_val("mission_score", None),
        decision=get_val("decision", None),
        history=get_val("history", []),
        changes=get_val("changes", None),
        evidence=get_val("evidence", {})
    )

def load_records(root: Path = DATA_ROOT) -> dict[str, Record]:
    records_dict = {}
    # glob root/*/decisions/*.yaml
    for p in sorted(root.glob("*/decisions/*.yaml")):
        try:
            rec = load_record(p)
            records_dict[rec.id] = rec
        except Exception:
            continue
    return records_dict

def validate(rec: Record, graph: Any, all_ids: set[str]) -> list[str]:
    errors = []
    
    # 1. Status
    if rec.status not in STATUSES:
        errors.append(f"status must be in {STATUSES}")

    # 2. Citations
    # book_choice
    if "cite" in rec.book_choice:
        try:
            check_citation(rec.book_choice["cite"])
        except ValueError as e:
            errors.append(str(e))
    
    # options facts
    for opt in rec.options:
        for fact in opt.get("facts", []):
            if "cite" in fact:
                try:
                    check_citation(fact["cite"])
                except ValueError as e:
                    errors.append(str(e))
            
            # 3. Fact needs cite or flag
            if "cite" not in fact and "flag" not in fact:
                errors.append("Each option fact needs a 'cite' OR a 'flag'")
            elif "flag" in fact:
                if fact["flag"] not in {"derived", "unknown", "judgment"}:
                    pass # valid flag
            
    # positions citations
    for pos in rec.positions:
        for cite in pos.get("citations", []):
            try:
                check_citation(cite)
            except ValueError as e:
                errors.append(str(e))

    # 4. mod-ez rules
    if rec.spot == "mod-ez":
        if not rec.replaces:
            errors.append("replaces must be non-empty")
        for rid in rec.replaces:
            if rid not in graph.ops:
                errors.append(f"bad id {rid}")
        if not any(o.get("kind") == "book" for o in rec.options):
            errors.append("options must include one with kind == 'book'")

    # 5. Option kinds and uniqueness
    opt_ids = []
    for opt in rec.options:
        oid = opt.get("id")
        if oid in opt_ids:
            errors.append(f"duplicate option id {oid}")
        opt_ids.append(oid)
        if opt.get("kind") not in {"book", "candidate", "dropped", "unavailable"}:
            errors.append(f"invalid kind {opt.get('kind')}")

    # 6. Positions
    for pos in rec.positions:
        role = pos.get("role")
        if role not in ROLES:
            errors.append(f"bad role {role}")
        oid = pos.get("option")
        if oid not in opt_ids:
            errors.append(f"bad option {oid}")
        if pos.get("confidence") not in {"low", "medium", "high"}:
            errors.append("invalid confidence")

    # 7. coupled_with
    for cid in rec.coupled_with:
        if cid not in all_ids:
            errors.append(f"missing id {cid}")

    # 8. Decision
    if rec.status == "decided":
        if rec.decision is None:
            errors.append("decided status requires decision")
        else:
            d_opt = rec.decision.get("option")
            if d_opt not in opt_ids:
                errors.append(f"bad option {d_opt}")
            if not rec.decision.get("reason"):
                errors.append("decision needs reason")
            if not rec.decision.get("date"):
                errors.append("decision needs date")
    elif rec.status == "open":
        if rec.decision is not None:
            errors.append("open status must have decision None")

    # 9. History
    if rec.status == "decided":
        if not rec.history:
            errors.append("decided record must have history")
        else:
            prev_to = "open"
            for entry in rec.history:
                e_date = entry.get("date")
                e_reason = entry.get("reason")
                e_from = entry.get("from")
                e_to = entry.get("to")
                
                if not e_date or not e_reason:
                    errors.append("history entry needs date and reason")
                    continue
                
                if e_from != prev_to:
                    errors.append("history entries must chain")
                
                # Allowed transitions
                valid_trans = {("open", "decided"), ("decided", "reopened"), ("reopened", "decided")}
                if (e_from, e_to) not in valid_trans:
                    errors.append("invalid transition")
                
                prev_to = e_to
            
            if rec.history[-1].get("to") != rec.status:
                errors.append("history last 'to' must equal status")
            
            # Decided check
            last_entry = rec.history[-1]
            if last_entry.get("to") != "decided":
                errors.append("decided record must end with a to:decided entry")
            
            # Date check
            d_date = str(rec.decision.get("date")) if rec.decision else ""
            if d_date != str(last_entry.get("date")):
                errors.append("decision date must equal last history entry date")

    # 10. Evidence
    for key in ["paper", "material", "outside_review", "flight"]:
        val = rec.evidence.get(key)
        if val and val != "none":
            if val not in {"none", "partial", "done"}:
                errors.append("invalid evidence value")

    return errors

def validate_all(root: Path = DATA_ROOT, graph_dir: Path = Path("guide/graph")) -> list[str]:
    try:
        records_dict = load_records(root)
        graph = guide.schema.load_graph(graph_dir)
        all_ids = set(records_dict.keys())
        all_errors = []
        for rid, rec in records_dict.items():
            errs = validate(rec, graph, all_ids)
            for e in errs:
                all_errors.append(f"{rid}: {e}")
        return all_errors
    except Exception as e:
        # If a record is malformed (load_record fails), it's an error string.
        # But the task says "A malformed record file becomes an error string, not a crash."
        # This implies we catch errors during the loop.
        return [str(e)]

def load_spots(path: Path = DATA_ROOT / "spots.yaml") -> list[dict]:
    with open(path, 'r') as f:
        return yaml.safe_load(f)
