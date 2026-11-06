"""Tool handlers over session state (no LLM)."""
from app import tools
from app.main import _new_session, _public_state


def demo_session(mode="lockdown"):
    s = _new_session()
    tools.set_safety_mode(s, mode)
    tools.set_context(s, platforms=["apple"], region="usa")
    tools.record_observation(s, "location", "showed up at a café")
    tools.record_observation(s, "messages", "knew what she texted her sister")
    return s


def test_tool_schemas_match_handlers():
    assert {t["name"] for t in tools.TOOLS} == set(tools.HANDLERS)


def test_context_and_region_normalized():
    s = demo_session()
    assert s["platforms"] == ["apple"] and s["region"] == "US"


def test_bad_inputs_return_errors_not_exceptions():
    s = _new_session()
    assert "error" in tools.set_safety_mode(s, "maybe")
    assert "error" in tools.set_context(s, platforms=["blackberry"])
    assert "error" in tools.record_finding(s, "spyware", "reported", "interview")
    assert "error" in tools.request_screenshot(s, "home_screen", "x")


def test_hypothesis_uses_session_platforms():
    s = demo_session()
    h = tools.hypothesize(s)
    ids = {c for cand in h["candidates"] for c in cand["channels"]}
    assert "google_location_share" not in ids
    assert s["last_hypothesis"] is h


def test_unknown_observation_flows_to_unexplained():
    s = demo_session()
    r = tools.record_observation(s, "conversation in car")
    assert r["in_vocabulary"] is False
    assert tools.hypothesize(s)["unexplained"] == ["conversation_in_car"]


def test_claude_cannot_self_verify():
    s = demo_session()
    r = tools.record_finding(s, "find_my_sharing", "verified", "screenshot")
    assert r["recorded_level"] == "plausible"
    assert s["findings"]["find_my_sharing"]["screenshot_confirmed"] is False


def test_rule_out_removes_finding():
    s = demo_session()
    tools.record_finding(s, "signed_in_device", "plausible", "inference")
    tools.record_finding(s, "signed_in_device", "plausible", "screenshot", status="ruled_out")
    assert "signed_in_device" not in s["findings"]
    assert "signed_in_device" in s["ruled_out"]


def test_full_demo_plan_lockdown_then_covert():
    s = demo_session("lockdown")
    for cid in ("find_my_sharing", "signed_in_device", "recovery_control"):
        tools.record_finding(s, cid, "plausible", "interview")
    tools.hypothesize(s)
    r = tools.propose_plan(s, ["remove_unknown_device", "stop_find_my_sharing"], ["us_ndvh"])
    assert r["ok"]
    assert r["shown_as_discuss_with_advocate_first"] == []
    assert "fix_recovery_email" in r["added_prerequisites"]
    assert r["still_exposed_after_actionable_steps"] == []
    # switching mode re-validates the stored plan
    tools.set_safety_mode(s, "covert")
    assert [x["id"] for x in s["plan"]["actionable"]] == ["document_evidence"]
    state = _public_state(s)
    assert state["plan"]["safety_mode"] == "covert"
    assert "location" in state["plan"]["simulation"]["still_exposed"]


def test_propose_plan_rejects_invented_ids():
    s = demo_session()
    r = tools.propose_plan(s, ["delete_his_account"])
    assert r["ok"] is False and r["rejected"]
    assert s["plan"] is None


def test_public_state_has_no_conversation_text():
    s = demo_session()
    s["messages"].append({"role": "user", "content": "secret story"})
    assert "secret story" not in str(_public_state(s))
    assert "café" not in str(_public_state(s))


def test_catalog_is_deterministic():
    assert tools.catalog_text() == tools.catalog_text()
    assert "stop_find_my_sharing" in tools.catalog_text()


def test_inference_only_is_a_possibility_not_a_finding():
    s = demo_session()
    tools.record_finding(s, "apple_id_password", "reported", "interview")
    tools.record_finding(s, "find_my_sharing", "plausible", "inference")
    state = _public_state(s)
    assert [f["channel_id"] for f in state["findings"]] == ["apple_id_password"]
    assert [f["channel_id"] for f in state["to_check"]] == ["find_my_sharing"]
    assert tools.active_channels(s) == {"apple_id_password"}


def test_inference_only_does_not_count_toward_exposure():
    s = demo_session()
    tools.record_finding(s, "sms_forwarding", "plausible", "inference")
    assert _public_state(s)["exposed"] == []
    assert tools.simulate_plan(s, [])["still_exposed"] == []


def test_inference_upgraded_by_interview_becomes_finding():
    s = demo_session()
    tools.record_finding(s, "find_my_sharing", "plausible", "inference")
    tools.record_finding(s, "find_my_sharing", "reported", "interview")
    state = _public_state(s)
    assert [f["channel_id"] for f in state["findings"]] == ["find_my_sharing"]
    assert state["to_check"] == [] and "location" in state["exposed"]
