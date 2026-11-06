"""Tools Claude can call. Each handler is plain Python over session state;
all decisions go through engines.py / validator.py (no LLM here).

Session state keys used here are created in main._new_session().
"""
from app import data_store, engines, validator

SCREEN_IDS = sorted({c["how_to_verify"].split(":", 1)[1]
                     for c in data_store.channels().values()
                     if c["how_to_verify"].startswith("screenshot:")})
CHANNEL_IDS = sorted(data_store.channels())


# ----------------------------------------------------------- derived state

def active_channels(session: dict) -> set[str]:
    """Channels backed by something the survivor said or showed (interview/screenshot).
    Inference-only guesses are 'possible explanations to check', not findings, so they
    never count toward exposure, simulation or the caseworker summary."""
    return {cid for cid, f in session["findings"].items() if f["basis"] != "inference"}


def possible_channels(session: dict) -> set[str]:
    return {cid for cid, f in session["findings"].items() if f["basis"] == "inference"}


def split_findings(session: dict) -> tuple[list[dict], list[dict]]:
    """(findings, possible explanations to check), both validated, in insertion order."""
    checked, _ = validator.validate_findings(list(session["findings"].values()))
    return ([f for f in checked if f["basis"] != "inference"],
            [f for f in checked if f["basis"] == "inference"])


def screen_for(channel_id: str) -> str | None:
    how = data_store.channels()[channel_id]["how_to_verify"]
    return how.split(":", 1)[1] if how.startswith("screenshot:") else None


def platforms(session: dict) -> set[str] | None:
    return set(session["platforms"]) if session["platforms"] else None


def run_hypothesis(session: dict) -> dict:
    observed = {o["knowledge"] for o in session["observations"]}
    result = engines.hypothesize(observed, session["ruled_out"], platforms(session))
    session["last_hypothesis"] = result
    return result


# ---------------------------------------------------------------- handlers

def set_safety_mode(session: dict, mode: str) -> dict:
    if mode not in ("covert", "lockdown"):
        return {"error": "mode must be 'covert' or 'lockdown'"}
    session["safety_mode"] = mode
    if session["plan"]:  # re-validate an existing plan under the new mode
        _revalidate_plan(session)
    return {"ok": True, "safety_mode": mode,
            "rule": ("Only steps the other person can't notice will be shown as actionable."
                     if mode == "covert" else "Full plan allowed, still in dependency order.")}


def set_context(session: dict, platforms: list[str] | None = None,
                region: str | None = None) -> dict:
    out: dict = {"ok": True}
    if platforms is not None:
        bad = [p for p in platforms if p not in engines.PLATFORMS]
        if bad:
            return {"error": f"unknown platforms {bad}; use {list(engines.PLATFORMS)}"}
        session["platforms"] = sorted(set(platforms))
        out["platforms"] = session["platforms"]
    if region is not None:
        session["region"] = validator.normalize_region(region)
        out["region"] = session["region"]
    return out


def record_observation(session: dict, knowledge: str, evidence: str = "") -> dict:
    k = knowledge.strip().lower().replace(" ", "_")
    if any(o["knowledge"] == k for o in session["observations"]):
        return {"ok": True, "already_recorded": k}
    # Keep the survivor's words short; nothing is persisted.
    session["observations"].append({"knowledge": k, "evidence": evidence[:200]})
    known = k in engines.observables()
    return {"ok": True, "knowledge": k, "in_vocabulary": known,
            **({} if known else {"note": "Not something any checked channel reveals; "
                                         "hypothesize will list it as unexplained."})}


def record_finding(session: dict, channel_id: str, evidence_level: str, basis: str,
                   status: str = "active", note: str = "") -> dict:
    if channel_id not in data_store.channels():
        return {"error": f"unknown channel {channel_id!r}", "valid_channels": CHANNEL_IDS}
    if status == "ruled_out":
        session["findings"].pop(channel_id, None)
        session["ruled_out"].add(channel_id)
        return {"ok": True, "ruled_out": channel_id}
    session["ruled_out"].discard(channel_id)
    finding = {
        "channel_id": channel_id,
        "evidence_level": evidence_level,
        "basis": basis,
        # Decided by code: true only if the user clicked "Yes, that's right" on a
        # reading of the screen that verifies this channel (see main.py). Never Claude.
        "screenshot_confirmed": (basis == "screenshot"
                                 and screen_for(channel_id) in session["confirmed_screens"]),
        "note": note[:200],
    }
    [checked], flags = validator.validate_findings([finding])
    session["findings"][channel_id] = {k: checked[k] for k in finding}
    return {"ok": True, "recorded_level": checked["evidence_level"], "flags": flags}


def hypothesize(session: dict) -> dict:
    return run_hypothesis(session)


