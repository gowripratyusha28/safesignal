# SafeSignal — Tech-Safety Copilot (Hackathon Build Spec)

> Hand this file to Claude Code at the start of the hackathon. It contains the problem, the reasoning behind every design decision, the architecture, data formats, prompts, safety rules, build order, and demo script. Build in the order given in "Build plan". Working end-to-end beats feature-complete.
>
> "SafeSignal" is a placeholder name — rename freely.

---

## 1. Context

- **Event:** Code with Claude: Women in AI Hackathon (Anthropic, San Francisco). One-day build, pitch to Anthropic judges.
- **Track:** #2 Safety and rights — *"Laws and support services vary widely by place, and it can be hard to know what protections apply or where to turn. How might we help women and girls understand their rights and find the right support?"*
- **Builder background:** systems engineer (AWS EC2, IBM storage/SAN, Huawei NAS); built a multi-tenant GPU lease manager at USC (cgroups/PAM isolation, gRPC control plane). Access control is home turf.

## 2. The problem

Abusers often monitor and control partners through **ordinary technology**, not hacking: a shared Apple ID, Find My location sharing, an old iPad still signed in, a family phone plan they own, a recovery email they control.

Evidence (use one stat in the pitch, not all):
- A US survey of 72 domestic violence shelters: 85% of workers had helped victims tracked by GPS; NNEDV found 54% of abusers tracked survivors' phones with stalkerware (Citizen Lab, 2019).
- Cornell Tech field study: compromised accounts or exploitable misconfigurations found for 23 of 44 survivors.
- Expert help is scarce: Cornell's Clinic to End Tech Abuse (CETA), the best-known model, has handled ~700 referrals in six years, mostly in New York. Advocates often lack the training to trace how access chains across services.
- Survivors are often told they are "paranoid"; being believed matters (Refuge).

