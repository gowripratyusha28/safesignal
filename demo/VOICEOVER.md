# Voice-over notes (≈3 minutes)

Read at a calm pace. Cues in **[brackets]** say what should be on screen; the typed lines are in `demo/DEMO_LINES.md`.

---

**[Landing page]**

Abusers rarely hack. They use ordinary technology: a shared Apple ID, an old iPad still signed in, a recovery email they set up years ago. Survivors are often told they're paranoid. The experts who can trace this, like Cornell's tech abuse clinic, have seen about seven hundred people in six years, mostly in New York.

And the chatbots filling that gap aren't safe. A USENIX Security audit this year found they gave unsafe or incomplete advice eighty-six percent of the time, and could be talked into helping an abuser about two-thirds of the time.

This is SafeSignal. Claude runs the investigation like a tech-safety advocate. Deterministic code decides what's verified and what's safe to recommend.

**[Click into the chat; step 1]**

The first question is always safety: are you still in contact with this person? That answer sets the mode in code, and it changes everything the app is allowed to suggest.

**[Step 2: iPhone, New York]**

She says where she is. The support panel fills with vetted hotlines for her region, and a "Your rights" section appears: short facts from official sources only. Official information, never legal advice.

**[Step 3: the café story]**

Now the story. He showed up at a café she'd only mentioned in a text to her sister.

**[Open "Under the hood"]**

Claude turns that into two observations: he knows her location, and he's seen her messages. Then this deterministic engine ranks every way he could know, scores them, and picks the one screenshot that best tells the top explanations apart. Claude didn't choose the screenshot. Code did.

**[Step 4–5: upload, confirm card]**

She uploads the screen. The image is read once and thrown away; it never enters the conversation. The app shows her exactly what it read, and only her click can confirm it.

**[Step 6: "only the iPhone is mine"]**

Two devices she doesn't own are signed into her account. The finding becomes "verified." Notice the wording: the app still won't say *he* is reading her messages. Every finding carries an evidence level, so a shared account can explain what he knows without the app accusing anyone.

**[Step 7: password and recovery email]**

He set up her phone and controls the recovery email. That's the trap most advice misses: change the password first and he simply resets it.

**[Step 8: plan appears]**

So the plan comes out in dependency order: document first, use a safe device, fix the recovery email, then change the password, then remove his devices. Every step comes from a vetted playbook with a source. Claude can't invent a step, a menu path, or a phone number; the validator rejects anything that isn't in the data.

**[Tap a step]**

Each step says whether he might notice, and what it costs her.

**[Step 9: custody handoffs]**

Now she says she still has to see him twice a week. Watch the panel. The mode flips to covert, and every step he could notice moves under "talk to an advocate first." Same findings, different plan, enforced in code, not left to a prompt.

**[Step 10: "is this illegal?"]**

She asks if what he's doing is illegal. Claude answers only from the rights list for her region, labelled as not legal advice.

**[Step 11–12: summary, Quick Exit]**

With her consent, a caseworker summary: technical findings only, no story, no names, never saved. And one click, or two taps of Escape, and she's on a weather page.

**[Closing, back on the landing page or a slide]**

We red-teamed it against the pretexts abusers actually use: custody, "she consented," "it's for a novel." Ten out of ten refused.

Nothing is stored. Every recommendation is from a vetted playbook. Every conclusion has an evidence level. Claude runs the investigation like the expert most survivors never get to see, and code makes sure it's safe.
