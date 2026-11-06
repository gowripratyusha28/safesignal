# SafeSignal: Tech-Safety Copilot

An AI copilot that does what a trained tech-safety advocate does in a clinic consultation. It
listens to a survivor's story, forms hypotheses about how an abuser is getting information,
asks for the one settings screenshot that best tells them apart, reads it, and produces a
**detection-aware, dependency-ordered** plan from a vetted playbook, plus region-appropriate support.

Built for *Code with Claude: Women in AI Hackathon*, Track 2 (Safety and rights). Supports
advocates; does not replace them.

## Core principle: Claude reasons, code decides

| Claude (LLM) | Deterministic code (tested, no LLM) |
|---|---|
| Understands messy stories, runs the interview | `engines.py`: what each access channel exposes; ranks causes; simulates a plan |
| Chooses what to ask next, reads screenshots | `validator.py`: only real fix/resource IDs; safety mode; ordering; evidence levels |
| Explains kindly in plain language | Strips unvetted phone numbers/URLs and false reassurance from every reply |

Claude can only reference fixes in `app/data/fixes.json` and resources in `app/data/resources.json`.

## Safety design (against six failure modes)
1. **False accusation:** every finding is `reported` / `plausible` / `verified`. "Verified" requires the
   survivor to confirm a screenshot reading; code enforces it, and only for that screen's channel.
2. **A step alerts the abuser:** covert mode (still in contact, or unsure) never shows detectable steps as
   actionable. Plans are reordered so access can't be regained (e.g. recovery email before password).
3. **The tool becomes a record:** in-memory sessions only, 30-minute expiry, no content logs, no
   localStorage. Screenshots are read once and discarded. No names or addresses are asked for.
4. **The abuser uses it:** it analyses only your own accounts and gives defensive guidance only.
5. **Traces on a compromised device:** Quick Exit (button or Esc twice), iCloud Photos warning before
   screenshots, safe-device guidance.
6. **Stale instructions:** each playbook entry cites an official source and has a `verified_on` date;
   unchecked entries are labelled in the UI.

Anything the checks can't explain is flagged with expert resources, never "you're safe".

**Rights (Track 2):** `app/data/rights.json` holds short, plain-language facts about the law per region
(US, US-NY, UK/England & Wales), each with an official source URL. Shown as "official information,
not legal advice"; Claude can restate them but cannot cite a law that isn't in the list.
Research trail: `demo/rights_research.md`.

## Run it
```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env        # never sent to the browser
.venv/bin/uvicorn app.main:app --port 8766
# open http://localhost:8766
.venv/bin/python -m pytest -q                      # engines, validator, tools, screenshot, export
```

## Layout
```
app/main.py        FastAPI routes (session, message, screenshot + confirm/skip, plan, export, exit)
app/agent.py       Claude tool-use loop, system prompt (cached), turn rollback, reply validation
app/tools.py       11 tools Claude can call; all decisions via engines/validator
app/engines.py     simulator + hypothesize (pure functions)
app/validator.py   plan/finding/reply checks, region lookup
app/vision.py      one-shot screenshot extraction (structured output); image never stored
app/export.py      consent-gated caseworker summary (technical findings only)
app/data/          channels, playbook fixes, resources, rights (human-verified; see demo/*.md checklists)
app/static/        single-page UI (vanilla JS)
demo/              demo script, verification checklist, prepared screenshots
```

Model: `claude-sonnet-5-5` for the agent and vision, with server-side refusal fallback enabled.

## Out of scope
Stalkerware scanning (unreliable; impossible on iOS), reading settings automatically, making changes for
the user, stored accounts or conversations, and legal advice.
