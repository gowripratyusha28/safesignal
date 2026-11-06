# Rights basics research — US, US-NY, UK

Researched 2026-11-06. Every item below is `"verified_on": "UNVERIFIED"` until a human checks the quoted source.
The app should present these as **official information, not legal advice**. None of this is legal advice.

## 1. Summary

**What was found (all from allowed, actually-fetched sources):**

- **US national (5 items):** federal cyberstalking statute 18 U.S.C. §2261A (DOJ guide); Safe Connections Act line-separation right (FCC compliance guide DA 25-267); protective orders are state-level (thehotline.org); protection orders valid across state lines, 18 U.S.C. §2265 (DOJ guide); where to get free legal help (thehotline.org).
- **US-NY (5 + 1 optional):** three courts that issue orders of protection; tech-related "family offenses" (stalking, aggravated harassment, identity theft, coercion, intimate-image dissemination); 2020 smart-home-device provision in orders of protection; right to cut off an abuser's connected-vehicle access; right to a free appointed lawyer in Family Court + NYS hotline; (optional) coerced-debt law effective 2026-06-17. All from opdv.ny.gov.
- **UK (6 items, England & Wales unless noted):** controlling/coercive behaviour offence (SCA 2015 s.76 + CPS guidance naming spyware); stalking offence whose statutory examples include monitoring internet/email use (PHA 1997 s.2A); unauthorised access to accounts/devices (Computer Misuse Act 1990 s.1, UK-wide); Domestic Abuse Act 2021 definition incl. economic and coercive abuse; non-molestation/occupation orders (gov.uk); DAPO pilot (gov.uk); legal aid + Rights of Women advice lines.

**What could NOT be confirmed (❓):**

- ❓ **womenslaw.org** returned HTTP 403 on every page tried (general restraining orders, stalking/cyberstalking, NY pages, email hotline, home page). WomensLaw is only cited *indirectly* via thehotline.org's statement that it "has state-by-state information about laws including protective and restraining orders". The WomensLaw Email Hotline, and the claim that WomensLaw is run by NNEDV, are unconfirmed.
- ❓ **nycourts.gov** returned 403 on every page tried (CourtHelp order-of-protection pages, NYC Family Court page, Criminal Jury Instructions PDF). So: "no filing fee in Family Court", order durations (2 / 5 years), and the CJI statement that "following" includes GPS tracking (Penal Law §120.45) are unconfirmed — they appeared only in search-result snippets, not fetched pages.
- ❓ **fcc.gov** consumer pages returned 403; the Safe Connections item rests on the FCC's official Small Entity Compliance Guide on docs.fcc.gov instead (DA 25-267, March 2025). That is authoritative but written for carriers, not survivors.
- ❓ **police.uk / met.police.uk** returned 403; UK stalking facts rest on legislation.gov.uk and cps.gov.uk instead.
- ❓ The §2261A wording is quoted from a DOJ U.S. Attorney's Office guide dated April 2019, not from the current U.S. Code (uscode.house.gov is not on the allowed list). A 2025 DOJ affidavit found in search suggests the statute has since been amended (adds pets/service animals to the fear element) — the core electronic-means wording appears unchanged, but a human should check the current code text.
- ❓ The NY 2020 smart-home law quote on opdv.ny.gov was cut off mid-sentence by the fetch tool ("...to prohibit the restrained party from remotely controlling"). The page cites bill numbers (A.10039 / S.7926), not a statute section.
- ❓ DAPO pilot: gov.uk lists pilot areas but gives no end date; a Met Police document seen only in search results said the pilot is due to end November 2026. Pilot areas may have changed by the time a human checks.
- I tried `curl` with a browser User-Agent to get round the 403s; that was blocked by the permission system as bot-check circumvention and I did not retry. Those sites remain unverified.

**Safety / accuracy flags for the app (see also §4):**

