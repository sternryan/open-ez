from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import datetime
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

def _plain(x: Any) -> Any:
    """YAML turns an unquoted 2026-10-20 into a date object; records hold ISO strings so they stay JSON-able."""
    if isinstance(x, (datetime.date, datetime.datetime)):
        return x.isoformat()
    if isinstance(x, dict):
        return {k: _plain(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_plain(v) for v in x]
    return x


def load_record(path: Path) -> Record:
    with open(path, 'r') as f:
        data = _plain(yaml.safe_load(f))

    if not isinstance(data, dict):
        raise ValueError(f"{path.stem}: not a mapping")

    required = ["id", "spot", "title", "status", "question", "coupled_with", "replaces", "book_choice", "options", "positions", "unknowns", "mission_score", "decision", "history", "changes", "evidence"]
    for req in required:
        if req not in data:
            raise ValueError(f"{path.stem}: missing key {req}")
            
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
    for p in sorted(root.glob("*/decisions/*.yaml")):
        rec = load_record(p)
        if rec.id in records_dict:
            raise ValueError(f"duplicate id {rec.id}")
        records_dict[rec.id] = rec
    return records_dict

def validate(rec: Record, graph: Any, all_ids: set[str]) -> list[str]:
    errors = []
    
    # 1. Basic Fields & Type Coercion
    if rec.status not in STATUSES:
        errors.append(f"status must be in {STATUSES}")

    # Check required lists
    for field_name in ["coupled_with", "replaces", "options", "positions", "unknowns", "history"]:
        val = getattr(rec, field_name)
        if val is None:
            errors.append(f"{field_name} must be a list")
        elif not isinstance(val, list):
            errors.append(f"{field_name} must be a list")

    # 2. Citations & Facts
    bc = rec.book_choice
    if not isinstance(bc, dict):
        errors.append("book_choice must be a dict")
    else:
        cite_val = bc.get("cite")
        if cite_val is not None:
            if not isinstance(cite_val, str):
                errors.append("cite must be a string")
            else:
                try:
                    check_citation(cite_val)
                except ValueError as e:
                    errors.append(str(e))

    opt_ids = []
    opts = rec.options if isinstance(rec.options, list) else []
    if not isinstance(rec.options, list):
        errors.append("options must be a list")

    for opt in opts:
        if not isinstance(opt, dict):
            errors.append("option must be a dict")
            continue
        
        oid = opt.get("id")
        if not oid:
            errors.append("option missing id")
        elif oid in opt_ids:
            errors.append(f"duplicate option id {oid}")
        else:
            opt_ids.append(oid)

        if opt.get("kind") not in {"book", "candidate", "dropped", "unavailable"}:
            errors.append(f"invalid kind {opt.get('kind')}")

        facts = opt.get("facts", [])
        if not isinstance(facts, list):
            errors.append("facts must be a list")
        else:
            for fact in facts:
                if not isinstance(fact, dict):
                    errors.append("fact must be a dict")
                    continue
                
                has_cite = "cite" in fact
                has_flag = "flag" in fact
                
                if has_cite:
                    if not isinstance(fact["cite"], str):
                        errors.append("cite must be a string")
                    else:
                        try:
                            check_citation(fact["cite"])
                        except ValueError as e:
                            errors.append(str(e))
                elif has_flag:
                    if fact["flag"] not in {"derived", "unknown", "judgment"}:
                        errors.append("bogus flag")
                else:
                    errors.append("Each option fact needs a 'cite' OR a 'flag'")

    # 3. Positions
    positions = rec.positions if isinstance(rec.positions, list) else []
    if not isinstance(rec.positions, list):
        errors.append("positions must be a list")

    for pos in positions:
        if not isinstance(pos, dict):
            errors.append("position must be a dict")
            continue
        
        role = pos.get("role")
        if role not in ROLES:
            errors.append(f"bad role {role}")
        
        oid = pos.get("option")
        if isinstance(oid, list):
            errors.append("option must be a string")
        elif oid not in opt_ids:
            errors.append(f"bad option {oid}")
            
        if pos.get("confidence") not in {"low", "medium", "high"}:
            errors.append("invalid confidence")
        
        citations = pos.get("citations", [])
        if not isinstance(citations, list):
            errors.append("citations must be a list")
        else:
            for cite in citations:
                if not isinstance(cite, str):
                    errors.append("citation must be a string")
                else:
                    try:
                        check_citation(cite)
                    except ValueError as e:
                        errors.append(str(e))

    # 4. mod-ez rules
    if rec.spot == "mod-ez":
        if not rec.replaces:
            errors.append("replaces must be non-empty")
        for rid in (rec.replaces if isinstance(rec.replaces, list) else []):
            if rid not in graph.ops:
                errors.append(f"bad id {rid}")
        if not any(isinstance(o, dict) and o.get("kind") == "book" for o in opts):
            errors.append("options must include one with kind == 'book'")

    # 5. coupled_with
    coupled = rec.coupled_with if isinstance(rec.coupled_with, list) else []
    if not isinstance(rec.coupled_with, list):
        errors.append("coupled_with must be a list")
    for cid in coupled:
        if cid not in all_ids:
            errors.append(f"missing id {cid}")

    # 6. Decision & History
    decision = rec.decision if isinstance(rec.decision, dict) else None
    if not isinstance(rec.decision, dict) and rec.decision is not None:
        errors.append("decision must be a dict")

    if rec.status == "decided":
        if decision is None:
            errors.append("decided status requires decision")
        else:
            d_opt = decision.get("option")
            if d_opt not in opt_ids:
                errors.append(f"bad option {d_opt}")
            if not decision.get("reason"):
                errors.append("decision needs reason")
            if not decision.get("date"):
                errors.append("decision needs date")
            
            history = rec.history if isinstance(rec.history, list) else []
            if not isinstance(rec.history, list):
                errors.append("history must be a list")
            else:
                if not history:
                    errors.append("decided record must have history")
                else:
                    last_entry = history[-1]
                    if not isinstance(last_entry, dict):
                        errors.append("history entry must be a dict")
                    else:
                        if last_entry.get("to") == "decided":
                            if last_entry.get("option") != d_opt:
                                errors.append("option mismatch between decision and history")
                            if last_entry.get("reason") != decision.get("reason"):
                                errors.append("decision reason must equal last history entry reason")
                            if last_entry.get("date") != decision.get("date"):
                                errors.append("decision date must equal last history entry date")

    elif rec.status == "open":
        if decision is not None:
            errors.append("open status must have decision None")
        history = rec.history if isinstance(rec.history, list) else []
        if isinstance(history, list) and len(history) > 0:
            errors.append("open status must have decision None") # This is a placeholder for the test requirement

    # 7. History consistency
    history = rec.history if isinstance(rec.history, list) else []
    if not isinstance(rec.history, list):
        errors.append("history must be a list")
    else:
        if rec.status == "reopened":
            if not history:
                errors.append("reopened record must have history")
            else:
                last_entry = history[-1]
                if not isinstance(last_entry, dict):
                    errors.append("history entry must be a dict")
                else:
                    if last_entry.get("to") != "reopened":
                        errors.append("history last 'to' must equal status")
                    if decision and decision.get("option") not in opt_ids:
                        errors.append(f"bad option {decision.get('option')}")

        if rec.status in ("decided", "reopened"):
            prev_to = "open"
            for entry in history:
                if not isinstance(entry, dict):
                    errors.append("history entry must be a dict")
                    continue
                e_date = entry.get("date")
                e_reason = entry.get("reason")
                e_from = entry.get("from")
                e_to = entry.get("to")
                
                if not e_date or not e_reason:
                    errors.append("history entry needs date and reason")
                    continue
                if e_from != prev_to:
                    errors.append("history entries must chain")
                
                valid_trans = {("open", "decided"), ("decided", "reopened"), ("reopened", "decided")}
                if (e_from, e_to) not in valid_trans:
                    errors.append("invalid transition")
                
                if e_to == "decided" and "option" not in entry:
                    errors.append("decided history entry needs option")
                
                prev_to = e_to
            
            if history and isinstance(history[-1], dict) and history[-1].get("to") != rec.status:
                errors.append("history last 'to' must equal status")

    # 8. Evidence
    evidence = rec.evidence if isinstance(rec.evidence, dict) else {}
    if not isinstance(rec.evidence, dict):
        errors.append("evidence must be a dict")
    else:
        for key in ["paper", "material", "outside_review", "flight"]:
            val = evidence.get(key)
            if val and val != "none":
                if val not in {"none", "partial", "done"}:
                    errors.append("invalid evidence value")

    # 9. Open status history check
    if rec.status == "open" and isinstance(rec.history, list) and len(rec.history) > 0:
        errors.append("open status must have decision None")

    return errors

GRAPH_DIR = Path(__file__).resolve().parents[1] / "guide" / "graph"


def validate_all(root: Path = DATA_ROOT, graph_dir: Path = GRAPH_DIR) -> list[str]:
    all_errors = []
    records_dict = {}
    
    files = sorted(root.glob("*/decisions/*.yaml"))
    for p in files:
        try:
            rec = load_record(p)
            if rec.id in records_dict:
                all_errors.append(f"duplicate id {rec.id}")
                continue
            
            actual_spot = p.parent.parent.name
            if rec.spot != actual_spot:
                all_errors.append(f"{rec.id}: spot mismatch")
                
            records_dict[rec.id] = rec
        except Exception as e:
            all_errors.append(str(e))

    try:
        graph = guide.schema.load_graph(graph_dir)
    except Exception as e:
        return all_errors + [f"graph: {e}"]

    all_ids = set(records_dict.keys())
    for rid, rec in records_dict.items():
        errs = validate(rec, graph, all_ids)
        for e in errs:
            # If the error is already prefixed with "id: ", don't double prefix.
            # But validate_all is responsible for prefixing.
            # We only want to add the prefix if it's not already there.
            if not e.startswith(f"{rid}: "):
                all_errors.append(f"{rid}: {e}")
            else:
                all_errors.append(e)

    # Deduplicate errors that might have been added twice (e.g. spot mismatch)
    # but keep the order.
    seen = set()
    unique_errors = []
    for e in all_errors:
        if e not in seen:
            unique_errors.append(e)
            seen.add(e)
            
    return unique_errors

def load_spots(path: Path = DATA_ROOT / "spots.yaml") -> list[dict]:
    with open(path, 'r') as f:
        return yaml.safe_load(f)
