"""Deterministic engines: simulator (forward) + hypothesize (backward).

RULE: this module must NEVER call an LLM. See spec.md §9.

Vocabulary: observations and channel `reveals` share one vocabulary
(see OBSERVABLES). Anything outside it can't be explained by any channel and
is returned under "unexplained".
"""
from itertools import combinations

from app import data_store

# recovery_control lets them reset these accounts even after a password change.
RECOVERY_REOPENS = ("apple_id_password", "google_signed_in")

# knows_passcode reveals "everything_with_physical_access": it can explain any
# data stored on the phone, but not live location, and at lower weight because
# it needs physical access.
PHYSICAL_ACCESS = "everything_with_physical_access"
PHYSICAL_ACCESS_COVERS = frozenset({
    "messages", "photos", "notes", "backups", "sms", "whatsapp_messages",
    "email", "call_logs", "sms_logs", "location_history",
})

HIT_WEIGHT = 1.0
WILDCARD_HIT_WEIGHT = 0.5
EXTRA_PENALTY = 0.1     # predicts things they haven't shown knowing
CHANNEL_PENALTY = 0.3   # per channel: prefer simpler explanations
TOP_N = 8


def observables() -> list[str]:
    """Every observation term a channel can explain (for the agent's tool schema)."""
    terms = {r for c in data_store.channels().values() for r in c["reveals"]}
    terms.discard(PHYSICAL_ACCESS)
    return sorted(terms | PHYSICAL_ACCESS_COVERS)


# ---------------------------------------------------------------- simulator

PLATFORMS = ("apple", "google", "whatsapp")


def channel_in_scope(channel_id: str, platforms: set[str] | None) -> bool:
    """platforms=None means 'not known yet' → every channel is in scope."""
    if platforms is None:
        return True
    plat = data_store.channels()[channel_id].get("platform", "any")
    return plat == "any" or plat in platforms


def _effective(active: set[str], platforms: set[str] | None = None) -> set[str]:
    eff = set(active)
    if "recovery_control" in eff:
        eff.update(c for c in RECOVERY_REOPENS if channel_in_scope(c, platforms))
    return eff


def exposed(active_channels: set[str], platforms: set[str] | None = None) -> set[str]:
    """Union of everything revealed by active channels.
    If recovery_control is active, account reset re-enables apple_id_password
    and google access even after a password change."""
    chans = data_store.channels()
    out: set[str] = set()
    for cid in _effective(active_channels, platforms):
        if cid in chans:
            out.update(chans[cid]["reveals"])
    return out


def simulate_plan(active_channels: set[str], fix_ids: list[str],
                  platforms: set[str] | None = None) -> dict:
    """Apply fixes in order and report what's left and what's wrong.

    Returns {"remaining_channels", "still_exposed", "order_problems", "unknown_fixes"}.
    A password/device fix applied while recovery_control is still active does
    not stick: the channel stays open and an order problem is reported.
    """
    fixes = data_store.fixes()
    remaining = set(active_channels)
    applied: list[str] = []
    problems: list[str] = []
    unknown: list[str] = []

    for fid in fix_ids:
        fix = fixes.get(fid)
        if fix is None:
            unknown.append(fid)
            continue
        for pre in fix["prerequisites"]:
            if pre not in applied:
                where = "later in the plan" if pre in fix_ids else "missing from the plan"
                problems.append(f"{fid} needs {pre} first ({where})")
        if fix["evidence_loss"] and "document_evidence" not in applied:
            problems.append(f"{fid} can erase evidence; document_evidence must come first")
        for cid in fix["closes"]:
            if cid in RECOVERY_REOPENS and "recovery_control" in remaining:
                problems.append(
                    f"{fid} won't hold: they control your recovery email/phone and "
                    f"can reset access to {cid} — fix recovery first")
                continue
            remaining.discard(cid)
        applied.append(fid)

    # dedupe, keep order
    problems = list(dict.fromkeys(problems))
    return {
        "remaining_channels": sorted(remaining),
        "still_exposed": sorted(exposed(remaining, platforms)),
        "order_problems": problems,
        "unknown_fixes": unknown,
    }


