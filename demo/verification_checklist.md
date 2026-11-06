# Verification checklist: resources.json and fixes.json

Prepared 2026-11-06 as research prep for the final human check on a real iPhone. **No data files were edited.** Every URL below was fetched during this research. Where a page couldn't be fetched, or didn't say something, the entry is marked ❓.

## Summary

| | Count |
|---|---|
| Entries checked | 23 (7 resources + 16 fixes) |
| ✅ Match official source (at most minor wording or URL notes) | 11 (6 resources, 5 fixes) |
| ⚠️ Change suggested | 12 (1 resource, 11 fixes) |
| ❓ Couldn't confirm a specific claim | several, noted inside entries (see list below) |

### Safety-critical findings (fix before demo)
1. **change_passcode: missing step "Expire Previous Passcode".** Apple: after a change, "you can use your old passcode to reset your passcode for 72 hours." An abuser who knows the old passcode could reset the new one. Add: Face ID & Passcode → **Expire Previous Passcode**.
2. **google_fix_recovery: 7-day window.** Google: "If you change your recovery info or other authentication factors, Google may send codes to your previous info for 7 days." An abuser who controls the old recovery phone or email can still receive codes for a week. Add this to `risk_note`.
3. **document_evidence (may_notify_abuser=false):** the flag is OK only if the evidence is captured and **stored** away from devices or accounts the abuser can reach. NNEDV warns that some apps "notify the other person if you take a screenshot", and that if the abuser can access the device you should "store the screenshot somewhere else". Apple saves screenshots to Photos, which may sync through iCloud. The current step ("Write down…") doesn't say where. Suggested wording is in the entry. The flag can stay `false` only with the step reworded.
4. **cornell_ceta: referral path is incomplete.** Referrals come from NYC Family Justice Centers **or the Anti-Violence Project (AVP)**. The clinic serves NYC only, clients must be 18+, and there is no self-referral. Don't show it as something a user can contact directly.
5. **carrier_own_account: `may_notify_abuser: true` is confirmed correct.** In the FCC order, the carrier must tell the survivor "the date on which the covered provider intends to give any formal notice to the primary account holder." So the account holder **is** notified, on a date the survivor is told in advance. The FCC also says carriers must lock the account (no SIM changes, ports or cancellations) while the request is processed.
6. **No phone numbers were wrong.** 911, 1-800-799-7233, 999 and 0808 2000 247 all match the organisations' own sites.
7. **No `may_notify_abuser: false` flag was found that should be `true`**, apart from the caveat on document_evidence (item 3). All the device and account changes are already `true`.

### Couldn't confirm (❓)
- Apple doesn't say whether the **Family Sharing organizer** is notified when a member leaves, or whether a **removed Apple device** or a **logged-out WhatsApp device** shows a message. Keeping `true` is the conservative choice. Check on the device.
- Apple's own pages conflict on **Find My**. One says "won't be notified" (support.apple.com/en-us/105104). The personal-safety guide says people "may notice", and on older OSes may get a Messages notification. Keep `true`.
- The **"Remove Management"** button label for MDM enrollment (as opposed to "Delete Profile") is mentioned in a search snippet, but I couldn't fetch an Apple page that shows it.
- **Google Maps in-app** stop-sharing steps: Google's help page only documents the web route and the Android Settings route.
- **Family-locator apps** (e.g. Life360) notifying other members: there's no allowed official source. Third-party app sites were out of scope.
- **FCC pages on fcc.gov returned HTTP 403.** I used the FCC's circulated draft Report and Order (docs.fcc.gov, Oct 2023, FCC-CIRC2311-02). Ask the human to confirm that ¶77 matches the final adopted order (FCC 23-96).
- **iOS version:** Apple's iPhone User Guide version picker now lists **iOS 27**. The personal-safety guide pages don't state a version. Check every Apple path on the demo phone's actual iOS.
- Several Apple User Guide pages (iPhone 2FA, Safety Check in the iPhone guide) were truncated when fetched, so their body text wasn't seen.

