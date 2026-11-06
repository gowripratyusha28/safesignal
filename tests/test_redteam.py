"""Deterministic guarantees behind the abuser-pretext red team (live run: demo/redteam.py)."""
import json
from pathlib import Path

from app import agent, data_store, validator


def test_redteam_prompt_set_loads():
    prompts = json.loads(Path("demo/redteam_prompts.json").read_text())
    assert len(prompts) >= 10
    assert len({p["id"] for p in prompts}) == len(prompts)
    assert {"direct_location", "novelist_pretext", "evade_alert"} <= {p["id"] for p in prompts}


def test_prompt_states_own_accounts_only_rule():
    assert "OWN accounts and devices" in agent.SYSTEM_PROMPT
    assert "whatever the stated" in agent.SYSTEM_PROMPT


def test_playbook_has_no_offensive_capability():
    """Every fix closes one of the user's own exposure channels or is an info step."""
    chans = data_store.channels()
    for f in data_store.fixes().values():
        assert all(c in chans for c in f["closes"]), f["id"]
        text = " ".join(f["steps"]).lower()
        for phrase in ("without them knowing", "without her knowing", "hidden from",
                       "secretly", "install on their"):
            assert phrase not in text, (f["id"], phrase)


def test_unexplained_location_adds_safe_tracker_check():
    r = validator.validate_plan(["document_evidence"], "covert",
                                last_hypothesis={"unexplained": ["location"]})
    ids = [s["id"] for s in r["actionable"]]
    assert "check_unknown_tracker_alerts" in ids           # safe: not moved to advocate-first
    assert any("physical trackers" in n for n in r["notices"])
    r2 = validator.validate_plan(["document_evidence"], "covert",
                                 last_hypothesis={"unexplained": ["car_conversation"]})
    assert "check_unknown_tracker_alerts" not in r2["order"]


def test_global_resources_appear_after_national_and_for_unknown_regions():
    uk = validator.resources_for("UK")["resources"]
    assert uk[-1]["region"] == "GLOBAL" and uk[0]["region"] == "UK"
    unknown = validator.resources_for("Atlantis")
    assert unknown["found"] is False
    assert unknown["resources"] and all(r["region"] == "GLOBAL" for r in unknown["resources"])
