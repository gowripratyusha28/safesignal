"""Engine trace: a short, content-free record of what the deterministic code
decided on each turn, so the survivor (and a judge) can see 'code deciding'.

Entries hold tool names, IDs, scores and validator decisions only. Never the
survivor's words, Claude's notes, or anything read from a screenshot.
"""
MAX_ENTRIES = 60


def add(session: dict, source: str, text: str) -> None:
    session.setdefault("trace", []).append({"source": source, "text": text})
    del session["trace"][:-MAX_ENTRIES]


def _ids(xs) -> str:
    return ", ".join(xs) if xs else "none"


def for_tool(session: dict, name: str, inp: dict, out: dict) -> None:
    """Summarise one tool call. `inp` may contain survivor-derived text
    (evidence, note); only ids/enums from it are used."""
    if "error" in out:
        add(session, name, f"rejected input: {out['error']}")
        return
    if name == "set_safety_mode":
        add(session, name, f"mode = {out['safety_mode']}. {out['rule']}")
    elif name == "set_context":
        bits = [f"platforms = {_ids(out['platforms'])}" if "platforms" in out else "",
                f"region = {out['region']}" if "region" in out else ""]
        add(session, name, "; ".join(b for b in bits if b))
    elif name == "record_observation":
        if "already_recorded" in out:
            return
        tag = "" if out["in_vocabulary"] else " (outside checked categories → will be unexplained)"
        add(session, name, f"category: {out['knowledge']}{tag}")
    elif name == "record_finding":
        if "ruled_out" in out:
            add(session, name, f"{out['ruled_out']} ruled out")
            return
        line = f"{inp.get('channel_id')} → {out['recorded_level']} (basis: {inp.get('basis')})"
        if out["flags"]:
            line += " — validator: " + "; ".join(f.split(": ", 1)[-1] for f in out["flags"])
        add(session, name, line)
    elif name == "hypothesize":
        cands = out["candidates"][:3]
        ranked = " | ".join(f"{i + 1}. {'+'.join(c['channels'])} ({c['score']})"
                            for i, c in enumerate(cands))
        bc = out["best_check"]
        line = f"ranked {len(out['candidates'])} explanations: {ranked or 'none'}"
        if bc:
            line += f". Best check: screenshot of {bc['screen_id']}"
        if out["unexplained"]:
            line += f". UNEXPLAINED: {_ids(out['unexplained'])} → expert referral required"
        add(session, name, line)
    elif name == "request_screenshot":
        add(session, name, f"asked for screen {inp.get('screen_id')}")
    elif name == "get_fix":
        if out.get("found"):
            add(session, name, f"{inp.get('fix_id')} → found in playbook")
        else:
            add(session, name, f"'{inp.get('fix_id')}' is NOT in the playbook → rejected; "
                               f"closest: {_ids(out['closest_matches'])}")
    elif name == "find_fixes":
        add(session, name, f"{out['channel_id']} → {_ids(f['id'] for f in out['fixes'])}")
    elif name == "simulate_plan":
        line = (f"[{_ids(inp.get('fix_ids', []))}] → remaining: {_ids(out['remaining_channels'])}"
                f"; still exposed: {_ids(out['still_exposed'])}")
        if out["order_problems"]:
            line += "; PROBLEMS: " + " / ".join(out["order_problems"])
        if out["unknown_fixes"]:
            line += f"; unknown fix ids: {_ids(out['unknown_fixes'])}"
        add(session, name, line)
    elif name == "get_resources":
        n = len(out["resources"])
        nr = len(out.get("rights", []))
        add(session, name, f"{out['region'] or 'no region'} → {n} vetted entries, "
                           f"{nr} rights facts (official sources)"
                           + ("" if out["found"] else " (nothing vetted; no names given)"))
    elif name == "propose_plan":
        if not out["ok"]:
            add(session, name, "validator REJECTED: " + "; ".join(
                f"{r['kind']} '{r['id']}' unknown (closest: {_ids(r['closest_matches'])})"
                for r in out["rejected"]))
            return
        parts = [f"actionable: {_ids(out['shown_as_actionable'])}"]
        if out["shown_as_discuss_with_advocate_first"]:
            parts.append("moved to advocate-first (may notify): "
                         f"{_ids(out['shown_as_discuss_with_advocate_first'])}")
        if out["added_prerequisites"]:
            parts.append(f"added missing prerequisites: {_ids(out['added_prerequisites'])}")
        if any("reordered" in n for n in out["notices"]):
            parts.append("reordered to respect dependencies")
        if out["unexplained_notice"]:
            parts.append("unexplained → notice + expert resource forced")
        parts.append(f"still exposed after safe steps: "
                     f"{_ids(out['still_exposed_after_actionable_steps'])}")
        add(session, "validator", "; ".join(parts))
