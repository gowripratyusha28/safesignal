"""Plan/output validator. RULE: never calls an LLM. See spec.md §11.

Everything Claude wants to show the survivor passes through here:
  lookup_fix / resources_for   – registry lookups (unknown IDs → closest matches)
  validate_findings            – rule 5: "verified" needs a confirmed screenshot
  validate_plan                – rules 1–4, 7: IDs, covert mode, order, documentation,
                                 unexplained-observation notice
  validate_reply               – rule 6 + 7: strip unvetted phone numbers/URLs and
                                 false reassurance from free text
"""
import difflib
import re

from app import data_store, engines

EVIDENCE_LEVELS = ("reported", "plausible", "verified")

UNEXPLAINED_NOTICE = (
    "Some of what you've described isn't explained by what we've checked so far. "
    "It could be something outside this tool, like a physical tracker, someone you "
    "both know, or an app we didn't cover. This does not mean you are imagining it. "
    "A tech-safety expert can help look further."
)

# Resources that can investigate beyond this tool. Used when something is unexplained.
EXPERT_HELPS = {"expert tech consultation", "tech abuse guides", "device guides"}
# Web-based expert guides usable from anywhere, when a region has none of its own.
GLOBAL_EXPERT_FALLBACK = ("nnedv_safetynet", "uk_refuge_tech")

# Official account pages the app may mention in addition to resources/fixes.
EXTRA_ALLOWED_DOMAINS = {"account.apple.com", "myaccount.google.com",
                         "support.apple.com", "support.google.com"}

REGION_ALIASES = {
    "us": "US", "usa": "US", "united states": "US", "united states of america": "US",
    "america": "US", "uk": "UK", "gb": "UK", "united kingdom": "UK", "britain": "UK",
    "great britain": "UK", "england": "UK", "scotland": "UK", "wales": "UK",
    "northern ireland": "UK",
}

# ------------------------------------------------------------------ registry


def _closest(query: str, pool: dict[str, dict], label_key: str) -> list[str]:
    """Closest IDs by id or by title/name similarity."""
    q = query.lower()
    by_id = difflib.get_close_matches(q, list(pool), n=3, cutoff=0.4)
    labels = {v[label_key].lower(): k for k, v in pool.items()}
    by_label = [labels[m] for m in difflib.get_close_matches(q.replace("_", " "), list(labels),
                                                             n=3, cutoff=0.3)]
    return list(dict.fromkeys(by_id + by_label))[:3]


def lookup_fix(fix_id: str) -> dict:
    fix = data_store.fixes().get(fix_id)
    if fix is None:
        return {"found": False, "closest_matches": _closest(fix_id, data_store.fixes(), "title")}
    return {"found": True, **fix}


def lookup_resource(resource_id: str) -> dict:
    res = data_store.resources().get(resource_id)
    if res is None:
        return {"found": False,
                "closest_matches": _closest(resource_id, data_store.resources(), "name")}
    return {"found": True, **res}


def normalize_region(region: str | None) -> str | None:
    """'usa' → 'US', 'us-ny' / 'US, New York'? → 'US-NY' (2-letter state codes only)."""
    if not region:
        return None
    r = region.strip().lower()
    if r in REGION_ALIASES:
        return REGION_ALIASES[r]
    m = re.fullmatch(r"(us|usa)[\s,-]+([a-z]{2})", r)
    if m:
        return f"US-{m.group(2).upper()}"
    return region.strip().upper()


def resources_for(region: str | None) -> dict:
    """Region-specific entries first, then national ones. Never invents anything."""
    reg = normalize_region(region)
    all_res = list(data_store.resources().values())
    if reg is None:
        return {"found": False, "region": None, "resources": [],
                "note": "Ask which country they are in (no other location details needed)."}
    country = reg.split("-")[0]
    local = [r for r in all_res if r["region"] == reg and reg != country]
    national = [r for r in all_res if r["region"] == country]
    global_ = [r for r in all_res if r["region"] == "GLOBAL"]
    found = local + national
    if not found:
        return {"found": False, "region": reg, "resources": global_,
                "note": "No vetted local resources for this region; only global services are "
                        "listed. Suggest their local emergency number; do not name other "
                        "organizations or numbers."}
    return {"found": True, "region": reg, "resources": found + global_}