# --------------------------------------------------------------- hypothesize

def _explains(channel: dict, observed: set[str]) -> tuple[set[str], set[str]]:
    """(direct hits, wildcard hits) for one channel."""
    reveals = set(channel["reveals"])
    direct = reveals & observed
    wild = (observed & PHYSICAL_ACCESS_COVERS) - direct if PHYSICAL_ACCESS in reveals else set()
    return direct, wild


def _score(members: list[dict], observed: set[str]) -> tuple[float, set[str]]:
    direct: set[str] = set()
    wild: set[str] = set()
    predicts: set[str] = set()
    for ch in members:
        d, w = _explains(ch, observed)
        direct |= d
        wild |= w
        predicts |= set(ch["reveals"]) - {PHYSICAL_ACCESS}
    wild -= direct
    extra = predicts - observed
    score = (HIT_WEIGHT * len(direct) + WILDCARD_HIT_WEIGHT * len(wild)
             - EXTRA_PENALTY * len(extra) - CHANNEL_PENALTY * len(members))
    return round(score, 3), direct | wild


def _best_check(candidates: list[dict]) -> dict | None:
    """Screenshot that best splits the top candidates (by score weight)."""
    chans = data_store.channels()
    top = candidates[:5]
    if not top:
        return None
    weights = [max(c["score"], 0.01) for c in top]
    total = sum(weights)
    options = sorted({cid for c in top for cid in c["channels"]
                      if chans[cid]["how_to_verify"].startswith("screenshot:")})
    if not options:
        return None

    def rank(cid: str):
        inside = sum(w for c, w in zip(top, weights) if cid in c["channels"])
        split = min(inside, total - inside) / total
        in_top = cid in top[0]["channels"]
        return (-split, not in_top, cid)

    cid = min(options, key=rank)
    return {
        "channel_id": cid,
        "screen_id": chans[cid]["how_to_verify"].split(":", 1)[1],
        "label": chans[cid]["label"],
    }


def hypothesize(observed: set[str], ruled_out: set[str] | frozenset[str] = frozenset(),
                platforms: set[str] | None = None) -> dict:
    """Input: what they seem to know, e.g. {"location", "messages"}.

    Returns {
      "candidates": [{channels, explains, unexplained, score}, ...]  (best first),
      "best_check": {channel_id, screen_id, label} | None,
      "interview_checks": [channel ids that can only be checked by asking],
      "unexplained": observations NO remaining channel can explain,
    }
    If "unexplained" is non-empty the agent must refer to an expert and never
    imply the survivor is safe.
    """
    observed = set(observed)
    chans = [c for cid, c in sorted(data_store.channels().items())
             if cid not in ruled_out and channel_in_scope(cid, platforms)]

    explainable: set[str] = set()
    useful: list[dict] = []
    for ch in chans:
        d, w = _explains(ch, observed)
        if d or w:
            useful.append(ch)
            explainable |= d | w

    candidates = []
    for ch in useful:
        score, hits = _score([ch], observed)
        candidates.append({"channels": [ch["id"]], "explains": sorted(hits),
                           "unexplained": sorted(observed - hits), "score": score})

    for a, b in combinations(useful, 2):
        ha = set().union(*_explains(a, observed))
        hb = set().union(*_explains(b, observed))
        if not (ha - hb) or not (hb - ha):
            continue  # one member adds nothing the other doesn't already explain
        score, hits = _score([a, b], observed)
        candidates.append({"channels": [a["id"], b["id"]], "explains": sorted(hits),
                           "unexplained": sorted(observed - hits), "score": score})

    candidates.sort(key=lambda c: (-len(c["explains"]), -c["score"],
                                   len(c["channels"]), c["channels"]))
    candidates = candidates[:TOP_N]

    top_ids = {cid for c in candidates[:5] for cid in c["channels"]}
    interview = sorted(cid for cid in top_ids
                       if data_store.channels()[cid]["how_to_verify"] == "interview")

    return {
        "candidates": candidates,
        "best_check": _best_check(candidates),
        "interview_checks": interview,
        "unexplained": sorted(observed - explainable),
    }