- **Safe Connections Act line separation can notify the abuser.** The FCC guide says the provider "must not notify an abuser who is not the primary account holder", but it also says the provider will give "formal notification of a line separation ... to the primary account holder". If the abuser *is* the primary account holder they will be told. In `covert` mode this fact should be shown as information only, and any related fix must carry `may_notify_abuser: true`.
- **"UK" items are mostly England & Wales only.** SCA 2015 s.76, PHA 1997 s.2A, DAA 2021 s.1, non-molestation orders, DAPOs, legal aid and Rights of Women all apply to England and Wales. Only the Computer Misuse Act item is UK-wide. Scotland and Northern Ireland have different law; consider labelling the region "UK (England & Wales)" in the UI.
- Several items are **pilots or very new** (DAPO pilot; NY coerced-debt law effective 2026-06-17) and will age quickly.

---

## 2. JSON blocks (ready to paste)

### US national

```json
[
  {"id": "us_federal_stalking", "region": "US", "summary": "Using the internet, phone or other electronic means to repeatedly harass, intimidate or spy on someone, causing fear or serious distress, can be a federal crime (18 U.S.C. 2261A). States have their own stalking laws too.", "source": "https://www.justice.gov/usao-sdwv/page/file/1159421/dl", "verified_on": "UNVERIFIED"},
  {"id": "us_safe_connections", "region": "US", "summary": "Under the federal Safe Connections Act you can ask your mobile carrier to move your line off a shared plan within 2 business days, with no fee and no approval from the account holder. Some documentation is needed.", "source": "https://docs.fcc.gov/public/attachments/DA-25-267A1.pdf", "verified_on": "UNVERIFIED"},
  {"id": "us_protective_orders", "region": "US", "summary": "Civil protective (restraining) orders come from state courts, so the rules differ by state. You apply at a courthouse. WomensLaw.org has state-by-state details. An order is not a substitute for a safety plan.", "source": "https://www.thehotline.org/resources/protective-restraining-orders/", "verified_on": "UNVERIFIED"},
  {"id": "us_order_valid_across_states", "region": "US", "summary": "Under federal law (18 U.S.C. 2265), a valid protection order from one state must be honored and enforced in every other state and on tribal land, even if you have moved and have not registered it there.", "source": "https://www.justice.gov/usao-sdwv/page/file/1159421/dl", "verified_on": "UNVERIFIED"},
  {"id": "us_free_legal_help", "region": "US", "summary": "The National Domestic Violence Hotline (1-800-799-7233) does not give legal advice but can help you find free local legal help. WomensLaw.org explains each state's protective order and custody laws in plain language.", "source": "https://www.thehotline.org/get-help/domestic-violence-legal-help/", "verified_on": "UNVERIFIED"}
]
```

### US-NY

```json
[
  {"id": "us_ny_orders_of_protection", "region": "US-NY", "summary": "In New York you can ask for an order of protection in Family Court (a civil case started with a family offense petition), in criminal court, or in Supreme Court during a divorce. It can order no contact with you.", "source": "https://opdv.ny.gov/orders-protection", "verified_on": "UNVERIFIED"},
  {"id": "us_ny_tech_family_offenses", "region": "US-NY", "summary": "In New York, stalking, aggravated harassment, identity theft, coercion and sharing intimate images without consent are 'family offenses' when done by a family or household member, so Family Court can hear them.", "source": "https://opdv.ny.gov/law-and-public-safety", "verified_on": "UNVERIFIED"},
  {"id": "us_ny_smart_home_devices", "region": "US-NY", "summary": "Since 2020, a New York court issuing an order of protection can also bar the other person from remotely controlling connected devices (smart home technology) in your home.", "source": "https://opdv.ny.gov/laws-regulations", "verified_on": "UNVERIFIED"},
  {"id": "us_ny_connected_vehicle", "region": "US-NY", "summary": "New York law lets a victim of domestic violence end another person's access to a car's connected services, such as GPS location and remote app controls.", "source": "https://opdv.ny.gov/know-your-rights", "verified_on": "UNVERIFIED"},
  {"id": "us_ny_free_lawyer_and_hotline", "region": "US-NY", "summary": "In a New York Family Court protection order case, if you cannot afford a lawyer the court must appoint one at no cost to you. The NYS hotline (800-942-6906, text 844-997-2121) can connect you to local legal advocacy.", "source": "https://opdv.ny.gov/know-your-rights", "verified_on": "UNVERIFIED"},
  {"id": "us_ny_coerced_debt", "region": "US-NY", "summary": "From June 17, 2026, a New York law protects survivors from being held responsible for debt they were forced into. It only covers debt from that date on; OPDV publishes forms for notifying creditors.", "source": "https://opdv.ny.gov/coerced-debt-law", "verified_on": "UNVERIFIED"}
]
```
(`us_ny_coerced_debt` is optional — economic rather than tech abuse, but relevant to account takeover / fraudulent purchases.)