def rights_for(region: str | None) -> list[dict]:
    """Official rights basics: local (e.g. US-NY) first, then national. Never invented."""
    reg = normalize_region(region)
    if reg is None:
        return []
    country = reg.split("-")[0]
    items = list(data_store.rights().values())
    local = [r for r in items if r["region"] == reg and reg != country]
    national = [r for r in items if r["region"] == country]
    return local + national


def expert_resources(region: str | None) -> list[dict]:
    pool = resources_for(region)["resources"]
    experts = [r for r in pool if EXPERT_HELPS & set(r["helps_with"])]
    if not experts:
        res = data_store.resources()
        experts = [res[i] for i in GLOBAL_EXPERT_FALLBACK if i in res]
    return experts


# ------------------------------------------------------------------ findings


def validate_findings(findings: list[dict]) -> tuple[list[dict], list[str]]:
    """Rule 5. Each finding: {channel_id, evidence_level, basis, screenshot_confirmed}.
    'verified' without a user-confirmed screenshot is downgraded to 'plausible'."""
    chans = data_store.channels()
    out, flags = [], []
    for f in findings:
        cid = f.get("channel_id")
        if cid not in chans:
            flags.append(f"dropped finding for unknown channel {cid!r}")
            continue
        level = f.get("evidence_level")
        if level not in EVIDENCE_LEVELS:
            flags.append(f"{cid}: unknown evidence level {level!r} → reported")
            level = "reported"
        if level == "verified" and not (f.get("basis") == "screenshot"
                                        and f.get("screenshot_confirmed") is True):
            flags.append(f"{cid}: 'verified' needs a user-confirmed screenshot → plausible")
            level = "plausible"
        out.append({**f, "evidence_level": level, "label": chans[cid]["label"]})
    return out, flags


# ---------------------------------------------------------------------- plan


def _with_prerequisites(fix_ids: list[str]) -> tuple[list[str], list[str]]:
    """Add missing prerequisites (recursively). Returns (ids, added)."""
    fixes = data_store.fixes()
    ids = list(dict.fromkeys(fix_ids))
    added: list[str] = []
    i = 0
    while i < len(ids):
        for pre in fixes[ids[i]]["prerequisites"]:
            if pre not in ids:
                ids.append(pre)
                added.append(pre)
        i += 1
    return ids, added


def _topo_order(ids: list[str]) -> list[str]:
    """Stable topological sort: prerequisites first, otherwise keep Claude's order."""
    fixes = data_store.fixes()
    pos = {fid: n for n, fid in enumerate(ids)}
    deps = {fid: {p for p in fixes[fid]["prerequisites"] if p in pos} for fid in ids}
    # document_evidence goes before anything that can erase evidence (rule 4)
    if "document_evidence" in pos:
        for fid in ids:
            if fixes[fid]["evidence_loss"]:
                deps[fid].add("document_evidence")
    order: list[str] = []
    remaining = set(ids)
    while remaining:
        ready = [f for f in remaining if not (deps[f] & remaining)]
        if not ready:  # cycle — shouldn't happen with vetted data
            raise ValueError(f"prerequisite cycle among {sorted(remaining)}")
        nxt = min(ready, key=pos.__getitem__)
        order.append(nxt)
        remaining.remove(nxt)
    return order