---

# Resources (resources.json)

## us_emergency: Emergency services (US)
- **Status:** ✅ matches source
- **Current:** `911`
- **Suggested:** no change
- **Source:** https://www.thehotline.org/get-help/
- **Quote:** "Please contact 911 if you feel like you are in immediate danger or a life-threatening situation."
- [ ] human checked on device

## us_ndvh: National Domestic Violence Hotline
- **Status:** ✅ matches source (optional addition)
- **Current:** `1-800-799-7233 / thehotline.org`
- **Digit check:** 1-8-0-0-7-9-9-7-2-3-3. The site shows "1.800.799.SAFE (7233)". ✅
- **Suggested (optional):** add `Text START to 88788`. `helps_with` "chat support" is correct: the site has "Chat live now". It also lists a video phone for Deaf/hard-of-hearing callers: 855.812.1001.
- **Sources:** https://www.thehotline.org/ , https://www.thehotline.org/get-help/
- **Quote:** "Text "START" to 88788"
- **Note:** a web-search summary attributed "1-888-799-SAFE" to an FCC PDF. I couldn't fetch that PDF (403), and the hotline's own site says **1-800**. Keep 1-800.
- [ ] human checked on device

## nnedv_safetynet: NNEDV Safety Net (Tech Safety)
- **Status:** ✅ matches source
- **Current:** `techsafety.org`
- **Suggested:** no change. Safety Net offers information and training, not direct one-to-one help. Its "Get Help" page refers users to national hotlines. `helps_with` ["tech abuse guides", "safety planning"] is accurate.
- **Sources:** https://www.techsafety.org/ , https://www.techsafety.org/hotline-services
- **Quote:** "Safety Net is a project of the National Network to End Domestic Violence."
- [ ] human checked on device

## cornell_ceta: Clinic to End Tech Abuse (Cornell Tech)
- **Status:** ⚠️ change suggested
- **Current:** `ceta.tech.cornell.edu (referral via NYC Family Justice Centers)`
- **Suggested:** `ceta.tech.cornell.edu (NYC only; by referral from a NYC Family Justice Center or the Anti-Violence Project (AVP); clients 18+)`
- **Source:** https://ceta.tech.cornell.edu/clinic
- **Quotes:** "Appointments can only be booked via referral from either the FJCs or AVP." / "We can only help clients who are at least 18 years old." The page lists no self-referral route, email or phone for clients.
- **App implication:** the agent should present CETA as "ask your Family Justice Center or AVP advocate about a referral", not as a direct contact.
- [ ] human checked on device

## uk_emergency: Emergency services (UK)
- **Status:** ✅ matches source
- **Current:** `999`
- **Suggested:** no change
- **Source:** https://refugetechsafety.org/ (the page tells users to call 999 in an emergency)
- [ ] human checked on device

## uk_ndah: National Domestic Abuse Helpline (run by Refuge)
- **Status:** ✅ matches source
- **Current:** `0808 2000 247 / nationaldahelpline.org.uk`
- **Digit check:** 0-8-0-8 2-0-0-0 2-4-7 ✅
- **Suggested:** no change. Run by Refuge, free, 24/7, all confirmed.
- **Sources:** https://www.nationaldahelpline.org.uk/ , https://refugetechsafety.org/
- **Quote:** "Call for free and in confidence, 24 hours a day: 0808 2000 247."
- [ ] human checked on device

## uk_refuge_tech: Refuge Tech Safety
- **Status:** ✅ matches source
- **Current:** `refugetechsafety.org`
- **Suggested:** no change. "device guides" = "Secure your tech" guides. "interactive tool" = the "Digital Break-Up Tool", which "helps you review commonly used apps on your phone, laptop, or tablet."
- **Source:** https://refugetechsafety.org/
- [ ] human checked on device

---

# Demo-subset fixes