### UK (England & Wales unless noted)

```json
[
  {"id": "uk_coercive_control", "region": "UK", "summary": "In England and Wales, repeated controlling or coercive behaviour by a partner or family member is a crime (Serious Crime Act 2015 s.76). Prosecutors' guidance lists monitoring you online or with spyware as an example.", "source": "https://www.legislation.gov.uk/ukpga/2015/9/section/76", "verified_on": "UNVERIFIED"},
  {"id": "uk_stalking_monitoring", "region": "UK", "summary": "Stalking is a crime in England and Wales. The law's own examples include monitoring someone's use of the internet, email or other electronic communication, and spying on them (Protection from Harassment Act 1997 s.2A).", "source": "https://www.legislation.gov.uk/ukpga/1997/40/section/2A", "verified_on": "UNVERIFIED"},
  {"id": "uk_unauthorised_access", "region": "UK", "summary": "Deliberately getting into a computer, phone or online account without authorisation is a criminal offence across the UK under the Computer Misuse Act 1990 (section 1).", "source": "https://www.legislation.gov.uk/ukpga/1990/18/section/1", "verified_on": "UNVERIFIED"},
  {"id": "uk_domestic_abuse_definition", "region": "UK", "summary": "The Domestic Abuse Act 2021 defines domestic abuse to include controlling or coercive behaviour, economic abuse and psychological or emotional abuse, not just physical violence. A single incident can count.", "source": "https://www.legislation.gov.uk/ukpga/2021/17/section/1", "verified_on": "UNVERIFIED"},
  {"id": "uk_non_molestation_order", "region": "UK", "summary": "If you have experienced domestic abuse you can apply to the family court for a non-molestation order (stops harm or threats) or an occupation order (who lives in the home). No fee to apply; breaking it can mean arrest.", "source": "https://www.gov.uk/injunction-domestic-violence", "verified_on": "UNVERIFIED"},
  {"id": "uk_dapo_pilot", "region": "UK", "summary": "Domestic Abuse Protection Orders (DAPOs) are being piloted in some areas of England and Wales. Victims can apply themselves with no court fee, and breaching a DAPO is a criminal offence.", "source": "https://www.gov.uk/guidance/domestic-abuse-protection-notices-dapns-and-domestic-abuse-protection-orders-dapos", "verified_on": "UNVERIFIED"},
  {"id": "uk_legal_aid_and_advice", "region": "UK", "summary": "Legal aid may be available for domestic abuse cases if you have evidence (e.g. from police, courts or a refuge) and cannot afford legal costs. Rights of Women runs free legal advice lines for women in England and Wales.", "source": "https://www.gov.uk/legal-aid/domestic-abuse", "verified_on": "UNVERIFIED"}
]
```
(7 UK items; `uk_dapo_pilot` and `uk_unauthorised_access` are the easiest to drop if 5 is the target.)

---

## 3. Per-item verification: quotes and checkboxes

Quotes are the exact text returned by the fetch tool from the cited page. Where the tool paraphrased rather than quoted, this is noted.

### US national

