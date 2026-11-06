"""Caseworker export: consent required, technical findings only."""
from datetime import date

from fastapi.testclient import TestClient

from app import main, tools
from app.export import build_summary


def demo():
    s = main._new_session()
    tools.set_safety_mode(s, "covert")
    tools.set_context(s, platforms=["apple"], region="UK")
    tools.record_observation(s, "location", "he turned up at Maria's flat on Elm Street")
    tools.record_observation(s, "knew_about_sister_jane_visit", "Jane told me")
    tools.record_finding(s, "apple_id_password", "reported", "interview",
                         note="He set it up in 2019 when we lived in Leeds")
    tools.record_finding(s, "find_my_sharing", "plausible", "inference")
    tools.record_finding(s, "knows_passcode", "plausible", "interview", status="ruled_out")
    tools.hypothesize(s)
    tools.propose_plan(s, ["change_apple_id_password"], ["uk_ndah"])
    s["messages"].append({"role": "user", "content": "my whole story with names"})
    return s


def test_summary_has_technical_findings():
    t = build_summary(demo(), today=date(2026, 11, 6))
    assert "Generated: 2026-11-06" in t
    assert "Covert" in t and "apple" in t and "UK" in t
    assert "Knows your Apple ID password: reported by survivor" in t
    assert "Find My" not in t  # inference-only guess is not a finding
    assert "CHECKED AND NOT FOUND ACTIVE" in t and "Knows your phone passcode" in t
    assert "discuss with advocate first" in t
    assert "0808 2000 247" in t
    assert "1 observation(s)" in t  # unexplained count only


def test_summary_has_no_narrative_or_names():
    t = build_summary(demo())
    for leak in ("Maria", "Elm Street", "Jane", "sister", "Leeds", "2019", "whole story"):
        assert leak not in t, leak


def test_export_requires_consent():
    c = TestClient(main.app)
    sid = c.post("/api/session").json()["session_id"]
    assert c.post("/api/export", json={"session_id": sid}).status_code == 400
    assert c.post("/api/export", json={"session_id": sid, "consent": False}).status_code == 400
    r = c.post("/api/export", json={"session_id": sid, "consent": True})
    assert r.status_code == 200 and "CASEWORKER SUMMARY" in r.json()["summary"]


def test_export_empty_session():
    t = build_summary(main._new_session())
    assert "no plan proposed yet" in t and "none recorded" in t
