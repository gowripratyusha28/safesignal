# CLAUDE.md — standing instructions for this repo

Read `spec.md` first. It is the source of truth for the problem, design reasoning, data formats, prompts, safety rules, and build order.

## Non-negotiable rules
1. **Claude reasons, code decides.** `engines.py` (simulator, hypothesize) and `validator.py` must never call an LLM.
2. **No invented content.** The app may only show fixes from `data/fixes.json` and resources from `data/resources.json`. Unknown IDs return `{found: false, closest_matches: [...]}`.
3. **Safety mode is enforced in code.** In `covert` mode, fixes with `may_notify_abuser: true` are never shown as actionable steps.
4. **Never perform changes for the user.** Only explain options and risks.
5. **No persistence.** In-memory session state only. No database, no logs of conversation content, no localStorage of chat. Quick Exit wipes the session.
6. **Collect less.** Never prompt for names, addresses, children's details, or escape plans.
7. **Evidence levels everywhere:** `reported` / `plausible` / `verified`. "Verified" requires a user-confirmed screenshot finding.
8. Data files contain human-verified content. When drafting new playbook entries, mark `verified_on` as `"UNVERIFIED"` until a human checks the source.

## Stack
- Python 3.11+, FastAPI, Anthropic Python SDK, pytest.
- Frontend: one `index.html` with vanilla JS/CSS. No framework.
- API key from `ANTHROPIC_API_KEY` env var; never sent to the browser.
- Use the current Claude Sonnet model for the agent and vision (check docs.claude.com for the model string). Enable prompt caching on the system prompt.

## Workflow
- Build in the priority order in `spec.md` §14. Get the end-to-end text flow working before screenshots, and screenshots before polish.
- Write tests for `engines.py` and `validator.py` as you build them; run `pytest` after every change to those files.
- Keep a text-only fallback working at all times.
- Commit after each working milestone.

## Layout
```
app/
  main.py         FastAPI routes
  agent.py        Claude tool-use loop + system prompt
  engines.py      simulator + hypothesize (pure functions)
  validator.py    plan/output checks
  data/channels.json
  data/fixes.json
  data/resources.json
  static/index.html
tests/
  test_engines.py
  test_validator.py
demo/
  screenshots/    prepared demo screenshots (blurred, fake names)
```
