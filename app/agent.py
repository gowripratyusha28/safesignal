"""Claude tool-use loop. Claude reasons; engines/validator decide.

Tools are registered in TOOLS (schemas sent to Claude) and HANDLERS
(python functions that run them). Hour 1–3 fills these in.
"""
import json
import os

import anthropic

MODEL = "claude-sonnet-5-5"
MAX_ITERATIONS = 8

SYSTEM_PROMPT = """You are a trauma-informed tech-safety advocate helping someone who may be experiencing
technology-facilitated abuse. You run a consultation like a trained clinic volunteer:
listen, form hypotheses, ask for specific evidence, verify, then build a safe plan.

Rules:
- First, ask whether they still live with or are in regular contact with the person.
  Call set_safety_mode.
- Ask ONE question at a time. Use plain, warm language. Believe them; never call their
  concerns paranoid. Never claim the person IS watching unless a finding is verified.
- Do not ask for names, addresses, children's details, or escape plans. Refer to people
  by role ("your former partner").
- Use hypothesize to decide what to check next. Request the screenshot that best
  distinguishes the top candidates.
- You may ONLY recommend fixes returned by get_fix and resources from get_resources.
  Never invent steps, menu paths, phone numbers, or organizations.
- Before proposing a plan, call simulate_plan and resolve any remaining exposure or
  order problem.
- If hypothesize returns anything under "unexplained", say clearly that what we've
  checked doesn't explain it, that it may be something outside this tool (a physical
  tracker, someone they both know, an app we didn't cover), and show expert resources.
  Never imply they are now safe.
- Never perform or claim to perform changes. The survivor decides.
- Recommend documenting evidence before any change.
- If they are in immediate danger, direct them to emergency services and the hotline
  from get_resources first.
- You support advocates; you do not replace them. Encourage contacting an advocate.
- Reply in the same language the person writes in.
"""

# Tool schemas (Claude-facing) and handlers (python). Filled in Hour 1–3.
TOOLS: list[dict] = []
HANDLERS: dict = {}  # name -> fn(session: dict, **input) -> dict

_client: anthropic.Anthropic | None = None


def client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def _call_claude(messages: list) -> object:
    kwargs = dict(
        model=MODEL,
        max_tokens=16000,
        # Cache the long, stable system prompt (tools render before system, and
        # the tool list is static, so both stay in the cached prefix).
        system=[{"type": "text", "text": SYSTEM_PROMPT,
                 "cache_control": {"type": "ephemeral"}}],
        messages=messages,
        output_config={"effort": "medium"},
        # Server-side fallback if a safety classifier declines (DV topics can trip it).
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if TOOLS:
        kwargs["tools"] = TOOLS
    return client().beta.messages.create(**kwargs)


def _run_tool(session: dict, name: str, tool_input: dict) -> tuple[str, bool]:
    handler = HANDLERS.get(name)
    if handler is None:
        return json.dumps({"error": f"unknown tool {name}"}), True
    try:
        return json.dumps(handler(session, **tool_input)), False
    except Exception as e:  # report to Claude, don't crash the turn
        return json.dumps({"error": str(e)}), True


def run_turn(session: dict, user_content: list | str) -> str:
    """Append a user turn, loop through tool calls, return the user-facing text.

    History is append-only: full response.content (including thinking blocks)
    is stored back unchanged.
    """
    messages = session["messages"]
    messages.append({"role": "user", "content": user_content})

    for _ in range(MAX_ITERATIONS):
        resp = _call_claude(messages)
        content = [b.model_dump(exclude_none=True) for b in resp.content]
        messages.append({"role": "assistant", "content": content})

        if resp.stop_reason == "refusal":
            return ("I'm not able to help with that here. If you are in danger, please contact "
                    "emergency services or a domestic violence hotline.")

        tool_uses = [b for b in resp.content if b.type == "tool_use"]
        if resp.stop_reason != "tool_use" or not tool_uses:
            return "".join(b.text for b in resp.content if b.type == "text").strip()

        results = []
        for tu in tool_uses:
            out, is_err = _run_tool(session, tu.name, tu.input)
            results.append({"type": "tool_result", "tool_use_id": tu.id,
                            "content": out, "is_error": is_err})
        messages.append({"role": "user", "content": results})

    return "I need a moment to think this through — could you say that again?"