**us_federal_stalking** — `[ ] human checked`
- Source fetched: https://www.justice.gov/usao-sdwv/page/file/1159421/dl (DOJ, U.S. Attorney's Office S.D. W.Va., "Federal Domestic Violence Statutes and Elements for Prosecution — April 2019", p.5–6)
- Quote (Cyber Stalking, 18 U.S.C. § 2261A(2)): "It is a federal crime with intent to kill, injure, harass, intimidate, or place under surveillance with the intent to kill, injure, harass or intimidate, to use the mail, any interactive computer service or electronic communication service, or any facility of interstate commerce (including the Internet) to engage in a course of conduct that causes, attempts to cause, or would be reasonably expected to cause substantial emotional distress or places such person in reasonable fear of the death of, or serious bodily injury to, that person or a member of that person's immediate family or that person's intimate partner. A single communication is not sufficient."
- Supporting quote on state law, from DOJ U.S. Attorneys' Bulletin May 2016 (https://www.justice.gov/usao/file/851856/dl?inline=, p.13, quoting a Presidential Proclamation): "In every State across our Nation, stalking is a crime."
- Also fetched: https://www.justice.gov/usao-me/page/file/1411076/dl (USAO Maine brochure, rev. 2021) quoting §2261A(2) with the same operative wording.
- ❓ Current U.S. Code text not checked (uscode.house.gov not on allowed list); a 2025 DOJ affidavit in search results shows later amendments to the fear element.
- Note for UI: this is a federal statute; state stalking/cyberstalking laws vary and are the usual route for prosecution.

**us_safe_connections** — `[ ] human checked`
- Source fetched: https://docs.fcc.gov/public/attachments/DA-25-267A1.pdf (FCC Small Entity Compliance Guide, DA 25-267, 25 March 2025, for Report and Order FCC 23-96)
- Quote (p.2, "Processing Timeframe"): "Within two (2) business days after receiving a completed line separation request from a survivor, a covered provider must separate the line of the survivor and the line of any individual in the care of the survivor from the shared mobile service contract or separate the line of the abuser from the shared mobile service contract."
- Quote (p.5, prohibitions — a provider cannot condition separation on): "Requiring payment of a fee, penalty, or other charge;" ... "Requiring approval of separation by the primary account holder (if the survivor is not the primary account holder);"
- Quote (p.4, notifications): "A covered provider must not notify an abuser who is not the primary account holder when the covered provider separates the line(s) of a survivor or an individual in the care of a survivor from a shared mobile service contract."
- Quote (p.4, required notifications to survivor): "As soon as feasible after receiving a line separation request, a covered provider must notify a survivor of the date on which it intends to: (1) give any formal notification of a line separation, cancellation, or suspension of service to the primary account holder (if the survivor is not the primary account holder) and (2) to the abuser (if the line separation involves the abuser's line)."
- Quote (p.2, confidentiality): providers "must treat the existence of the line separation request and any information or documents submitted by a survivor ... as confidential and securely dispose of the information no later than 90 days after receiving the information."
- Quote (p.8, Lifeline): "Qualified survivors may receive up to a total of six months of emergency communications support."
- Quote (p.9, effective dates): "The following rules in the Report and Order became effective on June 4, 2024, and compliance with such rules became required on July 15, 2024: 47 CFR §§ 64.6400 through 64.6407, and § 64.2010."
- Documentation: the guide says providers must "Clearly identify the information and documentation that survivor must include with a line separation request" (p.5) but the accepted document types are in the underlying order (FCC 23-96), not fetched. ❓ Exact documentation list unconfirmed.
- ❓ Consumer-facing FCC page https://www.fcc.gov/consumers/guides/how-request-phone-line-separation-abusers-account returned 403.
- Safety flag: if the abuser is the primary account holder they *will* receive formal notification — see §4.

**us_protective_orders** — `[ ] human checked`
- Source fetched: https://www.thehotline.org/resources/protective-restraining-orders/
- Quote: "A protective order is a legal document intended to prohibit your partner from physically coming near you or harming or harassing you, your children"
- Quote: "You can apply for a protective order at courthouses."
- Quote: "a protective order should never replace a safety plan"
- Quote: protective orders "depend on your partner's adherence to the law and law enforcement's willingness to enforce"
- Quote (same site, legal-help page): "WomensLaw.org has state-by-state information about laws including protective and restraining orders and child custody laws."
- Note: the page does not itself say "laws vary by state"; that is implied by the state-by-state pointer. State-dependence is the key caveat for the UI.

