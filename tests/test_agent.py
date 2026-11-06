"""Agent loop behaviour without calling the API (Claude is faked)."""
from types import SimpleNamespace as NS

from app import agent
from app.main import _new_session


def _resp(content, stop):
    blocks = []
    for c in content:
        b = NS(**c)
        b.model_dump = (lambda c=c: lambda **kw: dict(c))()
        blocks.append(b)
    return NS(content=blocks, stop_reason=stop)


def test_failure_mid_turn_rolls_back_history(monkeypatch):
    s = _new_session()
    s["messages"] = [{"role": "user", "content": "earlier"},
                     {"role": "assistant", "content": [{"type": "text", "text": "ok"}]}]
    calls = iter([
        _resp([{"type": "tool_use", "id": "t1", "name": "hypothesize", "input": {}}], "tool_use"),
        RuntimeError("API down"),
    ])

    def fake(messages):
        r = next(calls)
        if isinstance(r, Exception):
            raise r
        return r

    monkeypatch.setattr(agent, "_call_claude", fake)
    reply = agent.run_turn(s, "new message")
    assert reply == agent.FALLBACK_ERROR_REPLY
    assert len(s["messages"]) == 2  # unanswered tool_use was not left behind


def test_reply_is_validated(monkeypatch):
    s = _new_session()
    monkeypatch.setattr(agent, "_call_claude", lambda m: _resp(
        [{"type": "text", "text": "You're safe now. Call 1-888-555-0199."}], "end_turn"))
    reply = agent.run_turn(s, "hi")
    assert "safe now" not in reply and "555" not in reply


def test_legal_question_adds_operator_instruction(monkeypatch):
    s = _new_session()
    monkeypatch.setattr(agent, "_call_claude", lambda m: _resp(
        [{"type": "text", "text": "ok"}], "end_turn"))
    agent.run_turn(s, "Is what he's doing even illegal?")
    roles = [m["role"] for m in s["messages"]]
    assert roles == ["user", "system", "assistant"]
    assert s["messages"][1]["content"] == agent.RIGHTS_INSTRUCTION
    assert any("rights list" in e["text"] for e in s["trace"])

    s2 = _new_session()
    agent.run_turn(s2, "He always knows where I am.")
    assert [m["role"] for m in s2["messages"]] == ["user", "assistant"]
    agent.run_turn(s2, "[App message, not typed by the person] court screen read")
    assert "system" not in [m["role"] for m in s2["messages"]]


def test_plan_request_adds_operator_instruction(monkeypatch):
    s = _new_session()
    monkeypatch.setattr(agent, "_call_claude", lambda m: _resp(
        [{"type": "text", "text": "ok"}], "end_turn"))
    agent.run_turn(s, "No, nothing like that. What can I do?")
    assert s["messages"][1] == {"role": "system", "content": agent.PLAN_INSTRUCTION}
    s2 = _new_session()
    agent.run_turn(s2, "Is this illegal? What can I do?")   # law question wins
    assert s2["messages"][1]["content"] == agent.RIGHTS_INSTRUCTION
