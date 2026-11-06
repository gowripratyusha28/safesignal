# Demo script (2–3 minutes)

Matches what the app actually does as of the last browser check. Persona is fictional.

## Before you go on stage
- [ ] `.venv/bin/uvicorn app.main:app --port 8766`, open http://localhost:8766 in a **fresh** window.
- [ ] Real screenshot ready in `demo/screenshots/` (Apple Account device list showing an extra
      "Home iPad" or similar, names and emails blurred). Fallback: the fictional mock
      `demo/screenshots/mock_devices_fictional.png`.
- [ ] Demo-subset entries in `app/data/fixes.json` checked on the phone and `verified_on` set.
- [ ] Backup video recorded.
- [ ] Zoom the browser so the side panel is readable from the back of the room.

## Lockdown run (main demo)

| # | You type / do | What to point at |
|---|---|---|
| 1 | Page loads; Claude asks the safety question. | "First question is always safety: are you still in contact?" |
| 2 | `I left him two weeks ago and we have no contact at all.` | Badge turns **Lockdown**. |
| 3 | `I have an iPhone, I'm in the US.` | Support panel fills with US resources from the vetted list. |
| 4 | `He showed up at a café I'd only mentioned in a text to my sister. He always seems to know where I am.` | Claude records two observations (location + messages) and runs the **deterministic** hypothesis engine. It asks for the **Apple ID device list**, the screen that best splits the top explanations, and warns about iCloud Photos sync. |
| 5 | Upload the screenshot. | The confirm card lists exactly what was read. "The image is never stored. Only this reading is kept, and only your click can confirm it." |
| 6 | Click **Yes, that's right**. | |
| 7 | `Only the iPhone is mine. I've never had an iPad or a MacBook. He has a MacBook.` | Finding turns **verified**. Claude still says it can't be sure *he* is using them: evidence levels prevent false accusations. |
| 8 | `He set up my phone and probably still knows my Apple ID password. The recovery email is one he created.` | Two **reported** findings. Recovery control is special: he could reset the password after she changes it. |
| 9 | If Claude asks about the passcode: `No, I changed my passcode. Can you show me a plan?` | Plan appears: **document → safe device → fix recovery email → change password → remove device**. "If she'd removed the iPad first, the simulator shows he'd just get back in through the recovery email. Code reorders it, not the model." |

## Covert contrast (30 seconds)
Open a new window (or Quick Exit and reload):
1. `I still live with him.` → badge **Covert**.
2. `iPhone, I'm in the UK.`
3. `He always knows where I am. He set up my phone and knows my Apple ID password. I can't take screenshots safely. What can I do safely?`
4. Point at the panel: only **document** and **safe device** are "Safe now"; everything else is under
   **"Talk to an advocate before doing these"**. UK resources (0808 2000 247, Refuge Tech Safety, 999).
   "Same diagnosis, different plan. The safety mode is enforced in code, not left to the prompt."

## Close (pick 2–3)
- **Caseworker summary:** tick consent → Show summary. Technical findings only; no story, no names.
- **Quick Exit:** one click (or Esc twice) wipes the server session and replaces the page with weather.com.
- Pitch line: *"Claude runs the investigation like a tech-safety expert most survivors never get to
  see. Deterministic tools make sure every conclusion is verified and every recommendation is safe."*

## If something goes wrong on stage
- **Claude asks an extra question:** answer it naturally; the flow adapts.
- **No plan after step 9:** type `Please put the plan together.`
- **Error message in chat:** the turn rolled back safely; send the same line again.
- **Network down:** switch to the backup video.

## Likely judge questions
- *Why not scan for stalkerware?* Unreliable (anti-spyware tools miss IPV apps) and impossible on iOS.
  We refer to expert clinics. Cornell's ISDi could plug in as another evidence source.
- *What stops Claude inventing a fix or a hotline?* The validator: unknown IDs are rejected with closest
  matches, and phone numbers and URLs not in the vetted data are stripped from replies. Tests prove it.
- *What if the abuser uses it?* It only analyses your own accounts and gives defensive steps.
- *What's stored?* Nothing. In-memory sessions, a 30-minute timeout, no logs of content, and screenshots
  are discarded after reading.
- *Are the menu paths right?* Every entry has an official source URL and a verified date; entries not yet
  checked on a device say so in the panel.