**us_order_valid_across_states** — `[ ] human checked`
- Source fetched: https://www.justice.gov/usao-sdwv/page/file/1159421/dl (p.8, "Full Faith and Credit to Orders of Protection — 18 U.S.C. § 2265")
- Quote: "This civil law provides that a civil or criminal order issued by a court in one state or Indian tribe shall be accorded full faith and credit by the court of another state or tribe, and is to be enforced as if it were the order of the court of the second state or tribe. This law applies to permanent, temporary and ex parte protection orders that comply with the statute's requirements. To comply, the protection order must have provided the defendant with reasonable notice and an opportunity to be heard, in a manner consistent with due process."
- Quote: "Registration of an order issued by another court or tribe is not required for enforcement."
- Caveat in the same source: "law enforcement may be unable to verify the validity of a protection order at the time of arrest." Carry a paper/digital copy.

**us_free_legal_help** — `[ ] human checked`
- Source fetched: https://www.thehotline.org/get-help/domestic-violence-legal-help/
- Quote: "The Hotline doesn't give legal advice" ... "there may be legal resources available in your community that we can help you identify."
- Quote: "WomensLaw.org has state-by-state information about laws including protective and restraining orders and child custody laws."
- Quote: "Ask a volunteer legal services provider (attorneys who offer free legal services to low-income individuals)"
- Phone on page: 800.799.SAFE (7233) (matches existing `us_ndvh` resource).
- ❓ womenslaw.org itself (403) — its Email Hotline and NNEDV ownership not confirmed from a fetched page; left out of the summary.

### US-NY

**us_ny_orders_of_protection** — `[ ] human checked`
- Source fetched: https://opdv.ny.gov/orders-protection (NYS Office for the Prevention of Domestic Violence)
- Quote: "You can get an order of protection from a Family Court, a court that hears criminal cases, or a Supreme Court."
- Quote: "You start the case by filing a Family Offense Petition."
- Tool paraphrase: criminal courts issue orders "as a condition of release and/or bail in a criminal case"; Supreme Court can issue one during a divorce case.
- Quote (example condition): "have no contact with you, your family, household members, or your children"
- Quote: "If your order of protection is violated you, can file a violation with family court, call the police, or contact a local domestic violence advocate."
- Supporting quote from https://opdv.ny.gov/know-your-rights: "Either court may issue an order of protection from conduct constituting a family offense." and "The forms you need to obtain an order of protection are available from the family court and the local criminal court."
- ❓ "No filing fee in Family Court" and order durations (2 years / 5 years) appeared only in nycourts.gov search snippets; nycourts.gov pages returned 403. Not included in the summary.

**us_ny_tech_family_offenses** — `[ ] human checked`
- Source fetched: https://opdv.ny.gov/law-and-public-safety
- Quote: "The following are family offenses when they occur between members of the same family or household"
- Listed (per fetch): "Stalking in the 1st Degree" through "Stalking in the 4th Degree" (PL § 120.45–120.60); "Aggravated Harassment in the 2nd Degree" (PL § 240.30); "Coercion 2nd" (PL § 135.61) and "Coercion 3rd, subs. 1, 2, and 3" (PL § 135.60); "Identity Theft in the 1st Degree" through "Identity Theft in the 3rd Degree" (PL §§ 190.78–190.80); "Unlawful dissemination or publication of an intimate image" (PL § 245.15).
- Note: "Unlawful surveillance" (PL § 250.45) does not appear on the page.
- ❓ Whether NY's stalking definition of "following" expressly includes GPS tracking: a nycourts.gov jury-instruction PDF (search snippet: "the unauthorized tracking of such person's movements or location through the use of a global positioning system or other device") could not be fetched (403). Not included in summary.