def _fix_view(fix: dict, actionable: bool) -> dict:
    return {
        "id": fix["id"], "title": fix["title"], "platform": fix["platform"],
        "steps": fix["steps"], "risk_note": fix["risk_note"], "source": fix["source"],
        "verified_on": fix["verified_on"], "may_notify_abuser": fix["may_notify_abuser"],
        "evidence_loss": fix["evidence_loss"], "loses_access": fix["loses_access"],
        "label": ("Safe now" if not fix["may_notify_abuser"]
                  else "May notify them — consider talking to an advocate first"
                  if actionable else "Discuss with an advocate before doing this"),
    }


def validate_plan(fix_ids: list[str], safety_mode: str | None,
                  active_channels: set[str] | None = None,
                  resource_ids: list[str] | None = None,
                  region: str | None = None,
                  last_hypothesis: dict | None = None,
                  platforms: set[str] | None = None) -> dict:
    """Rules 1–4 and 7. Returns {"ok": False, "rejected": [...]} if any ID is unknown
    (Claude must retry with real IDs); otherwise the display-ready plan."""
    fixes = data_store.fixes()
    resources = data_store.resources()
    resource_ids = resource_ids or []

    # Rule 1: every ID must exist.
    rejected = [{"id": f, "kind": "fix", **lookup_fix(f)} for f in fix_ids if f not in fixes]
    rejected += [{"id": r, "kind": "resource", **lookup_resource(r)}
                 for r in resource_ids if r not in resources]
    if rejected:
        return {"ok": False,
                "rejected": [{"id": r["id"], "kind": r["kind"],
                              "closest_matches": r["closest_matches"]} for r in rejected]}

    notices: list[str] = []
    unexplained = (last_hypothesis or {}).get("unexplained") or []

    # Rule 4: anything that can erase evidence needs documentation first.
    ids = list(fix_ids)
    # Unexplained location → add the safe, passive tracker check (code decides, not Claude).
    if "location" in unexplained and "check_unknown_tracker_alerts" in fixes \
            and "check_unknown_tracker_alerts" not in ids:
        ids.append("check_unknown_tracker_alerts")
        notices.append("Added a safe check for physical trackers, because the location "
                       "observations aren't explained by what we checked.")
    if any(fixes[f]["evidence_loss"] for f in ids) and "document_evidence" not in ids:
        ids.insert(0, "document_evidence")

    # Rule 3: prerequisites present and ordered.
    ids, added = _with_prerequisites(ids)
    if "document_evidence" in ids and "document_evidence" not in fix_ids:
        added = list(dict.fromkeys(["document_evidence", *added]))
    order = _topo_order(ids)
    if added:
        notices.append("Added required earlier steps: " + ", ".join(added))
    reordered = [f for f in order if f in fix_ids] != list(dict.fromkeys(fix_ids))
    if reordered:
        notices.append("Steps were reordered so each one happens after what it depends on.")

    # Rule 2: covert (or unknown) mode → detectable fixes are never actionable.
    covert = safety_mode != "lockdown"
    actionable, discuss_first = [], []
    for fid in order:
        fix = fixes[fid]
        if covert and fix["may_notify_abuser"]:
            discuss_first.append(_fix_view(fix, actionable=False))
        else:
            actionable.append(_fix_view(fix, actionable=True))
    if covert and discuss_first:
        notices.append("Because you may still be in contact with this person, steps they "
                       "could notice are listed separately. Talk them through with an "
                       "advocate before doing any of them.")

    # Resources Claude chose, plus rule 7: unexplained → expert resource + notice.
    chosen = [resources[r] for r in dict.fromkeys(resource_ids)]
    unexplained_notice = None
    if unexplained:
        unexplained_notice = UNEXPLAINED_NOTICE
        if not any(EXPERT_HELPS & set(r["helps_with"]) for r in chosen):
            have = {r["id"] for r in chosen}
            chosen += [r for r in expert_resources(region) if r["id"] not in have][:2]

    simulation = None
    if active_channels is not None:
        # Simulate only what the survivor would actually do now.
        simulation = engines.simulate_plan(set(active_channels),
                                           [f["id"] for f in actionable], platforms)

    return {
        "ok": True,
        "safety_mode": "lockdown" if not covert else "covert",
        "order": order,
        "actionable": actionable,
        "discuss_first": discuss_first,
        "added_prerequisites": added,
        "reordered": reordered,
        "notices": notices,
        "unexplained": unexplained,
        "unexplained_notice": unexplained_notice,
        "resources": chosen,
        "simulation": simulation,
    }


