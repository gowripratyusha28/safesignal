"""Caseworker summary. Pure function over session state; no LLM.

Contains technical findings only: no conversation, no survivor's words, no
notes written by Claude, no device or person names, no plans beyond step titles.
"""
from datetime import date

from app import data_store, engines, tools, validator

MODE_TEXT = {
    "covert": "Covert (still in contact or unsure): only undetectable steps shown as actionable",
    "lockdown": "Lockdown (has left): full plan in dependency order",
    None: "Not set (treated as covert)",
}

LEVEL_TEXT = {
    "reported": "reported by survivor",
    "plausible": "plausible (fits the facts, not checked)",
    "verified": "verified (survivor confirmed a screenshot reading)",
}


def build_summary(session: dict, today: date | None = None) -> str:
    today = today or date.today()
    findings, _possible = tools.split_findings(session)  # inference-only guesses excluded
    chans = data_store.channels()
    plan = session["plan"]
    vocab = set(engines.observables())
    observed = [o["knowledge"] for o in session["observations"]]
    in_vocab = sorted({o for o in observed if o in vocab})
    out_vocab = len({o for o in observed if o not in vocab})
    unexplained = (session["last_hypothesis"] or {}).get("unexplained", [])

    L = ["SAFESIGNAL CASEWORKER SUMMARY (technical findings only)",
         f"Generated: {today.isoformat()}",
         "Contains no conversation content. Share only through a channel the other person "
         "cannot access.",
         "",
         f"Safety mode: {MODE_TEXT.get(session['safety_mode'], MODE_TEXT[None])}",
         f"Platforms: {', '.join(session['platforms']) or 'not stated'}",
         f"Region: {session['region'] or 'not stated'}",
         "",
         "WHAT THE OTHER PERSON SEEMS TO KNOW (categories)"]
    L += [f"- {o.replace('_', ' ')}" for o in in_vocab] or ["- none recorded"]
    if out_vocab:
        L.append(f"- plus {out_vocab} other observation(s) outside the checked categories")

    L += ["", "FINDINGS (possible access channels)"]
    for f in findings:
        L.append(f"- {f['label']}: {LEVEL_TEXT[f['evidence_level']]}; basis: {f['basis']}")
    if not findings:
        L.append("- none recorded")
    ruled = sorted(session["ruled_out"])
    if ruled:
        L += ["", "CHECKED AND NOT FOUND ACTIVE"]
        L += [f"- {chans[c]['label']}" for c in ruled]

    exposed = sorted(engines.exposed(tools.active_channels(session), tools.platforms(session)))
    L += ["", "MAY BE EXPOSED (if the findings above are active)",
          "- " + (", ".join(e.replace("_", " ") for e in exposed) if exposed else "nothing identified")]

    if unexplained:
        L += ["", f"NOT EXPLAINED BY WHAT WAS CHECKED: {len(unexplained)} observation(s). "
                  "May be outside this tool (physical tracker, mutual contacts, other apps). "
                  "Expert follow-up recommended."]

    L += ["", "SAFETY PLAN (steps from the vetted playbook, in order)"]
    if plan:
        n = 1
        for s in plan["actionable"]:
            tag = "safe now" if not s["may_notify_abuser"] else "may notify them"
            L.append(f"{n}. {s['title']} [{tag}]"); n += 1
        for s in plan["discuss_first"]:
            L.append(f"{n}. {s['title']} [discuss with advocate first: may notify them]"); n += 1
        unverified = sum(1 for s in plan["actionable"] + plan["discuss_first"]
                         if s["verified_on"] == "UNVERIFIED")
        if unverified:
            L.append(f"Note: {unverified} step(s) have menu paths not yet checked on a current "
                     "device.")
    else:
        L.append("- no plan proposed yet")

    resources = (plan["resources"] if plan and plan["resources"]
                 else validator.resources_for(session["region"])["resources"])
    L += ["", "SUPPORT RESOURCES"]
    L += [f"- {r['name']}: {r['contact']}" for r in resources] or ["- none for this region"]

    rights = validator.rights_for(session["region"])
    if rights:
        L += ["", "RIGHTS BASICS FOR THIS REGION (official information, not legal advice)"]
        for r in rights:
            scope = f" [{r['scope']}]" if r.get("scope") else ""
            L.append(f"- {r['summary']}{scope} (source: {r['source']})")

    L += ["", "Evidence levels: reported = survivor's account; plausible = consistent with the "
              "facts; verified = survivor confirmed what a settings screenshot showed. "
              "'Not verified' does not mean it is not happening.",
          "This summary supports an advocate's assessment; it is not a forensic report."]
    return "\n".join(L)
