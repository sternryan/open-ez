import os
import json
import re
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable, Optional

from hangar.records import ROLES, Record
from core.sources import parse_citation, check_citation, load_registry

class CouncilUnavailable(RuntimeError):
    pass

@dataclass
class CouncilReply:
    positions: list[dict]
    reply_text: str
    unknowns: list[str]
    error: Optional[str] = None

def backbone(rec: Record) -> dict:
    cites_set = set()
    
    def add_cite(s: Any):
        if isinstance(s, str):
            try:
                cid, page = parse_citation(s)
                cites_set.add(f"{cid}:p{page}")
            except (ValueError, AttributeError):
                pass

    if hasattr(rec, 'book_choice') and isinstance(rec.book_choice, dict):
        add_cite(rec.book_choice.get("cite"))
    elif hasattr(rec, 'book_choice') and hasattr(rec.book_choice, 'cite'):
        add_cite(rec.book_choice.cite)
    
    if hasattr(rec, 'options'):
        for opt in rec.options:
            if isinstance(opt, dict):
                for fact in opt.get("facts", []):
                    if isinstance(fact, dict):
                        add_cite(fact.get("cite"))

    sorted_cites = sorted(list(cites_set))
    registry = load_registry()
    sources = {}
    for c in sorted_cites:
        cid = c.split(":")[0]
        if cid in registry:
            sources[cid] = registry[cid]["title"]

    res = {
        "record": {
            "id": rec.id,
            "title": rec.title,
            "question": rec.question,
            "status": rec.status,
        },
        "book_choice": rec.book_choice,
        "options": rec.options,
        "mission_scores": rec.mission_score,
        "cites": sorted_cites,
        "sources": sources,
        "axes": rec.axes if hasattr(rec, 'axes') and isinstance(rec.axes, list) else []
    }
    
    if hasattr(rec, 'coupled_with'):
        res["coupled_with"] = rec.coupled_with
    if hasattr(rec, 'unknowns'):
        res["unknowns"] = rec.unknowns
        
    return res

def _confidence(conf: Any) -> str:
    """The enum, or a number in [0, 1] mapped to it (>= 0.75 high, >= 0.45 medium); anything else is low."""
    if conf in ("low", "medium", "high"):
        return conf
    if isinstance(conf, (int, float)) and not isinstance(conf, bool) and 0 <= conf <= 1:
        return "high" if conf >= 0.75 else "medium" if conf >= 0.45 else "low"
    return "low"


SYSTEM_PROMPT = (
    "JSON schema: positions[role,picks,confidence,reasoning,citations,judgment], reply_text, unknowns. "
    "Give exactly one position for EACH of the five roles: propulsion, structures, fuel-systems, aero-flight-test, historian. "
    "confidence is the string low, medium or high. judgment is a boolean: true when the reasoning is opinion "
    "rather than facts from the pack. A role with no pick on an axis gives picks {} and says why in reasoning. "
    "The pack contains axes ([{id, options}]). Each position provides picks as {axis_id: option_id} "
    "for the axes it has a view on. Use only axis ids and option ids from the pack; "
    "never recommend a dropped or unavailable option. "
    "Citation format: <id>:p<page>. "
    "Behaviors: cite only from the pack, say unknown rather than estimate, "
    "disagree out loud and keep dissent, name couplings, answer against the mission scores. "
    "The roadmap trust standard (material tests, outside review, flight test) still has to clear the paper case."
)