def request_screenshot(session: dict, screen_id: str, instructions: str) -> dict:
    if screen_id not in SCREEN_IDS:
        return {"error": f"unknown screen_id {screen_id!r}", "valid_screen_ids": SCREEN_IDS}
    session["pending_screenshot"] = {"screen_id": screen_id, "instructions": instructions[:500]}
    from app.vision import SCREEN_HINTS  # local import: vision imports agent
    return {"ok": True, "upload_box_shown": True,
            "where_to_find": SCREEN_HINTS.get(screen_id, ""),
            "use_this_path": "Describe where to find the screen using where_to_find only.",
            "remember": "Tell them screenshots saved on a phone that may be compromised can "
                        "sync through shared iCloud Photos; photographing the screen with a "
                        "safe device is safer."}


def get_fix(session: dict, fix_id: str) -> dict:
    return validator.lookup_fix(fix_id)


def find_fixes(session: dict, channel_id: str) -> dict:
    if channel_id not in data_store.channels():
        return {"error": f"unknown channel {channel_id!r}", "valid_channels": CHANNEL_IDS}
    hits = [{"id": f["id"], "title": f["title"], "may_notify_abuser": f["may_notify_abuser"],
             "prerequisites": f["prerequisites"]}
            for f in data_store.fixes().values() if channel_id in f["closes"]]
    return {"channel_id": channel_id, "fixes": hits}


def simulate_plan(session: dict, fix_ids: list[str]) -> dict:
    return engines.simulate_plan(active_channels(session), fix_ids, platforms(session))


def get_resources(session: dict, region: str) -> dict:
    session["region"] = validator.normalize_region(region)
    out = validator.resources_for(region)
    rights = validator.rights_for(region)
    out["rights"] = [{k: r[k] for k in ("id", "summary", "source", "scope") if k in r}
                     for r in rights]
    out["rights_rule"] = ("Official information, not legal advice. Restate only what is "
                          "written here, in plain words; never predict outcomes or cite "
                          "laws not listed. Suggest an advocate or a free legal helpline "
                          "for what applies to them.")
    return out


def _revalidate_plan(session: dict) -> dict:
    req = session["plan_request"]
    result = validator.validate_plan(
        req["fix_ids"], session["safety_mode"], active_channels(session),
        req["resource_ids"], session["region"], session["last_hypothesis"],
        platforms(session))
    if result["ok"]:
        session["plan"] = result
    return result


def propose_plan(session: dict, fix_ids: list[str], resource_ids: list[str] | None = None,
                 notes: str = "") -> dict:
    session["plan_request"] = {"fix_ids": list(fix_ids), "resource_ids": list(resource_ids or [])}
    if session["last_hypothesis"] is None and session["observations"]:
        run_hypothesis(session)
    result = _revalidate_plan(session)
    if not result["ok"]:
        session["plan_request"] = None
        return {**result, "instruction": "Fix the rejected IDs (use closest_matches) and retry."}
    # Tell Claude what the survivor will actually see, so its reply matches the panel.
    return {
        "ok": True,
        "shown_as_actionable": [s["id"] for s in result["actionable"]],
        "shown_as_discuss_with_advocate_first": [s["id"] for s in result["discuss_first"]],
        "added_prerequisites": result["added_prerequisites"],
        "notices": result["notices"],
        "unexplained_notice": result["unexplained_notice"],
        "resources_shown": [r["id"] for r in result["resources"]],
        "still_exposed_after_actionable_steps":
            (result["simulation"] or {}).get("still_exposed", []),
    }


HANDLERS = {
    "set_safety_mode": set_safety_mode,
    "set_context": set_context,
    "record_observation": record_observation,
    "record_finding": record_finding,
    "hypothesize": hypothesize,
    "request_screenshot": request_screenshot,
    "get_fix": get_fix,
    "find_fixes": find_fixes,
    "simulate_plan": simulate_plan,
    "get_resources": get_resources,
    "propose_plan": propose_plan,
}


# ------------------------------------------------------------ tool schemas

def _obj(props: dict, required: list[str]) -> dict:
    return {"type": "object", "properties": props, "required": required,
            "additionalProperties": False}