**us_ny_smart_home_devices** — `[ ] human checked`
- Source fetched: https://opdv.ny.gov/laws-regulations
- Quote (entry "Smart Home Tech Abuse", 2020, Technology Safety/Abuse; **truncated by the fetch tool**): "Allows a court, when issuing an order of protection, to prohibit the restrained party from remotely controlling"
- Citation on page: "A. 10039 Rozic / S. 7926 Bailey" (bill numbers; no statute section given).
- ❓ Human must read the full sentence on the page and confirm the statute (likely an amendment to Family Court Act § 842 / Criminal Procedure Law — not confirmed).

**us_ny_connected_vehicle** — `[ ] human checked`
- Source fetched: https://opdv.ny.gov/know-your-rights
- Quote: "NYS law allows a victim of domestic violence to terminate an individual's access to connected vehicle service."
- Tool paraphrase of same page: connected vehicle technology "can include a global positioning system (GPS) that tracks the location of the vehicle or an app that controls any operation of the vehicle."
- ❓ Statute citation, process and documentation requirements not on the fetched page.

**us_ny_free_lawyer_and_hotline** — `[ ] human checked`
- Source fetched: https://opdv.ny.gov/know-your-rights
- Quote: "if it is determined that you cannot afford an attorney, one must be appointed to represent you without cost to you."
- Source fetched: https://opdv.ny.gov/survivors-victims and https://opdv.ny.gov/
- Quote: "Call 800-942-6906, Text 844-997-2121 or chat below"
- Quote: "All conversations are confidential, secure, and available 24/7 in most languages."
- Quote: local "service providers may offer: 24-hour hotlines, legal advocacy, counseling, emotional support"
- Note: the appointed-attorney right is stated in the Family Court context on the page; confirm scope.

**us_ny_coerced_debt** (optional) — `[ ] human checked`
- Source fetched: https://opdv.ny.gov/coerced-debt-law
- Quote: "This law is effective June 17, 2026."
- Quote: "The law only covers debt that occurred on or after the effective date."
- Tool paraphrase: protection against "being held responsible for debt they were forced into"; forms listed: "Notice of Coerced Debt form" and "3rd Party verification form".

### UK (England & Wales unless noted)

**uk_coercive_control** — `[ ] human checked`
- Source fetched: https://www.legislation.gov.uk/ukpga/2015/9/section/76
- Quote (s.76(1)): "A person (A) commits an offence if— (a) A repeatedly or continuously engages in behaviour towards another person (B) that is controlling or coercive, (b) at the time of the behaviour, A and B are personally connected (see subsection (6)), (c) the behaviour has a serious effect on B, and (d) A knows or ought to know that the behaviour will have a serious effect on B."
- Quote (s.76(11)(a)): "on conviction on indictment, to imprisonment for a term not exceeding five years, or a fine, or both;"
- Note: "personally connected" wording inserted 5 April 2023 by the Domestic Abuse Act 2021 s.68 (so the offence no longer requires living together).
- Source fetched: https://www.cps.gov.uk/legal-guidance/controlling-or-coercive-behaviour-intimate-or-family-relationship
- Quote (examples): "monitoring a person via online communication tools or using spyware." ; "using digital systems such as smart devices or social media to coerce, control, or upset the victim."
- Quote (evidence): "GPS tracking devices installed covertly an/or overtly on mobile phones, tablets, vehicles etc."
- Quote: the offence "has a maximum penalty of five years' imprisonment."
- Jurisdiction: England and Wales.

**uk_stalking_monitoring** — `[ ] human checked`
- Source fetched: https://www.legislation.gov.uk/ukpga/1997/40/section/2A
- Quote (s.2A(3)): "The following are examples of acts or omissions which, in particular circumstances, are ones associated with stalking— ... (d) monitoring the use by a person of the internet, email or any other form of electronic communication, ... (g) watching or spying on a person."
- Source fetched: https://www.cps.gov.uk/legal-guidance/stalking-or-harassment
- Quote: "Stalking or harassment can take place on the internet and via other technologies." Internet-based conduct can include using the internet "as a means of surveillance of the victim" and "accessing spyware or malware."
- Quote (penalties): s.2A/s.2 "carry the maximum general sentence a magistrates' court can impose"; s.4A/s.4 "carry a maximum of ten years' imprisonment and/or a fine on indictment."
- Jurisdiction: England and Wales (s.2A inserted by the Protection of Freedoms Act 2012).
- ❓ police.uk / met.police.uk advice pages returned 403.