def ask(rec: Record, message: str, history: list[dict], post: Optional[Callable[[dict], dict]] = None, timeout_s: int = 120) -> CouncilReply:
    try:
        injected = post is not None
        
        if post is None:
            url = os.environ.get("HANGAR_COUNCIL_URL")
            model_env = os.environ.get("HANGAR_COUNCIL_MODEL")
            if not url or not model_env:
                raise CouncilUnavailable("Missing environment variables")
            
            key = os.environ.get("HANGAR_COUNCIL_KEY")
            
            def default_post(payload: dict) -> dict:
                data = json.dumps(payload).encode("utf-8")
                headers = {"Content-Type": "application/json"}
                if key:
                    headers["Authorization"] = f"Bearer {key}"
                
                req = urllib.request.Request(
                    f"{url.rstrip('/')}/chat/completions",
                    data=data,
                    headers=headers,
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=timeout_s) as response:
                    return json.loads(response.read().decode("utf-8"))
            post = default_post

        model_name = "council" if injected else os.environ.get("HANGAR_COUNCIL_MODEL", "council")

        clean_history = []
        for h in history:
            if isinstance(h, dict) and h.get("role") in {"user", "assistant"} and isinstance(h.get("content"), str):
                clean_history.append(h)

        payload = {
            "model": model_name,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                *clean_history,
                {"role": "user", "content": f"{message}\n{json.dumps(backbone(rec))}"}
            ]
        }

        resp = post(payload)
        if not resp or "choices" not in resp or not resp["choices"]:
            return CouncilReply([], "", [], error="council reply was not valid JSON")
            
        content = resp["choices"][0]["message"]["content"]
        if not isinstance(content, str):
            return CouncilReply([], "", [], error="council reply was not valid JSON")

        json_match = re.search(r"```(?:json|JSON)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
        else:
            json_match_bare = re.search(r"(\{.*\})", content, re.DOTALL)
            if json_match_bare:
                content = json_match_bare.group(1)

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return CouncilReply([], "", [], error="council reply was not valid JSON")

        if not isinstance(data, dict):
            return CouncilReply([], "", [], error="council reply was not valid JSON")

        valid_positions = []
        backbone_data = backbone(rec)
        backbone_cites = set(backbone_data["cites"])
        
        # axis id -> option ids a position may pick (declared in the axis, not dropped or unavailable)
        kinds = {o.get("id"): o.get("kind") for o in (rec.options if isinstance(rec.options, list) else []) if isinstance(o, dict)}
        valid_axis_map = {}
        for ax in backbone_data.get("axes", []):
            if isinstance(ax, dict) and isinstance(ax.get("id"), str) and isinstance(ax.get("options"), list):
                valid_axis_map[ax["id"]] = {
                    o for o in ax["options"] if isinstance(o, str) and kinds.get(o) not in ("dropped", "unavailable")
                }

        positions_raw = data.get("positions")
        if not isinstance(positions_raw, list):
            positions_raw = []

        for p in positions_raw:
            if not isinstance(p, dict):
                continue
            
            role = p.get("role")
            if not isinstance(role, str) or role not in ROLES:
                continue
            
            # Validate picks
            picks_raw = p.get("picks")
            if not isinstance(picks_raw, dict):
                picks_raw = {}
            
            new_picks = {}
            for ax_id, opt_id in picks_raw.items():
                if not isinstance(ax_id, str) or not isinstance(opt_id, str):
                    continue
                if ax_id in valid_axis_map and opt_id in valid_axis_map[ax_id]:
                    new_picks[ax_id] = opt_id
            
            # A position with no valid pick is kept as comment-only advice (a concern or a dissent);
            # invalid picks are dropped one by one above.
            p["picks"] = new_picks

            if not isinstance(p.get("reasoning"), str):
                continue

            p["confidence"] = _confidence(p.get("confidence"))

            orig_cites = p.get("citations")
            kept_cites = []
            
            if isinstance(orig_cites, list):
                for c in orig_cites:
                    if isinstance(c, str):
                        try:
                            cid, page = parse_citation(c)
                            norm = f"{cid}:p{page}"
                            if norm in backbone_cites:
                                kept_cites.append(norm)
                        except (ValueError, AttributeError, TypeError):
                            pass
            
            p["citations"] = kept_cites
            
            n_given = len(orig_cites) if isinstance(orig_cites, list) else 0
            is_uncited = len(kept_cites) == 0 or len(kept_cites) != n_given

            raw_judgment = p.get("judgment", False)
            reasoning = p["reasoning"]
            if isinstance(raw_judgment, str):
                # Some models put their opinion sentence here instead of a flag: keep the words, visibly.
                judgment = False
                if raw_judgment.strip():
                    reasoning = f"{reasoning} Judgment: {raw_judgment.strip()}"
                    judgment = True
            else:
                judgment = raw_judgment is True
            
            if is_uncited:
                judgment = True
                if not reasoning:
                    reasoning = "(uncited)"
                elif not reasoning.endswith("(uncited)"):
                    reasoning = f"{reasoning} (uncited)"
                p["reasoning"] = reasoning
            
            p["judgment"] = judgment
            valid_positions.append(p)

        reply_text = data.get("reply_text", "")
        if not isinstance(reply_text, str):
            reply_text = ""
            
        unknowns_raw = data.get("unknowns", [])
        if not isinstance(unknowns_raw, list):
            unknowns_raw = []
        
        final_unknowns = []
        for u in unknowns_raw:
            if isinstance(u, str):
                final_unknowns.append(u)
            elif isinstance(u, dict) and isinstance(u.get("text"), str):
                final_unknowns.append(u["text"])

        return CouncilReply(
            positions=valid_positions,
            reply_text=reply_text,
            unknowns=final_unknowns,
            error=None
        )

    except CouncilUnavailable:
        raise
    except Exception as e:
        return CouncilReply([], "", [], error=f"council call failed: {type(e).__name__}")