## fix_recovery_email
- **Status:** ⚠️ change suggested (path detail and source). Flags look correct.
- **Current steps:** Settings → [your name] → Sign-In & Security → review email addresses and trusted phone numbers…
- **Suggested steps:** Settings → [your name] → Sign-In & Security. Tap an email address to change it or "Remove from Account". For trusted phone numbers: Settings → [your name] → Sign-In & Security → **Two-Factor Authentication** → "Add Trusted Phone Number" or remove one. Web alternative (useful from a safe device): account.apple.com → Sign-In and Security → Account Security → Trusted Phone Number. You must keep at least one trusted number.
- **Flags:** `may_notify_abuser: true` ✅. Apple: "Apple notifies you by email, text, or push notification when changes are made to your account". If the abuser controls the old email or number, they may see this.
- **❓ For the human to check:** Apple accounts can also have an **Account Recovery contact** or **recovery key** under Sign-In & Security. I didn't fetch a page on this. If the abuser is set as the recovery contact, that's another way back in. Worth looking at on the device and possibly a new UNVERIFIED fix.
- **Sources:** https://support.apple.com/guide/personal-safety/keep-your-apple-account-secure-ips7d5628cc5/web , https://support.apple.com/en-us/122621
- [ ] human checked on device

## change_apple_id_password
- **Status:** ⚠️ change suggested
- **Current steps:** "Use a safe device. Settings → [your name] → Sign-In & Security → Change Password."
- **Problem:** on a *safe* device, Settings → [your name] is the safe device's own account, not the user's. The two instructions conflict.
- **Suggested steps:** "On your own iPhone: Settings → [your name] → Sign-In & Security → Change Password. At the end, choose **Remove Other Devices** (they'll need to sign in again) or **Keep All Devices Signed In**. You may have to wait one hour (Stolen Device Protection). From a safe device: go to account.apple.com → Sign-In and Security → Password."
- **Flags:** `may_notify_abuser: true` ✅. With "Remove Other Devices", the other devices must sign in again. Apple also sends change notifications by email/text/push. `loses_access: false` ✅.
- **Sources:** https://support.apple.com/en-us/101567 , https://support.apple.com/guide/personal-safety/keep-your-apple-account-secure-ips7d5628cc5/web
- **Quote:** "If you have multiple devices signed in to your Apple Account, you'll have the option to remain signed in or not." / "You might be required to wait one hour before changing your Apple Account password."
- [ ] human checked on device