TOOLS = [
    {"name": "set_safety_mode",
     "description": "Record the answer to the first question. 'covert' if they still live "
                    "with or are in regular contact with the person, or are unsure; "
                    "'lockdown' if they have left and are not in regular contact.",
     "input_schema": _obj({"mode": {"type": "string", "enum": ["covert", "lockdown"]}},
                          ["mode"])},
    {"name": "set_context",
     "description": "Record which platforms they use (apple = iPhone/iPad/Mac/iCloud, "
                    "google = Android or Google account, whatsapp) and their country "
                    "(optionally US state, e.g. 'US-NY'). Never ask for more location detail.",
     "input_schema": _obj({"platforms": {"type": "array",
                                         "items": {"type": "string",
                                                   "enum": list(engines.PLATFORMS)}},
                           "region": {"type": "string"}}, [])},
    {"name": "record_observation",
     "description": "Record something the other person seems to know. Use one term from "
                    "the observation vocabulary in the system prompt when it fits; otherwise "
                    "a short snake_case description (it will be reported as unexplained). "
                    "One call per distinct thing.",
     "input_schema": _obj({"knowledge": {"type": "string"},
                           "evidence": {"type": "string",
                                        "description": "Brief paraphrase of what they said. "
                                                       "No names or addresses."}},
                          ["knowledge"])},
    {"name": "record_finding",
     "description": "Add or update a possible access channel. evidence_level: 'reported' "
                    "(they told you), 'plausible' (fits the facts), 'verified' (only after "
                    "they confirmed a screenshot reading in the app). basis 'inference' means "
                    "only you suspect it; it is shown as a possible explanation to check, not "
                    "as a finding, and doesn't count toward exposure. Use status "
                    "'ruled_out' when evidence shows a channel is NOT active.",
     "input_schema": _obj({"channel_id": {"type": "string", "enum": CHANNEL_IDS},
                           "evidence_level": {"type": "string",
                                              "enum": list(validator.EVIDENCE_LEVELS)},
                           "basis": {"type": "string",
                                     "enum": ["interview", "screenshot", "inference"]},
                           "status": {"type": "string", "enum": ["active", "ruled_out"]},
                           "note": {"type": "string"}},
                          ["channel_id", "evidence_level", "basis"])},
    {"name": "hypothesize",
     "description": "Run the deterministic engine over recorded observations, ruled-out "
                    "channels and platforms. Returns ranked candidate channels, best_check "
                    "(the screenshot that best distinguishes them), interview_checks, and "
                    "unexplained observations. Call after recording observations.",
     "input_schema": _obj({}, [])},
    {"name": "request_screenshot",
     "description": "Show an upload box for one specific screen. Use the screen_id from "
                    "best_check when possible. Instructions should say where to find the "
                    "screen in plain words.",
     "input_schema": _obj({"screen_id": {"type": "string", "enum": SCREEN_IDS},
                           "instructions": {"type": "string"}},
                          ["screen_id", "instructions"])},
    {"name": "get_fix",
     "description": "Get one vetted playbook fix by id (steps, risks, source). Unknown ids "
                    "return closest matches. Never describe steps that didn't come from here.",
     "input_schema": _obj({"fix_id": {"type": "string"}}, ["fix_id"])},
    {"name": "find_fixes",
     "description": "List playbook fixes that close a given channel.",
     "input_schema": _obj({"channel_id": {"type": "string", "enum": CHANNEL_IDS}},
                          ["channel_id"])},
    {"name": "simulate_plan",
     "description": "Apply fix ids in order to the current findings. Returns "
                    "remaining_channels, still_exposed, order_problems, unknown_fixes. "
                    "Resolve problems before propose_plan.",
     "input_schema": _obj({"fix_ids": {"type": "array", "items": {"type": "string"}}},
                          ["fix_ids"])},
    {"name": "get_resources",
     "description": "Vetted support resources for a country (and optional US state), plus "
                    "short official facts about their legal rights (information, not legal "
                    "advice). Only mention organizations, contacts and rights returned here.",
     "input_schema": _obj({"region": {"type": "string"}}, ["region"])},
    {"name": "propose_plan",
     "description": "Submit the plan. The validator checks ids, applies safety mode, fixes "
                    "ordering and adds required steps, then shows it in the side panel. The "
                    "result tells you exactly what the survivor sees; describe that, not "
                    "your original list.",
     "input_schema": _obj({"fix_ids": {"type": "array", "items": {"type": "string"}},
                           "resource_ids": {"type": "array", "items": {"type": "string"}},
                           "notes": {"type": "string"}},
                          ["fix_ids"])},
]


def catalog_text() -> str:
    """Static reference appended to the system prompt (stable → cacheable)."""
    lines = ["OBSERVATION VOCABULARY: " + ", ".join(engines.observables()), "", "CHANNELS:"]
    for c in data_store.channels().values():
        lines.append(f"- {c['id']} [{c['platform']}]: {c['label']}; reveals "
                     f"{', '.join(c['reveals'])}; verify by {c['how_to_verify']}")
    lines += ["", "PLAYBOOK FIXES (id: title — closes; may notify them?):"]
    for f in data_store.fixes().values():
        lines.append(f"- {f['id']}: {f['title']} — closes {', '.join(f['closes']) or 'nothing'}"
                     f"; {'MAY NOTIFY' if f['may_notify_abuser'] else 'not detectable'}")
    lines += ["", "RESOURCE IDS: " + ", ".join(data_store.resources())]
    return "\n".join(lines)
