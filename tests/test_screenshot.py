"""Screenshot flow: image never enters history; only the user's click confirms."""
import pytest
from fastapi.testclient import TestClient

from app import main, tools, vision

READING = {"screen": "Apple Account devices", "matches_requested_screen": True,
           "devices": ["This iPhone", "Home iPad"], "people_sharing": [], "settings": [],
           "uncertain": [], "need_more": ""}
PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 100


@pytest.fixture
def env(monkeypatch):
    seen = []
    monkeypatch.setattr(vision, "extract", lambda data, mt, sid: dict(READING))
    monkeypatch.setattr(main.agent, "run_turn",
                        lambda s, msg: (seen.append(msg), "ok")[1])
    c = TestClient(main.app)
    sid = c.post("/api/session").json()["session_id"]
    return c, sid, main.SESSIONS[sid], seen


def upload(c, sid, data=PNG, ctype="image/png"):
    return c.post("/api/screenshot", data={"session_id": sid},
                  files={"file": ("s.png", data, ctype)})


def test_upload_requires_a_request(env):
    c, sid, s, _ = env
    assert upload(c, sid).status_code == 400


def test_upload_returns_reading_and_keeps_image_out_of_history(env):
    c, sid, s, seen = env
    tools.request_screenshot(s, "apple_id_devices", "Settings → your name")
    r = upload(c, sid)
    assert r.status_code == 200 and r.json()["reading"]["devices"] == READING["devices"]
    assert s["messages"] == [] and seen == []   # nothing sent to the agent yet
    assert not any(isinstance(b, dict) and b.get("type") == "image"
                   for m in s["messages"] for b in (m["content"] if isinstance(m["content"], list) else []))
    assert "data:" not in str(s["pending_confirmation"])  # only the JSON reading is kept


def test_rejects_non_image(env):
    c, sid, s, _ = env
    tools.request_screenshot(s, "apple_id_devices", "x")
    assert upload(c, sid, b"hi", "text/plain").status_code == 400


def test_confirm_yes_enables_verified(env):
    c, sid, s, seen = env
    tools.request_screenshot(s, "apple_id_devices", "x")
    upload(c, sid)
    r = c.post("/api/screenshot/confirm", json={"session_id": sid, "confirmed": True})
    assert r.json()["confirmed"] is True
    assert "apple_id_devices" in s["confirmed_screens"]
    assert s["pending_screenshot"] is None and s["pending_confirmation"] is None
    assert "CONFIRMED" in seen[0] and "Home iPad" in seen[0]
    res = tools.record_finding(s, "signed_in_device", "verified", "screenshot")
    assert res["recorded_level"] == "verified"


def test_confirmed_screen_only_verifies_its_own_channel(env):
    c, sid, s, _ = env
    tools.request_screenshot(s, "apple_id_devices", "x")
    upload(c, sid)
    c.post("/api/screenshot/confirm", json={"session_id": sid, "confirmed": True})
    res = tools.record_finding(s, "find_my_sharing", "verified", "screenshot")
    assert res["recorded_level"] == "plausible"


def test_confirm_no_does_not_verify(env):
    c, sid, s, seen = env
    tools.request_screenshot(s, "apple_id_devices", "x")
    upload(c, sid)
    r = c.post("/api/screenshot/confirm",
               json={"session_id": sid, "confirmed": False, "correction": "list was cut off"})
    assert r.json()["confirmed"] is False
    assert s["confirmed_screens"] == set()
    assert s["pending_screenshot"] is not None  # can try again
    assert "NOT right" in seen[0] and "cut off" in seen[0]
    assert tools.record_finding(s, "signed_in_device", "verified",
                                "screenshot")["recorded_level"] == "plausible"


def test_wrong_screen_cannot_be_confirmed(env, monkeypatch):
    c, sid, s, seen = env
    monkeypatch.setattr(vision, "extract",
                        lambda *a: {**READING, "matches_requested_screen": False})
    tools.request_screenshot(s, "apple_id_devices", "x")
    upload(c, sid)
    r = c.post("/api/screenshot/confirm", json={"session_id": sid, "confirmed": True})
    assert r.json()["confirmed"] is False and s["confirmed_screens"] == set()


def test_confirm_without_reading(env):
    c, sid, s, _ = env
    r = c.post("/api/screenshot/confirm", json={"session_id": sid, "confirmed": True})
    assert r.status_code == 400


def test_vision_failure_is_friendly(env, monkeypatch):
    c, sid, s, _ = env
    def boom(*a):
        raise RuntimeError("api down")
    monkeypatch.setattr(vision, "extract", boom)
    tools.request_screenshot(s, "apple_id_devices", "x")
    r = upload(c, sid)
    assert r.status_code == 502 and s["pending_screenshot"] is not None


def test_skip_closes_upload_box(env):
    c, sid, s, seen = env
    tools.request_screenshot(s, "apple_id_devices", "x")
    r = c.post("/api/screenshot/skip", json={"session_id": sid})
    assert r.json()["state"]["pending_screenshot"] is None
    assert seen == [] and s["confirmed_screens"] == set()


def test_after_skip_further_screenshot_requests_are_blocked(env):
    c, sid, s, seen = env
    tools.request_screenshot(s, "apple_id_devices", "x")
    c.post("/api/screenshot/skip", json={"session_id": sid})
    r = tools.request_screenshot(s, "family", "y")
    assert "error" in r and "in words" in r["error"] and s["pending_screenshot"] is None
    r = tools.request_screenshot(s, "family", "y", person_offered=True)
    assert r["ok"] and s["pending_screenshot"]["screen_id"] == "family"
    upload(c, sid)                                   # a real upload lifts the block
    assert s["screenshot_declined"] is False