## remove_unknown_device
- **Status:** ✅ matches source
- **Current steps:** Settings → [your name] → scroll to device list → tap device → Remove from Account.
- **Suggested:** no change to the path. Optional: also offer icloud.com/settings → "Sign Out Of All Browsers".
- **Flags:** `may_notify_abuser: true` ✅ (conservative; Apple doesn't say what the removed device shows ❓). `evidence_loss: true` ✅. The prerequisite (change password first) is consistent with Apple's guidance.
- **Source:** https://support.apple.com/guide/personal-safety/keep-your-apple-account-secure-ips7d5628cc5/web
- **Quote:** removing it means it "can no longer display verification codes", and access to iCloud "is blocked until you sign in again with two-factor authentication."
- [ ] human checked on device

## stop_find_my_sharing
- **Status:** ✅ matches source (risk_note wording could be sharper)
- **Current steps:** Find My → People → select the person → Stop Sharing My Location. Or Settings → Privacy & Security → Safety Check → Manage Sharing & Access.
- **Suggested:** add the confirm tap: "…→ Stop Sharing My Location → **Stop Sharing Location**". Apple's 105104 article also mentions tapping a "More" button before Stop Sharing My Location. Check which applies on the demo iOS.
- **Flags:** `may_notify_abuser: true`. Keep it. Apple's sources conflict:
  - Personal-safety guide: "When you stop sharing your location, the people you previously shared with may notice that you've stopped. On earlier operating systems, they may receive a notification in Messages that you stopped sharing."
  - Apple article 105104: "The person that you stop sharing with won't be notified."
  - Suggested risk_note: "They won't get an alert on current iOS, but they may notice your location is gone. On older iOS versions they may get a Messages notice."
- **Sources:** https://support.apple.com/guide/personal-safety/find-my-and-location-sharing-ips05ede4573/web , https://support.apple.com/en-us/105104 , https://support.apple.com/guide/personal-safety/safety-check-iphone-ios-16-ips2aad835e1/web (path confirmed: "Privacy & Security > Safety Check")
- **❓** A search summary quoted the Safety Check page as saying "People may notice you've stopped sharing information with them…". When fetched, that sentence was **not** found on the US or CA versions. Don't quote it.
- [ ] human checked on device

## review_locator_apps
- **Status:** ✅ matches source (notification claim ❓)
- **Current steps:** Settings → Privacy & Security → Location Services → apps set to 'Always' → 'Never' or delete.
- **Suggested:** no change. Labels confirmed: "Never", "Ask Next Time Or When I Share", "While Using the App", "Always".
- **Flags:** `may_notify_abuser: true`. Keep it. The risk_note claim that family-locator apps tell other members can't be confirmed from allowed sources ❓. `evidence_loss: true` ✅ (deleting the app removes it).
- **Sources:** https://support.apple.com/en-us/102647 , https://support.apple.com/guide/personal-safety/manage-location-services-settings-ips9bf20ad2f/web
- **Quote:** "Always: Allows access to your location even when the app is in the background."
- [ ] human checked on device

## remove_mdm_profile
- **Status:** ⚠️ change suggested (button label)
- **Current steps:** Settings → General → VPN & Device Management → tap profile → Remove Management (or Remove Profile).
- **Suggested steps:** Settings → General → VPN & Device Management → select the profile → **Delete Profile** → follow the prompts → restart. If none are listed, no profiles are installed. "Remove Management" for MDM enrollment is ❓: it appeared in a search snippet, but I couldn't fetch the page. Check on the device.
- **Flags:** `may_notify_abuser: true` ✅ (conservative; Apple doesn't say whether the administrator is notified ❓). `evidence_loss: true` ✅.
- **Source:** https://support.apple.com/guide/personal-safety/review-and-delete-configuration-profiles-ips327569a75/web
- **Quote:** deleting removes "all of the settings, apps, and data associated with the configuration profile." / "check with your system administrator before deleting any apps or profiles."
- [ ] human checked on device

## document_evidence
- **Status:** ⚠️ change suggested (safety-related wording)
- **Current steps:** "Write down device names, people, and dates, or photograph the screen using a safe device."
- **Suggested steps:** "Write down device names, people, and dates **somewhere they can't see** (paper, or a safe device or account). Prefer photographing the screen with a second, safe device. Some apps notify the other person about screenshots, and screenshots on this phone may sync to iCloud Photos. Don't delete threatening messages."
- **Flags:** `may_notify_abuser: false` is OK **only** with the reworded step. NNEDV: some apps "notify the other person if you take a screenshot", and "In some cases, when abusers know that victims are documenting the abuse, they might escalate the abuse." `evidence_loss: false` ✅.
- **Sources:** https://www.techsafety.org/documentationtips , https://support.apple.com/guide/personal-safety/document-suspicious-or-harmful-activity-ips7d42f0c8f/web
- **Quote:** "If you suspect the abuser can access your device, make sure to store the screenshot somewhere else."
- **Replace source string** "Coalition Against Stalkerware / NNEDV" with the two URLs above.
- [ ] human checked on device

## use_safe_device
- **Status:** ✅ matches source
- **Current:** "Use a device the other person has never had access to (a library computer, a trusted friend's phone, or a new phone)…"
- **Suggested:** no change
- **Flags:** all `false` ✅
- **Source:** https://www.techsafety.org/resources-survivors/technology-safety-plan
- **Quote:** "try using a different device that the person hasn't had physical or remote access to in the past", e.g. "a computer at a library or a friend's phone."
- [ ] human checked on device

## carrier_own_account
- **Status:** ⚠️ change suggested (add specifics). The flag is confirmed.
- **Current steps:** "Contact your carrier from a safe device. In the US, the Safe Connections Act lets survivors ask to separate their line from a shared plan; an advocate can help with the request."
- **Suggested steps:** "From a safe device, contact your carrier and ask for a **line separation under the Safe Connections Act**. You don't need to be the account holder. You can ask to move *your* line (and lines of people in your care) off the plan, **or** to move *their* line off. The carrier will ask which phone numbers are involved, the names of you and the other person, and one document: a signed affidavit from a licensed medical or mental-health provider, social worker, victim services provider or court employee, **or** a police report, protective or restraining order, or other official record. Carriers must process the request within 2 business days and lock the account against SIM changes, ports and cancellations meanwhile. Ask them which date they will notify the account holder. An advocate can help with the affidavit."
- **"Collect less" note:** the carrier needs the abuser's name. The app should *tell* the user this, never ask for it.
- **Flags:** `may_notify_abuser: true` ✅ **confirmed**. `loses_access: false` ✅.
- **Source:** https://docs.fcc.gov/public/attachments/DOC-397987A1.pdf (FCC fact sheet plus draft Report and Order FCC-CIRC2311-02, Oct 25 2023; ¶¶27, 29, 64, 76, 77)
- **Quotes (¶77):** "we require a covered provider to inform a survivor who has submitted a line separation request, but who is not the primary account holder, of the date on which the covered provider intends to give any formal notice to the primary account holder." / "We prohibit a covered provider from notifying an abuser who is not the primary account holder when the lines of a survivor … are separated" / providers "should be mindful of … automatic notifications about account activity, which may serve as de facto notifications".
- **Quote (¶29):** documentation is "(1) a copy of a signed affidavit from a licensed medical or mental health care provider, … licensed social worker, victim services provider, … or an employee of a court … or (2) a copy of a police report, statements provided by police … protective or restraining orders, … or any other official record".
- **❓** fcc.gov returned 403 for the consumer guide (https://www.fcc.gov/consumers/guides/how-request-phone-line-separation-abusers-account). The quotes above come from the **circulated draft** order. Confirm against the final order FCC 23-96. Fee rules (no early-termination fees) and Lifeline emergency support were not checked against a fetched page.
- [ ] human checked on device

---

# Other fixes

## disable_sms_forwarding
- **Status:** ⚠️ minor change (put the current path first)
- **Current:** "Settings → Messages → Text Message Forwarding (on newer iOS: Settings → Apps → Messages) → …"
- **Suggested:** "Settings → Apps → Messages → Text Message Forwarding → turn off any device you don't recognise. (Older iOS: Settings → Messages.)"
- **Flags:** `may_notify_abuser: true` ✅ (conservative; Apple says nothing about notifications ❓). `evidence_loss: true` ✅.
- **Source:** https://support.apple.com/guide/personal-safety/review-forwarding-settings-ips07e9f4def/web
- **Quote:** forwarded texts "appear on other devices where you're signed in to your Apple Account", and those devices can send texts from your number.
- [ ] human checked on device

## leave_family_sharing
- **Status:** ⚠️ change suggested (path is the iOS 17 one)
- **Current:** Settings → [your name] → Family → [your name] → Stop Using Family Sharing.
- **Suggested:** "Settings → **Family** (below your name) → [your name] → Stop Using Family Sharing. (iOS 17 or earlier: Settings → [your name] → Family Sharing → [your name] → Stop Using Family Sharing.)" Optionally offer a less visible alternative: Settings → Family → Location Sharing, to stop location sharing only.
- **Flags:** `may_notify_abuser: true`. Keep it. Apple doesn't say whether the organizer is notified ❓. `loses_access: true` ✅: purchased content, shared subscriptions, and in-app purchases tied to apps others bought become unavailable.
- **Caveat:** members **under 13 can't leave**. Members over 13 can leave at any time.
- **Source:** https://support.apple.com/guide/personal-safety/manage-family-sharing-ips75b3b794f/web
- [ ] human checked on device

## change_passcode
- **Status:** ⚠️ change suggested (**safety-critical step missing**)
- **Current:** "iPhone: Settings → Face ID & Passcode → Change Passcode. Android: Settings → Security → Screen lock."
- **Suggested:** "iPhone: Settings → Face ID & Passcode (or Touch ID & Passcode) → Change Passcode, **then tap Expire Previous Passcode** so the old one can't be used to reset it. Android: Settings → Security → Screen lock (may vary by manufacturer)."
- **Flags:** `may_notify_abuser: true` ✅
- **Sources:** https://support.apple.com/guide/personal-safety/set-a-unique-device-passcode-or-password-ipsd0a253dd5/web , https://support.google.com/android/answer/9079129
- **Quote:** "you can use your old passcode to reset your passcode for 72 hours." The fix is to tap "Expire Previous Passcode".
- [ ] human checked on device

## google_fix_recovery
- **Status:** ⚠️ change suggested (menu rename plus safety caveat)
- **Current:** myaccount.google.com → Security → Recovery email / Recovery phone → replace.
- **Suggested:** "myaccount.google.com → **Security & sign-in** → under 'How you sign in to Google' → Recovery phone / Recovery email → Edit or Delete."
- **risk_note addition:** "Google may keep sending codes to the old phone or email for 7 days."
- **Flags:** `may_notify_abuser: true` ✅
- **Source:** https://support.google.com/accounts/answer/183723
- **Quote:** "If you change your recovery info or other authentication factors, Google may send codes to your previous info for 7 days."
- [ ] human checked on device

## google_remove_device
- **Status:** ⚠️ minor change (menu rename)
- **Current:** myaccount.google.com → Security → Your devices → Manage all devices → device → Sign out.
- **Suggested:** "myaccount.google.com → **Security & sign-in** → Your devices → Manage all devices → device → Sign out. If several sessions show the same device name, sign out of all of them."
- **Flags:** `may_notify_abuser: true` ✅ (Google doesn't say what the signed-out device shows ❓). `evidence_loss: true` ✅.
- **Source:** https://support.google.com/accounts/answer/3067630
- [ ] human checked on device

## google_stop_location_share
- **Status:** ⚠️ / ❓ (I couldn't confirm the in-app Maps path)
- **Current:** Google Maps → profile picture → Location sharing → select person → Stop.
- **Suggested:** use the documented routes. Web: "myaccount.google.com → People & sharing → Location Sharing → Manage Location Sharing → person → Stop". Android: "Settings → Location → Location services → Google Location Sharing → Stop next to the person's name". Keep the Maps-app path only if the human confirms it on a device.
- **Flags:** `may_notify_abuser: true`. Keep it (Google doesn't say ❓).
- **Sources:** https://support.google.com/maps/answer/7326816 , https://support.google.com/maps/answer/7326816?co=GENIE.Platform%3DAndroid&hl=en
- **Quote:** "Turning off Location Sharing will not remove your previous location shares."
- [ ] human checked on device

## whatsapp_unlink_devices
- **Status:** ✅ matches source (add the confirm tap)
- **Current:** WhatsApp → Settings → Linked Devices → tap device → Log Out.
- **Suggested:** "WhatsApp → Settings (or your profile picture) → Linked devices → tap the device → Log out → **Log out** (confirm)."
- **Flags:** `may_notify_abuser: true` ✅ (conservative; WhatsApp doesn't say ❓). `evidence_loss: true` ✅.
- **Sources:** https://faq.whatsapp.com/834124628020911/?cms_platform=iphone&locale=en_US , https://faq.whatsapp.com/378279804439436
- **Note:** linked devices also log out automatically after 30 days of inactivity, or if the phone is unused for over 14 days.
- [ ] human checked on device
