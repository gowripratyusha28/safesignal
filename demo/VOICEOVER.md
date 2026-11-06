# Voice-over notes (≈3½ minutes)

Four parts the video must cover: **Problem → What we built → Why we built it this way → User experience.**
Read at a calm pace. Cues in **[brackets]** say what should be on screen; typed lines are in `demo/DEMO_LINES.md`.

---

## 1. Problem statement  (≈35 s)

**[Landing page, or a title slide]**

Abusers rarely hack. They use ordinary technology: a shared Apple ID, an old iPad still signed in, a family phone plan, a recovery email they set up years ago. One study found exploitable account access for twenty-three of forty-four survivors it examined. Survivors are often told they're paranoid.

The experts who can trace this barely exist. Cornell's tech-abuse clinic, the best-known model, has seen about seven hundred people in six years, mostly in New York. Most advocates say they don't feel confident with tech abuse.

And the chatbots filling that gap aren't safe. A USENIX Security audit this year found they gave unsafe or incomplete advice eighty-six percent of the time, left out critical safety warnings in sixty percent, and could be talked into helping an abuser about two-thirds of the time.

## 2. What we built  (≈30 s)

**[App header; the side panel visible]**

SafeSignal is a tech-safety copilot. It does what a trained advocate does in a clinic consultation: listens to the survivor's story, works out how the abuser could be getting information, asks for the one settings screenshot that settles it, reads that screenshot, and builds a plan that's safe to carry out, in the right order. Then it connects her to hotlines and her legal rights for where she lives.

The principle behind it: Claude reasons, code decides. Claude runs the interview and reads the screens. Deterministic, tested code decides what counts as verified, which steps are safe, and what order they go in.

## 3. Why we built it this way  (≈35 s)

**[Show "Under the hood" and "What this tool can't do" in the panel]**

We designed against the exact failures that audit found.

Chatbots tell survivors to change a password when the abuser controls the recovery email; our simulator catches that and reorders the plan. They don't warn that a change can alert the abuser; every step here is labelled "safe now" or "may notify them," and in covert mode the risky ones are never shown as next steps. They skip evidence; here, documenting comes first, in code. They invent fixes and phone numbers; ours can only show entries from a vetted playbook with sources, and the validator rejects anything else. They can be turned against survivors; we red-teamed ours against the pretexts abusers use, and ten out of ten were refused.

And nothing is stored: no accounts, no history, screenshots read once and discarded, a quick-exit button, and a plain list of what the tool can't do.

## 4. User experience: the walkthrough  (≈1 min 45 s)

**[Click into the chat; step 1]**
The first question is always safety: are you still in contact with this person? That answer sets the mode in code and changes everything the app is allowed to suggest.

**[Step 2: iPhone, New York]**
She says where she is. The support panel fills with vetted hotlines for her region, and "Your rights" appears: short facts from official sources only, labelled as information, not legal advice.

**[Step 3: the café story; open "Under the hood"]**
He showed up at a café she'd only mentioned in a text to her sister. Claude turns that into two observations, location and messages. The engine ranks every way he could know, scores them, and picks the one screenshot that best tells the top explanations apart. Code chose the screenshot, not the model.

**[Steps 4–5: upload, confirm card]**
She uploads the screen. The image is read once and thrown away; it never enters the conversation. The app shows her what it read, and only her click can confirm it.

**[Step 6: "only the iPhone is mine"]**
Two devices she doesn't own are signed into her account. The finding becomes "verified." Notice it still won't say *he* is reading her messages. Every finding carries an evidence level, so the app explains without accusing.

**[Step 7: password and recovery email]**
He set up her phone and controls the recovery email. That's the trap: change the password first and he simply resets it.

**[Step 8: plan appears; tap a step]**
So the plan comes out in dependency order: document, safe device, fix the recovery email, then change the password, then remove his devices. Each step shows whether he might notice, the risk, and the source.

**[Step 9: custody handoffs]**
Now she says she still has to see him twice a week. The mode flips to covert, and every step he could notice moves under "talk to an advocate first." Same findings, different plan, enforced in code.

**[Step 10: "is this illegal?"]**
She asks if what he's doing is illegal. Claude answers only from the rights list for her region.

**[Steps 11–12: summary, Quick Exit]**
With her consent, a caseworker summary: technical findings only, no story, no names, never saved. And one click, and she's on a weather page.

## Closing  (≈15 s)

**[Landing page or closing slide]**

SafeSignal supports advocates; it doesn't replace them. Claude runs the investigation like the expert most survivors never get to see, and code makes sure every conclusion is verified and every recommendation is safe.
