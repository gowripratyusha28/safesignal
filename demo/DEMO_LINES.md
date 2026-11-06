# Demo: copy-paste lines

Keep this file and the `demo/screenshots/` folder open. Each box is one message; copy the whole box.
Server: `.venv/bin/uvicorn app.main:app --port 8766` (no --reload) → http://localhost:8766 → start the chat in a fresh window.

---

**1.** Page loads. Claude asks if you still live with / contact him. Send:

```
I left him two weeks ago and we have no contact at all.
```
→ Badge: Lockdown

**2.** Send:

```
I have an iPhone. I'm in New York, US.
```
→ Support list fills; "Your rights (11)" appears in the panel

**3.** Send:

```
He showed up at a café I'd only mentioned in a text to my sister. He always seems to know where I am.
```
→ Upload box appears. Open "Under the hood" and show the `hypothesize` line.

**4.** UPLOAD the screenshot that matches what Claude asked for, then click **Send screenshot**:

| If Claude says… | Upload |
|---|---|
| "Settings → your name → devices" / Apple Account / device list | `apple_id_devices.png` |
| "Safety Check" / "Manage Sharing & Access" / "Find My → People" | `safety_check_people.png` |
| "Sign-In & Security" | `sign_in_security.png` |
| "Location Services" | `location_services_apps.png` |
| "Family" / "Family Sharing" | `family.png` |
| "Text Message Forwarding" | `text_forwarding.png` |
| "VPN & Device Management" | `vpn_device_management.png` |

**5.** Click **Yes, that's right**.

**6.** Send the line that matches the screenshot you uploaded:

If `apple_id_devices.png`:
```
Only the iPhone is mine. I've never had an iPad or a MacBook. He has a MacBook.
```
If `safety_check_people.png`:
```
Alex is him. I didn't know I was still sharing my location with him.
```
If `location_services_apps.png`:
```
FamilyLocate is an app he installed when we were together. I never use it.
```
If `family.png`:
```
Alex is him. He set up Family Sharing when we were together.
```
→ Finding chip turns **verified**

**7.** Send:

```
He set up my phone and probably still knows my Apple ID password. The recovery email on it is one he created.
```
→ Two "reported" findings. If Claude asks for the Sign-In & Security screen instead: upload `sign_in_security.png`, click **Yes, that's right**, then send:
```
Yes, alex.m.1988 is his email.
```

**8.** If Claude asks anything else (passcode, other devices), send:

```
No, he doesn't know my passcode. Can you show me a plan now?
```
→ Plan appears in order: Record → Safe device → Fix recovery email → Change password → Remove device. Tap a step.

**9.** Send:

```
Actually, I still have to see him twice a week for custody handoffs.
```
→ Badge flips to **Covert**; steps move under "Talk to an advocate before doing these"; trace shows `set_safety_mode` + `validator`.

**10.** Send:

```
Is what he's doing even illegal?
```
→ Claude answers from the rights list, "official information, not legal advice".

**11.** Panel: tick the consent box → **Show summary** → **Close**.

**12.** Click **Quick Exit** (or press Esc twice).

---

## If something goes wrong

| Problem | Do |
|---|---|
| Claude asks an extra question | Answer it in one short sentence, then continue. |
| No plan after step 8 | Send: `Please put the plan together.` |
| Claude asks for a second screenshot you don't want to do | Click **Not now**, then send: `I can't take that one. What can I do?` |
| Red "Something went wrong" bubble | The turn rolled back. Send the same line again. |
| No upload box at step 3 | Send: `What should I check first?` |
| Internet/API down | Backup video. |

## Closing line

"This year's USENIX Security audit found DV chatbots give unsafe advice 86% of the time and help abusers two-thirds of the time. We red-teamed ours against the same pretexts: 10 of 10 refused. Claude runs the investigation like the tech-safety expert most survivors never get to see; deterministic code makes sure every conclusion is verified and every recommendation is safe."
