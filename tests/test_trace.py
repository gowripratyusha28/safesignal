"""The engine trace shows decisions, never content."""
from app import agent, tools, trace
from app.main import _new_session, _public_state


def run(s, name, **inp):
    out, _ = agent._run_tool(s, name, inp)
    return out


def test_trace_records_decisions_without_content():
    s = _new_session()
    run(s, "set_safety_mode", mode="covert")
    run(s, "record_observation", knowledge="location", evidence="he came to Maria's flat on Elm St")
    run(s, "record_finding", channel_id="find_my_sharing", evidence_level="verified",
        basis="screenshot", note="he said it in 2019 in Leeds")
    run(s, "hypothesize")
    run(s, "get_fix", fix_id="hack_his_phone")
    run(s, "propose_plan", fix_ids=["remove_unknown_device"])
    text = " ".join(e["text"] for e in s["trace"])
    for leak in ("Maria", "Elm", "2019", "Leeds"):
        assert leak not in text
    assert "mode = covert" in text
    assert "find_my_sharing → plausible" in text and "confirmed screenshot" in text
    assert "ranked" in text and "find_my_sharing" in text
    assert "NOT in the playbook" in text
    assert "added missing prerequisites" in text and "advocate-first" in text
    assert _public_state(s)["trace"] == s["trace"]


def test_trace_is_bounded_and_never_breaks_turn(monkeypatch):
    s = _new_session()
    for _ in range(trace.MAX_ENTRIES + 10):
        trace.add(s, "x", "y")
    assert len(s["trace"]) == trace.MAX_ENTRIES

    def boom(*a, **k):
        raise RuntimeError("trace bug")
    monkeypatch.setattr(trace, "for_tool", boom)
    out, is_err = agent._run_tool(s, "set_safety_mode", {"mode": "lockdown"})
    assert not is_err and s["safety_mode"] == "lockdown"


def test_reply_check_logs_kind_only(monkeypatch):
    s = _new_session()
    from tests.test_agent import _resp
    monkeypatch.setattr(agent, "_call_claude", lambda m: _resp(
        [{"type": "text", "text": "Call 1-888-555-0199 now."}], "end_turn"))
    agent.run_turn(s, "hi")
    assert s["trace"][-1]["text"] == "removed unvetted phone number"
    assert "555" not in str(s["trace"])
