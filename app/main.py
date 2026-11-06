"""FastAPI routes. In-memory sessions only — nothing is persisted or logged."""
import base64
import secrets
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # ANTHROPIC_API_KEY from .env; never sent to the browser

from fastapi import FastAPI, File, Form, HTTPException, UploadFile  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from app import agent, engines, tools, validator  # noqa: E402

app = FastAPI(title="SafeSignal", docs_url=None, redoc_url=None)

SESSION_TTL_SECONDS = 30 * 60
SESSIONS: dict[str, dict] = {}
STATIC = Path(__file__).parent / "static"
ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}


def _new_session() -> dict:
    return {
        "messages": [],
        "safety_mode": None,      # "covert" | "lockdown"
        "platforms": [],          # subset of engines.PLATFORMS; empty = unknown
        "region": None,
        "observations": [],       # [{knowledge, evidence}]
        "findings": {},           # channel_id -> {evidence_level, basis, screenshot_confirmed, note}
        "ruled_out": set(),
        "last_hypothesis": None,
        "pending_screenshot": None,
        "plan_request": None,
        "plan": None,
        "touched": time.time(),
    }


def _expire_old() -> None:
    now = time.time()
    for sid in [s for s, v in SESSIONS.items() if now - v["touched"] > SESSION_TTL_SECONDS]:
        SESSIONS.pop(sid, None)


def _get(sid: str) -> dict:
    _expire_old()
    s = SESSIONS.get(sid)
    if s is None:
        raise HTTPException(404, "session expired")
    s["touched"] = time.time()
    return s


def _public_state(s: dict) -> dict:
    """What the right-hand panel shows. Never includes conversation text."""
    findings, _ = validator.validate_findings(list(s["findings"].values()))
    hyp = s["last_hypothesis"] or {}
    plan = s["plan"]
    resources = (plan["resources"] if plan and plan["resources"]
                 else validator.resources_for(s["region"])["resources"])
    return {
        "safety_mode": s["safety_mode"],
        "platforms": s["platforms"],
        "findings": [{k: f[k] for k in ("channel_id", "label", "evidence_level", "basis")}
                     for f in findings],
        "exposed": sorted(engines.exposed(tools.active_channels(s), tools.platforms(s))),
        "unexplained": hyp.get("unexplained", []),
        "pending_screenshot": s["pending_screenshot"],
        "plan": plan,
        "resources": resources,
    }


class MessageIn(BaseModel):
    session_id: str
    text: str


class SessionIn(BaseModel):
    session_id: str


@app.post("/api/session")
def start_session():
    _expire_old()
    sid = secrets.token_urlsafe(24)
    SESSIONS[sid] = _new_session()
    return {"session_id": sid, "state": _public_state(SESSIONS[sid])}


@app.post("/api/message")
def message(body: MessageIn):
    s = _get(body.session_id)
    reply = agent.run_turn(s, body.text)
    return {"reply": reply, "state": _public_state(s)}


@app.post("/api/screenshot")
async def screenshot(session_id: str = Form(...), note: str = Form(""),
                     file: UploadFile = File(...)):
    s = _get(session_id)
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(400, "Please upload a PNG, JPEG, WebP or GIF image.")
    data = await file.read()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(400, "Image is too large (max 5 MB).")
    content = [
        {"type": "image", "source": {"type": "base64", "media_type": file.content_type,
                                     "data": base64.b64encode(data).decode()}},
        {"type": "text", "text": note or "Here is the screenshot you asked for."},
    ]
    reply = agent.run_turn(s, content)
    return {"reply": reply, "state": _public_state(s)}


@app.post("/api/plan")
def plan(body: SessionIn):
    return _public_state(_get(body.session_id))


@app.post("/api/exit")
def quick_exit(body: SessionIn):
    SESSIONS.pop(body.session_id, None)
    return {"ok": True}


@app.post("/api/export")
def export(body: SessionIn):
    raise HTTPException(501, "Caseworker export not built yet (P2).")


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html", headers={"Cache-Control": "no-store"})