# --------------------------------------------------------------------- reply

_TLDS = r"(?:com|org|net|gov|edu|uk|us|io|info|co|tech)"
URL_RE = re.compile(
    r"\b(?:https?://)?((?:[a-z0-9-]+\.)+" + _TLDS + r")\b(?:/[^\s)\]]*)?", re.IGNORECASE)
PHONE_RE = re.compile(r"(?<![\w-])\+?\d[\d\s().-]{5,}\d(?![\w-])")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

FALSE_REASSURANCE = [
    r"you(?:'| a)re (?:now |completely |totally |all |perfectly )?safe\b(?!\s+to\b)",
    r"\ball clear\b",
    r"nothing to worry about",
    r"no ?one is (?:watching|tracking|monitoring) you",
    r"you(?:'| a)re not being (?:watched|tracked|monitored)",
    r"you(?:'| a)re imagining",
]
_REASSURE_SENTENCE = re.compile(
    r"[^.!?\n]*(?:" + "|".join(FALSE_REASSURANCE) + r")[^.!?\n]*[.!?]?[ \t]*",
    re.IGNORECASE)

REMOVED = "[removed: not a vetted contact]"


def _digits(s: str) -> str:
    return re.sub(r"\D", "", s)


def _allowed_contacts() -> tuple[set[str], set[str]]:
    texts = [r["contact"] for r in data_store.resources().values()]
    texts += [s for f in data_store.fixes().values() for s in f["steps"]]
    texts += [r["summary"] + " " + r["source"] for r in data_store.rights().values()]
    domains = {m.group(1).lower().removeprefix("www.") for t in texts for m in URL_RE.finditer(t)}
    domains |= EXTRA_ALLOWED_DOMAINS
    phones = {_digits(m.group(0)) for t in texts for m in PHONE_RE.finditer(t)}
    return domains, phones


def _domain_ok(domain: str, allowed: set[str]) -> bool:
    d = domain.lower().removeprefix("www.")
    return any(d == a or d.endswith("." + a) for a in allowed)


def scrub_output(text: str) -> tuple[str, list[str]]:
    """Rule 6: strip phone numbers / URLs not present in resources.json (or fixes)."""
    domains, phones = _allowed_contacts()
    flags: list[str] = []

    def url_sub(m: re.Match) -> str:
        if _domain_ok(m.group(1), domains):
            return m.group(0)
        flags.append(f"removed unvetted link: {m.group(0)}")
        return REMOVED

    def phone_sub(m: re.Match) -> str:
        raw = m.group(0)
        d = _digits(raw)
        if DATE_RE.match(raw.strip()) or len(d) < 7 or len(d) > 15 or d in phones:
            return raw
        flags.append(f"removed unvetted phone number: {raw.strip()}")
        return REMOVED

    text = URL_RE.sub(url_sub, text)
    text = PHONE_RE.sub(phone_sub, text)
    return text, flags


def validate_reply(text: str) -> tuple[str, list[str]]:
    """Rules 6–7 for free text: unvetted contacts and false reassurance are removed.
    Checks are never complete, so 'you're safe' is never allowed."""
    text, flags = scrub_output(text)

    def reassure_sub(m: re.Match) -> str:
        flags.append(f"removed false reassurance: {m.group(0).strip()}")
        return ""

    text = _REASSURE_SENTENCE.sub(reassure_sub, text)
    text = re.sub(r"[ \t]+\n", "\n", text).strip()
    return text, flags