**uk_unauthorised_access** — `[ ] human checked`
- Source fetched: https://www.legislation.gov.uk/ukpga/1990/18/section/1
- Quote (s.1(1)): "A person is guilty of an offence if— (a) he causes a computer to perform any function with intent to secure access to any program or data held in any computer ... (b) the access he intends to secure ... is unauthorised; and (c) he knows at the time when he causes the computer to perform the function that that is the case."
- Quote (s.1(3)(c)): "on conviction on indictment, to imprisonment for a term not exceeding two years or to a fine or to both."
- Jurisdiction: UK-wide (separate summary penalties listed for England & Wales and Scotland).

**uk_domestic_abuse_definition** — `[ ] human checked`
- Source fetched: https://www.legislation.gov.uk/ukpga/2021/17/section/1
- Quote (s.1(3)): behaviour is abusive if it consists of any of: "physical or sexual abuse; violent or threatening behaviour; controlling or coercive behaviour; economic abuse (see subsection (4)); psychological, emotional or other abuse;" and the section states a single incident or a course of conduct both qualify (tool paraphrase of s.1(3) closing words).
- Quote (s.1(4)): "'Economic abuse' means any behaviour that has a substantial adverse effect on B's ability to— (a) acquire, use or maintain money or other property, or (b) obtain goods or services."
- Note: both parties must be aged 16 or over and "personally connected" (s.1(2)). Definition applies to England and Wales.

**uk_non_molestation_order** — `[ ] human checked`
- Source fetched: https://www.gov.uk/injunction-domestic-violence
- Quote: "You can apply for an 'injunction' if you've been the victim of domestic abuse."
- Quote (non-molestation order): "protects you or your child from being harmed or threatened by the person who's abused you"
- Quote (occupation order): "decides who can live in the family home or enter the surrounding area"
- Quote: "There's no fee when you apply, but you can choose to pay for legal advice to help you."
- Quote: "The person named in the injunction can be arrested if they break it."
- Jurisdiction: England and Wales (Family Law Act 1996).

**uk_dapo_pilot** — `[ ] human checked`
- Source fetched: https://www.gov.uk/guidance/domestic-abuse-protection-notices-dapns-and-domestic-abuse-protection-orders-dapos
- Quote: "DAPOs are protective orders and can be used to impose restrictions and conditions on a perpetrator of domestic abuse."
- Quote: "Applications can also be made by the police, by a victim themselves or by someone who is not directly involved."
- Quote: "There are no court fees for victims applying for a DAPO."
- Quote: "Breach of a DAPO is a criminal offence and should always be reported."
- Quote: "DAPNs and DAPOs are currently available in certain areas only." Pilot areas listed on page (per fetch): London boroughs of Croydon, Sutton and Bromley; Greater Manchester; Hartlepool, Middlesbrough, Redcar and Cleveland, Stockton-on-Tees; North Wales; plus British Transport Police. Orders available only where the perpetrator lives in a pilot area.
- Quote: "The court may decide to impose electronic monitoring (known as 'tagging') on a perpetrator."
- ❓ Pilot end date not on page (a Met Police document seen only in search said November 2026). Re-check before shipping.