**Gap no existing tool fills:** Apple Safety Check is Apple-only; Refuge/NNEDV guides are generic step lists; DV chatbots (e.g. the Hotline's "Ruth") answer questions. None reasons across services about *how access chains together*, verifies it from the survivor's own screens, and produces a **detection-aware, dependency-ordered** plan.

## 3. What we are building

An AI copilot that does what a trained tech-safety advocate does in a clinic consultation:

1. **Listens** to the survivor's story ("he showed up at a café I only mentioned in a text to my sister").
2. **Forms hypotheses** about how the abuser is getting information.
3. **Asks for evidence** — a specific settings screenshot that distinguishes the hypotheses.
4. **Reads the screenshot** (Claude vision) and upgrades findings to *verified*.
5. **Produces a safe plan** from a vetted playbook, ordered correctly, with each step labelled by whether the abuser might notice.
6. **Connects to support** — region-appropriate hotlines and tech-safety resources (Track 2).
7. Optionally produces a **caseworker summary** (export only with explicit consent).

Primary user framing: **survivors and the advocates/caseworkers who support them.** The pitch emphasizes it supports advocates, never replaces them.

**Pitch line:** *"Claude runs the investigation like a tech-safety expert most survivors never get to see. Deterministic tools make sure every conclusion is verified and every recommendation is safe."*

## 4. Core design principle: Claude reasons, code decides

Modelled on the Built with Opus 4.7 winners (Wrench Board, MedKit):
- **Claude does what only an LLM can:** understand messy stories, run an adaptive interview, read screenshots, choose which evidence to ask for, explain results kindly in plain language (any language).
- **Deterministic code does what must be correct every time:** what each access channel exposes, ranking candidate causes, checking a plan closes every exposure, enforcing safety rules, and validating that Claude only references real fixes/resources.
- **Claude never invents a fix, a step, a phone number, or a resource.** It may only reference IDs that exist in `data/fixes.json` and `data/resources.json`. Unknown IDs are rejected by the validator (like Wrench Board's refusal to fabricate component IDs; MedKit's curated guideline registry).
- No model training. Everything is Claude via the API + prompts + tools + data files.

## 5. Failure modes we design against

1. **False accusation of monitoring.** A shared iCloud may *explain* what he knows but doesn't prove he's watching. → Every finding carries an evidence level: `reported` / `plausible` / `verified`. Language follows the level. Never say "he is reading your messages" unless verified. Also never dismiss: "nothing verified yet" ≠ "you're imagining it".
2. **A recommendation exposes the survivor.** Changing passwords, removing devices, or stopping sharing can be noticed and escalate danger. → Every fix has `may_notify_abuser`, `risk_note`, loss-of-access and evidence-loss notes. **Never execute changes automatically.** Survivor chooses. "Document first, then change."
3. **The assistant itself becomes a record of abuse.** Names, escape plans, children's info, locations. → Collect less (people are "Person A — former partner"), persist nothing by default, export only with explicit consent, encrypted.
4. **The abuser uses the tool.** → Only analyzes the user's *own* accounts/devices; produces defensive guidance only.
5. **The tool leaves traces on a compromised device.** → Quick-exit button, no history, recommend using a safe device; warn that screenshots saved on a compromised phone can sync to the abuser via shared iCloud Photos.
6. **Stale or wrong instructions.** Platform menus change. → Playbook entries are human-verified, dated, and cite a source; advocate review recommended.

## 6. Safety mode (asked first, before anything else)

First question: *"Are you still living with or in regular contact with this person?"*

- `safety_mode = "covert"` (yes / unsure): only fixes with `may_notify_abuser: false` are recommended as actionable. Detectable fixes are shown as "Discuss with an advocate before doing this," never as next steps. Emphasize documentation, a safe device, and support contacts.
- `safety_mode = "lockdown"` (has left / safe): full plan, still in dependency order.

Code enforces this, not the prompt alone.

## 6a. What the app checks

Menu paths are approximate — **verify each on a current iOS/Android device before the demo.** Each check maps to a channel in `data/channels.json`.

### iPhone / Apple ID (core)
| Check | Where to look | Exposes if he has access | Verified by | Channel id |
|---|---|---|---|---|
| Location sharing | Find My → People, or Settings → Privacy & Security → Safety Check → Manage Sharing & Access | Live location | Screenshot | `find_my_sharing` |
| Signed-in devices | Settings → [name] → device list | Messages, photos, notes, backups on an extra iPad/Mac | Screenshot | `signed_in_device` |
| Family Sharing | Settings → [name] → Family | Location within family; organizer control | Screenshot | `family_sharing` |
| Text forwarding | Settings → Messages → Text Message Forwarding | SMS on other devices | Screenshot | `sms_forwarding` |
| Recovery email / trusted phone | Settings → [name] → Sign-In & Security | Can reset her password even after she changes it | Screenshot + ask "is that email/number his?" | `recovery_control` |
| Shared items | Safety Check → Manage Sharing & Access | Shared albums, notes, Health data | Screenshot | (record as finding; optional channel) |
| Apple ID password | Not visible | Everything in iCloud | Interview ("Did he set up your phone? Does he know the password?") | `apple_id_password` |
| Phone passcode | Not visible | Everything, with physical access | Interview | `knows_passcode` |
| Apps with location access | Settings → Privacy & Security → Location Services (app list, look for "Always") | Live location via dual-use family-locator apps (e.g. Life360) installed openly | Screenshot | `locator_app` |
| Device management profiles | Settings → General → VPN & Device Management | A configuration profile can let someone monitor or control the phone | Screenshot | `mdm_profile` |

### Google / Android (if used)
| Check | Where to look | Exposes | Verified by | Channel id |
|---|---|---|---|---|
| Devices & recent sign-ins | myaccount.google.com → Security | Gmail, Photos, location history | Screenshot | `google_signed_in` |
| Maps location sharing | Google Maps → profile → Location sharing | Live location | Screenshot | `google_location_share` |
| Recovery email / phone | Google account → Security | Account reset | Screenshot | `recovery_control` |
| Family Link | Google account → Family | Parental-style controls | Screenshot | (optional channel) |

### Apps and accounts
| Check | Where to look | Exposes | Verified by | Channel id |
|---|---|---|---|---|
| WhatsApp linked devices | WhatsApp → Settings → Linked devices | Chats on his computer | Screenshot | `whatsapp_linked` |
| Phone plan owner | Interview: "Whose name is the plan in?" | Call/text logs (who and when, not content) | Interview | `carrier_account` |

### Deliberately not checked (future work — mention in pitch)
- Stalkerware scanning (unreliable; not possible on iOS) — refer to expert clinics.
- Physical trackers (AirTags etc.) — only mention the phone's built-in unknown-tracker alerts.
- Email forwarding rules (Gmail/Outlook), social media sessions and Snap Map, Screen Time set by someone else.
- Shared bank, streaming, shopping and cloud accounts — interview question only.
- Car apps, smart-home cameras and doorbells.
- Non-technical sources (mutual friends, family, social posts) — interview question only.

### Rule: unexplained observations → say so, refer to an expert
Checks are never complete. If `hypothesize` cannot explain an observation with any checked or active channel, it must return it under `unexplained`, and the app must **never** imply the survivor is now safe. Claude says, in substance: *"What you're describing isn't explained by what we've checked so far. It could be something outside this tool, like a physical tracker, someone you both know, or an app we didn't cover. Here's an expert who can help,"* and shows resources (e.g. a tech-abuse clinic or the hotline). This ties to failure mode #1: never dismiss, never over-claim.

### Demo subset (build these first)
1. Location sharing (Safety Check screenshot)
2. Signed-in devices (Apple ID device list screenshot)
3. Recovery email / trusted phone (Sign-In & Security screenshot)
4. Apple ID password (interview)
5. Phone plan owner (interview)
6. Apps with location access (Location Services screenshot) — P1
7. Device management profiles (VPN & Device Management screenshot) — P1

Everything else is P2 — the channels already exist in data, so adding a check later means adding a screen id, extraction handling, and its fixes.

## 7. Architecture

```
Browser (single page, vanilla HTML/JS)
   │  chat + screenshot upload + plan view + quick-exit
   ▼
FastAPI backend (Python 3.11+)
   ├── /api/session        start session (in-memory only)
   ├── /api/message        user turn → agent loop → reply
   ├── /api/screenshot     image upload → agent loop (vision)
   ├── /api/plan           current validated plan
   └── /api/export         caseworker summary (explicit consent only)
   │
   ├── agent.py            Claude tool-use loop
   ├── engines.py          simulator + hypothesize (NO LLM CALLS)
   ├── validator.py        enforces IDs + safety mode + evidence levels
   ├── data/channels.json  access channels and what each exposes
   ├── data/fixes.json     vetted playbook
   └── data/resources.json hotlines / tech-safety orgs by region
```

- **State:** in-memory dict keyed by session ID. No database. Session wiped on quick-exit or timeout.
- **Models:** use the current Claude Sonnet model for the agent loop and vision (check docs.claude.com for the current model string, e.g. `claude-sonnet-5-5`). Optionally Haiku for cheap classification steps. Enable prompt caching on the long system prompt.
- **Fallback:** if voice or anything fancy breaks, text chat must still work end to end.

## 8. Data model

### 8.1 Access channels — `data/channels.json`
Each channel is a way the abuser might have access, and what it exposes.

```json
[
  {"id": "apple_id_password",  "label": "Knows your Apple ID password",            "reveals": ["location","messages","photos","backups","notes"], "how_to_verify": "interview"},
  {"id": "find_my_sharing",    "label": "Location shared via Find My",              "reveals": ["location"],                     "how_to_verify": "screenshot:safety_check_people"},
  {"id": "family_sharing",     "label": "In your Apple Family Sharing group",       "reveals": ["location","purchases"],         "how_to_verify": "screenshot:family"},
  {"id": "signed_in_device",   "label": "Another device signed into your Apple ID", "reveals": ["messages","photos","notes","backups"], "how_to_verify": "screenshot:apple_id_devices"},
  {"id": "sms_forwarding",     "label": "Texts forwarded to another device",        "reveals": ["sms"],                          "how_to_verify": "screenshot:text_forwarding"},
  {"id": "recovery_control",   "label": "Controls your recovery email or phone",    "reveals": ["account_reset"],                "how_to_verify": "screenshot:sign_in_security"},
  {"id": "google_signed_in",   "label": "Unknown device on your Google account",    "reveals": ["email","location_history","photos"], "how_to_verify": "screenshot:google_devices"},
  {"id": "google_location_share","label": "Location shared in Google Maps",         "reveals": ["location"],                     "how_to_verify": "screenshot:google_maps_sharing"},
  {"id": "whatsapp_linked",    "label": "WhatsApp linked device",                   "reveals": ["whatsapp_messages"],            "how_to_verify": "screenshot:whatsapp_linked"},
  {"id": "carrier_account",    "label": "Owns your phone plan account",             "reveals": ["call_logs","sms_logs"],         "how_to_verify": "interview"},
  {"id": "knows_passcode",     "label": "Knows your phone passcode",                "reveals": ["everything_with_physical_access"], "how_to_verify": "interview"},
  {"id": "locator_app",        "label": "Family-locator app with location access",  "reveals": ["location"],                     "how_to_verify": "screenshot:location_services_apps"},
  {"id": "mdm_profile",        "label": "Device management profile installed",      "reveals": ["device_activity","settings_control"], "how_to_verify": "screenshot:vpn_device_management"}
]
```

Note: `recovery_control` is special — it lets the abuser **regain** any account after a password change. The simulator must treat it as re-enabling `apple_id_password` / Google access unless fixed first.

### 8.2 Playbook — `data/fixes.json`
Seed ~10 entries. **Every step and menu path must be human-verified** against Refuge Tech Safety guides, NNEDV Safety Net (techsafety.org), and Apple/Google support pages before the demo. Claude Code may draft; a human checks.

```json
[
  {
    "id": "document_evidence",
    "title": "Record what you found before changing anything",
    "platform": "any",
    "closes": [],
    "steps": ["Write down device names, people, and dates, or photograph the screen using a safe device."],
    "may_notify_abuser": false,
    "loses_access": false,
    "evidence_loss": false,
    "risk_note": "Safe. Preserves proof that may support a protective order.",
    "prerequisites": [],
    "source": "Coalition Against Stalkerware / NNEDV",
    "verified_on": "YYYY-MM-DD"
  },
  {
    "id": "fix_recovery_email",
    "title": "Change your Apple ID recovery email and trusted phone number",
    "platform": "iPhone",
    "closes": ["recovery_control"],
    "steps": ["Settings → [your name] → Sign-In & Security → review email addresses and trusted phone numbers."],
    "may_notify_abuser": true,
    "loses_access": false,
    "evidence_loss": false,
    "risk_note": "If he controls the old email or number, he may see a notification.",
    "prerequisites": ["document_evidence"],
    "source": "Apple Support / Refuge",
    "verified_on": "YYYY-MM-DD"
  },
  {
    "id": "change_apple_id_password",
    "title": "Change your Apple ID password from a safe device",
    "platform": "iPhone",
    "closes": ["apple_id_password"],
    "steps": ["Use a safe device. Settings → [your name] → Sign-In & Security → Change Password."],
    "may_notify_abuser": true,
    "loses_access": false,
    "evidence_loss": false,
    "risk_note": "Other devices may be signed out, which he may notice.",
    "prerequisites": ["fix_recovery_email"],
    "source": "Apple Support",
    "verified_on": "YYYY-MM-DD"
  },
  {
    "id": "remove_unknown_device",
    "title": "Remove an unknown device from your Apple ID",
    "platform": "iPhone",
    "closes": ["signed_in_device"],
    "steps": ["Settings → [your name] → scroll to the device list → tap the device → Remove from Account."],
    "may_notify_abuser": true,
    "loses_access": false,
    "evidence_loss": true,
    "risk_note": "The device will be signed out, which he may notice. Document it first.",
    "prerequisites": ["document_evidence", "change_apple_id_password"],
    "source": "Apple Support",
    "verified_on": "YYYY-MM-DD"
  },
  {
    "id": "stop_find_my_sharing",
    "title": "Stop sharing your location in Find My",
    "platform": "iPhone",
    "closes": ["find_my_sharing"],
    "steps": ["Find My → People → select the person → Stop Sharing My Location. Or Safety Check → Manage Sharing & Access."],
    "may_notify_abuser": true,
    "loses_access": false,
    "evidence_loss": false,
    "risk_note": "He will likely notice your location is no longer visible.",
    "prerequisites": ["document_evidence"],
    "source": "Apple Support / NNEDV",
    "verified_on": "YYYY-MM-DD"
  },
  {
    "id": "use_safe_device",
    "title": "Use a safe device for sensitive communication",
    "platform": "any",
    "closes": [],
    "steps": ["Use a device he has never had access to (a library computer, a trusted friend's phone, or a new phone) to contact support or research options."],
    "may_notify_abuser": false,
    "loses_access": false,
    "evidence_loss": false,
    "risk_note": "Safe. Doesn't change anything he can see.",
    "prerequisites": [],
    "source": "NNEDV Safety Net",
    "verified_on": "YYYY-MM-DD"
  }
]
```

Add similar entries for: `disable_sms_forwarding`, `leave_family_sharing`, `google_remove_device`, `google_stop_location_share`, `whatsapp_unlink_devices`, `carrier_own_account` (contact carrier / Safe Connections Act line separation — verify details), `change_passcode`, `review_locator_apps` (closes `locator_app`; removing or limiting an app's location access may notify), `remove_mdm_profile` (closes `mdm_profile`; may notify and may affect a legitimate work profile — talk to an advocate or IT first).

### 8.3 Resources — `data/resources.json`
Verify every number and URL on the organization's own site before the demo.

```json
[
  {"id": "us_ndvh",        "name": "National Domestic Violence Hotline", "region": "US", "contact": "1-800-799-7233 / thehotline.org", "helps_with": ["safety planning","local shelters","chat support"]},
  {"id": "nnedv_safetynet","name": "NNEDV Safety Net — Tech Safety",     "region": "US", "contact": "techsafety.org",                    "helps_with": ["tech abuse guides","safety planning"]},
  {"id": "cornell_ceta",   "name": "Clinic to End Tech Abuse (Cornell Tech)", "region": "US-NY", "contact": "ceta.tech.cornell.edu (referral via NYC Family Justice Centers)", "helps_with": ["expert tech consultation"]},
  {"id": "uk_refuge_tech", "name": "Refuge Tech Safety",                 "region": "UK", "contact": "refugetechsafety.org",              "helps_with": ["device guides","interactive tool"]}
]
```

Region lookup: user enters country (and US state optionally). Show region-specific entries first, then national ones. (Optional, Track 2: a small `rights` field per region summarizing protective-order basics with an official source link — only if time and only from official sources.)

## 9. Deterministic engines — `engines.py` (NO LLM CALLS)

### 9.1 Simulator (forward): "what can he see?"
```python
def exposed(active_channels: set[str]) -> set[str]:
    """Union of everything revealed by active channels.
    If recovery_control is active, account-reset re-enables apple_id_password
    and google access even after a password change."""

def simulate_plan(active_channels: set[str], fix_ids: list[str]) -> dict:
    """Apply fixes in order (respecting prerequisites).
    Return {"remaining_channels": [...], "still_exposed": [...],
            "order_problems": [...]}  # e.g. password changed before recovery fixed
    """
```

### 9.2 Hypothesize (backward): "how is he finding out?"
```python
def hypothesize(observed: set[str], ruled_out: set[str] = set()) -> list[dict]:
    """Input: what he seems to know, e.g. {"location", "messages"}.
    Score every channel and pairs of channels:
      hits  = |reveals ∩ observed|          (explains observations)
      extra = |reveals − observed|          (predicts things he hasn't shown — small penalty)
    Return ranked candidates with: channels, explains, unexplained, score,
    and best_check = the screenshot that would best distinguish the top candidates
    (from channels[].how_to_verify).
    Also return a top-level "unexplained": observations that NO channel (checked,
    active, or still possible) can explain. If non-empty, the agent must refer to
    an expert and never imply the survivor is safe."""
```

Unit-test both engines (pytest). These tests are part of the demo story: "the diagnosis is deterministic and tested."

## 10. Agent — `agent.py` (Claude tool-use loop)

### Tools exposed to Claude
| Tool | Purpose |
|---|---|
| `set_safety_mode(mode)` | Record covert/lockdown from the first answer |
| `record_observation(knowledge, evidence)` | What the abuser seems to know, with the survivor's words |
| `record_finding(channel_id, evidence_level, basis)` | Add/upgrade a finding (`reported`/`plausible`/`verified`) |
| `hypothesize(observed)` | Calls the engine; returns ranked causes + best_check |
| `request_screenshot(screen_id, instructions)` | Ask the user for a specific screen (UI shows upload box) |
| `get_fix(fix_id)` | Returns the fix or `{found: false, closest_matches: [...]}` |
| `simulate_plan(fix_ids)` | Calls the engine; checks the plan closes everything |
| `get_resources(region)` | Region-appropriate support |
| `propose_plan(fix_ids, notes)` | Final plan → goes through validator before display |

Loop: user message → Claude (with tools) → execute tool calls → feed results back → repeat until Claude returns a user-facing reply. Cap iterations (e.g. 8).

### Screenshot reading
Claude reads the image directly (vision). Use this extraction instruction inside the agent when an image arrives:
```
Extract only what is visible in this screenshot. Return JSON:
{"screen": "...", "devices": [...], "people_sharing": [{"name": "...", "what": "..."}],
 "settings": [{"name": "...", "state": "..."}], "uncertain": [...], "need_more": "..."}
Do not guess. If text is unreadable, blurry, or a list is cut off, say so in
"uncertain" or "need_more".
```
Then show extracted items to the user for confirmation ("I see: iPhone, MacBook Air, 'Home iPad'. Is that right?") before upgrading anything to `verified`.

Screenshot safety: before the first request, tell the user that screenshots saved on a possibly compromised phone can sync via shared iCloud Photos; recommend photographing the screen with a safe device or checking account.apple.com / myaccount.google.com from a safe computer.

### System prompt (starting point)
```
You are a trauma-informed tech-safety advocate helping someone who may be experiencing
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
```

## 11. Validator — `validator.py`
Runs on every `propose_plan` and every rendered reply that references fixes:
1. Every `fix_id` and `resource_id` exists in the data files; otherwise reject and return closest matches to Claude.
2. In `covert` mode, fixes with `may_notify_abuser: true` are moved to a "discuss with an advocate first" section, never shown as actionable steps.
3. Prerequisites are satisfied and order is valid (e.g. `fix_recovery_email` before `change_apple_id_password`); if not, reorder or reject.
4. `document_evidence` appears before any fix with `evidence_loss: true`.
5. Findings shown as "verified" must have a confirmed screenshot basis.
6. Output text is scanned for phone numbers / URLs not present in `resources.json`; unverified ones are stripped and flagged.
7. If the latest `hypothesize` result has non-empty `unexplained`, the rendered plan must include the "not explained by what we checked" notice and at least one expert resource, and must not contain wording like "you're safe" or "all clear".

Unit-test every rule.

## 12. UI (single page)

- **Header:** app name + always-visible **Quick Exit** button (clears session, replaces page with a neutral site like a weather page, no back-history if possible).
- **Left: conversation** with Claude; screenshot upload appears inline when requested.
- **Right: live panel**
  - Safety mode badge (Covert / Lockdown)
  - Findings list, each with an evidence-level chip: Reported · Plausible · Verified
  - "What may be exposed" (from simulator)
  - Plan: ordered steps, each labelled **Safe now** or **May notify him — talk to an advocate first**, with risk notes and source
  - Support: region resources
- **Export (optional):** caseworker summary, only after an explicit consent checkbox; warns not to save to Downloads/shared cloud/shared email. Summary contains technical findings only — no narrative, no plans.
- No accounts, no localStorage of conversation, no analytics.

## 13. Demo script (2–3 minutes)

Prepare beforehand: a test iPhone/Apple ID that shares location with a contact named "Alex" and has an extra signed-in device. Take screenshots of Safety Check → Manage Sharing & Access and the Apple ID device list. Blur real names/emails.

1. Survivor (fictional persona): "I left him two weeks ago but he showed up at a café I'd only mentioned in a text to my sister. And he always seems to know where I am."
2. App asks safety question → "I've left" → Lockdown mode.
3. Claude calls hypothesize → top candidates: Find My sharing + signed-in device / shared Apple ID. Asks for the Safety Check screenshot (with the safe-device warning).
4. Upload → Claude reads it: "Your location is shared with 'Alex'. An iPad named 'Home iPad' is signed into your account." User confirms → **Verified**.
5. Claude asks one follow-up: "Is the recovery email on your Apple ID one he can access?" → "It's an email he set up."
6. Simulator: removing the iPad alone isn't enough — recovery control would let him regain access. Plan reorders: document → fix recovery email → change password → remove device → stop sharing.
7. Show the same case in **Covert mode**: detectable steps move to "talk to an advocate first"; plan becomes document + safe device + hotline.
8. Support panel shows hotline + tech-safety resources for the region.
9. Close with the pitch line and the safety design (evidence levels, playbook-only fixes, no persistence, quick exit).

## 14. Build plan (priority order — stop adding features when time is short)

**Hour 0–1:** repo setup; `CLAUDE.md`; data files with seed entries; FastAPI skeleton; single HTML page with chat.
**Hour 1–3 (P0 — must work):** agent loop with tools; engines + tests; validator + tests; plan panel.
**Hour 3–4 (P0):** screenshot upload + vision extraction + confirmation; evidence-level chips.
**Hour 4–5 (P1):** safety mode enforcement end-to-end; resources panel by region; quick exit.
**Hour 5–6 (P2, only if P0/P1 solid):** caseworker export with consent; multilingual replies (global / low-resource angle — Claude can respond in the user's language); polish.
**Last hour:** rehearse the demo with prepared screenshots; record a backup video of a successful run.

## 15. Out of scope (say so in the pitch if asked)
- **Scanning phones for stalkerware.** Research (Chatterjee et al.) found anti-spyware tools fail to reliably detect IPV-relevant apps (one had a 12% false-positive rate); iOS doesn't allow it. We refer spyware concerns to expert clinics; Cornell's open-source ISDi could plug in later as another evidence source.
- Reading device settings automatically (not possible on iOS by design; screenshots instead).
- Making any changes on the user's behalf.
- Persistent accounts or stored conversations.
- Legal advice — the app shows resources and official information only.

## 16. Judging angles to emphasize
- **Real problem, real gap:** expert tech-abuse help barely exists outside a few clinics.
- **Strong use of Claude:** agentic investigation, vision on real screens, adaptive interview, multilingual explanation.
- **Engineering judgment:** deterministic diagnosis, playbook-only fixes with a validator, evidence levels, safety mode, no persistence — designed against six named failure modes.
- **Track fit:** helps women understand what's exposed and find the right support where they live.
- **Builder fit:** an access-control engineer applying that expertise to people whose access is being turned against them.