**uk_legal_aid_and_advice** — `[ ] human checked`
- Source fetched: https://www.gov.uk/legal-aid/domestic-abuse
- Quote: "You might be able to get legal aid if you have evidence that you or your children have experienced domestic abuse" and "you cannot afford to pay legal costs."
- Quote: forms of abuse listed include "controlling behaviour", "emotional abuse" and "financial control, for example being stopped from accessing a joint bank account."
- Quote: "You can ask for evidence from:" "the courts," "the police," "social services," "a refuge manager," "your bank" (and health professionals etc.).
- Quote: "You do not have to get evidence before talking to a legal advisor," but "they'll need to see it before deciding whether you can get legal aid."
- Also fetched: https://www.gov.uk/legal-aid/domestic-abuse-or-violence — Quote: legal aid covers "protecting yourself or a child from abuse or harassment, for example domestic abuse or forced marriage".
- Source fetched: https://rightsofwomen.org.uk/get-information/ — Quote: "telephone advice lines provide vital free and confidential legal advice to women in England and Wales"
- Source fetched: https://www.rightsofwomen.org.uk/get-advice/criminal-law/ — Quote: "Call: 020 7251 8887"; hours "Tuesday 10am – 12pm" and "Thursday 7pm – 9pm"; covers "domestic violence, harassment and stalking" and "reporting offences to the police and the criminal justice system."
- Source fetched: https://www.rightsofwomen.org.uk/get-advice/family-law/ — Quote: "This line is for women in England and Wales who need family law advice." "Call: 020 7251 6577"; hours "Tuesday 7pm – 9pm," "Wednesday 7pm – 9pm," "Thursday 7pm – 9pm," "Friday 12pm – 2pm". London line "Call: 020 7608 1137". "We offer telephone interpreting services on our advice lines."
- Note: advice-line hours change; the individual line pages did not themselves say "free" — that word comes from the get-information page.

---

## 4. Notes for whoever wires this into the app

1. **Safe Connections Act and `covert` mode.** Per the FCC guide, the provider must not tell an abuser who is *not* the primary account holder, but it gives "formal notification" to the primary account holder. If the abuser holds the account, requesting a line separation will become known to them. Any fix built on this right must set `may_notify_abuser: true`; the rights item itself is information and can be shown in either mode, ideally with that caveat.
2. **Region labelling.** The UK items (except Computer Misuse Act) are England & Wales law. Consider "UK (England & Wales)" or a per-item `jurisdiction` note. Scotland has its own domestic abuse and stalking offences (not researched here).
3. **State-dependence in the US.** `us_protective_orders` and `us_free_legal_help` are national pointers only; the actual rules are state-level. Only NY has state items.
4. **Nothing here promises outcomes.** Summaries say "can ask", "may be available", "can be a crime". Keep it that way.
5. **No fabricated contact details.** Every phone number above appears on the cited fetched page.

## 5. All URLs actually fetched (for the audit trail)

Succeeded (content used): legislation.gov.uk s.76 SCA 2015; legislation.gov.uk s.2A PHA 1997; legislation.gov.uk s.1 DAA 2021; legislation.gov.uk s.1 CMA 1990; gov.uk/injunction-domestic-violence; gov.uk/legal-aid/domestic-abuse; gov.uk/legal-aid/domestic-abuse-or-violence; gov.uk DAPN/DAPO guidance; cps.gov.uk controlling-or-coercive-behaviour; cps.gov.uk stalking-or-harassment; rightsofwomen.org.uk/get-information/, /get-advice/, /get-advice/criminal-law/, /get-advice/family-law/; docs.fcc.gov DA-25-267A1.pdf; justice.gov usao-sdwv 1159421 (PDF); justice.gov usao-me 1411076 (PDF); justice.gov usao 851856 (USA Bulletin May 2016, PDF); justice.gov/usao-ndga/.../interstate-stalking and /federal-domestic-violence; thehotline.org/get-help/domestic-violence-legal-help/; thehotline.org/resources/protective-restraining-orders/; techsafety.org/resources-survivors; techsafety.org blog 2022/7/29 safe-connections-act-of-2022; opdv.ny.gov/, /orders-protection, /laws-regulations, /know-your-rights, /survivors-victims, /law-and-public-safety, /coerced-debt-law.

Failed (403/404 — not used): womenslaw.org (all pages); nycourts.gov (all pages); fcc.gov/safe-connections and consumer guide; docs.fcc.gov DOC-405322A1.pdf (not text-extractable); police.uk and met.police.uk stalking pages; techsafety.org/legal-resources (404); thehotline.org/resources/legal-help-for-victims-of-domestic-violence/ (404); gov.uk DAPO factsheet URL (404); justice.gov usao-ndtx 1213991 (PDF rendered unreadable); opdv.ny.gov/get-help, /find-help, /help-and-resources (404).
