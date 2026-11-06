"""One or more tests per validator rule (spec.md §11)."""
from app import validator as v

DEMO_ACTIVE = {"find_my_sharing", "signed_in_device", "recovery_control", "apple_id_password"}
DEMO_FIXES = ["document_evidence", "fix_recovery_email", "change_apple_id_password",
              "remove_unknown_device", "stop_find_my_sharing"]


# ---------------------------------------------- Rule 1: IDs must exist

def test_lookup_known_fix():
    r = v.lookup_fix("stop_find_my_sharing")
    assert r["found"] is True and r["title"]


def test_lookup_unknown_fix_gives_closest_matches():
    r = v.lookup_fix("stop_findmy_sharing")
    assert r == {"found": False, "closest_matches": r["closest_matches"]}
    assert "stop_find_my_sharing" in r["closest_matches"]


def test_lookup_unknown_fix_by_description():
    r = v.lookup_fix("change apple id password")
    assert "change_apple_id_password" in r["closest_matches"]


def test_lookup_unknown_resource():
    r = v.lookup_resource("us_hotline")
    assert r["found"] is False and r["closest_matches"]


def test_plan_with_invented_fix_is_rejected():
    r = v.validate_plan(["document_evidence", "factory_reset_his_phone"], "lockdown")
    assert r["ok"] is False
    assert r["rejected"][0]["id"] == "factory_reset_his_phone"
    assert "actionable" not in r


def test_plan_with_invented_resource_is_rejected():
    r = v.validate_plan(["document_evidence"], "lockdown", resource_ids=["made_up_org"])
    assert r["ok"] is False and r["rejected"][0]["kind"] == "resource"


# ---------------------------------------------- Rule 2: covert mode

def test_covert_moves_detectable_fixes_to_discuss_first():
    r = v.validate_plan(DEMO_FIXES, "covert")
    assert r["ok"]
    assert all(not s["may_notify_abuser"] for s in r["actionable"])
    assert [s["id"] for s in r["actionable"]] == ["document_evidence"]
    assert {s["id"] for s in r["discuss_first"]} == set(DEMO_FIXES) - {"document_evidence"}
    assert all("advocate" in s["label"] for s in r["discuss_first"])


def test_unknown_safety_mode_is_treated_as_covert():
    r = v.validate_plan(["stop_find_my_sharing"], None)
    assert r["safety_mode"] == "covert"
    assert "stop_find_my_sharing" not in [s["id"] for s in r["actionable"]]


def test_lockdown_shows_everything_as_actionable_with_labels():
    r = v.validate_plan(DEMO_FIXES, "lockdown")
    assert r["discuss_first"] == []
    labels = {s["id"]: s["label"] for s in r["actionable"]}
    assert labels["document_evidence"] == "Safe now"
    assert "May notify" in labels["stop_find_my_sharing"]


# ---------------------------------------------- Rule 3: prerequisites & order

def test_wrong_order_is_reordered():
    shuffled = ["remove_unknown_device", "change_apple_id_password", "stop_find_my_sharing",
                "fix_recovery_email", "document_evidence"]
    r = v.validate_plan(shuffled, "lockdown")
    o = r["order"]
    assert r["reordered"] is True
    assert o.index("fix_recovery_email") < o.index("change_apple_id_password") \
        < o.index("remove_unknown_device")
    assert o[0] == "document_evidence"


def test_missing_prerequisites_are_added():
    r = v.validate_plan(["remove_unknown_device"], "lockdown")
    assert r["order"] == ["document_evidence", "fix_recovery_email",
                          "change_apple_id_password", "remove_unknown_device"]
    assert set(r["added_prerequisites"]) == {"document_evidence", "fix_recovery_email",
                                             "change_apple_id_password"}
    assert any("Added" in n for n in r["notices"])


def test_correct_order_untouched():
    r = v.validate_plan(DEMO_FIXES, "lockdown")
    assert r["order"] == DEMO_FIXES
    assert r["reordered"] is False and r["added_prerequisites"] == []


def test_duplicates_removed():
    r = v.validate_plan(["document_evidence", "document_evidence"], "lockdown")
    assert r["order"] == ["document_evidence"]


# ---------------------------------------------- Rule 4: document before evidence loss

def test_document_evidence_inserted_before_evidence_loss():
    r = v.validate_plan(["whatsapp_unlink_devices"], "lockdown")
    assert r["order"][0] == "document_evidence"
    assert "document_evidence" in r["added_prerequisites"]


def test_document_evidence_moved_before_evidence_loss():
    r = v.validate_plan(["whatsapp_unlink_devices", "document_evidence"], "lockdown")
    assert r["order"] == ["document_evidence", "whatsapp_unlink_devices"]


# ---------------------------------------------- simulation attached to plan

def test_lockdown_demo_plan_closes_everything():
    r = v.validate_plan(DEMO_FIXES, "lockdown", active_channels=DEMO_ACTIVE)
    assert r["simulation"]["remaining_channels"] == []


def test_covert_simulation_shows_what_stays_exposed():
    r = v.validate_plan(DEMO_FIXES, "covert", active_channels=DEMO_ACTIVE)
    assert "location" in r["simulation"]["still_exposed"]


# ---------------------------------------------- Rule 5: verified needs confirmed screenshot

def test_verified_with_confirmed_screenshot_kept():
    out, flags = v.validate_findings([{"channel_id": "find_my_sharing", "evidence_level": "verified",
                                       "basis": "screenshot", "screenshot_confirmed": True}])
    assert out[0]["evidence_level"] == "verified" and flags == []
    assert out[0]["label"]


def test_verified_from_interview_downgraded():
    out, flags = v.validate_findings([{"channel_id": "apple_id_password",
                                       "evidence_level": "verified", "basis": "interview"}])
    assert out[0]["evidence_level"] == "plausible" and flags


def test_verified_from_unconfirmed_screenshot_downgraded():
    out, _ = v.validate_findings([{"channel_id": "signed_in_device", "evidence_level": "verified",
                                   "basis": "screenshot", "screenshot_confirmed": False}])
    assert out[0]["evidence_level"] == "plausible"


def test_unknown_channel_and_level():
    out, flags = v.validate_findings([
        {"channel_id": "spyware_x", "evidence_level": "reported"},
        {"channel_id": "carrier_account", "evidence_level": "certain"},
    ])
    assert [f["channel_id"] for f in out] == ["carrier_account"]
    assert out[0]["evidence_level"] == "reported"
    assert len(flags) == 2


# ---------------------------------------------- Rule 6: unvetted contacts stripped

def test_vetted_contacts_kept():
    text = "Call 1-800-799-7233 or visit thehotline.org or https://techsafety.org/resources."
    out, flags = v.scrub_output(text)
    assert out == text and flags == []


def test_vetted_uk_number_with_different_spacing_kept():
    out, flags = v.scrub_output("Ring 08082000247 any time.")
    assert flags == []


def test_unvetted_phone_removed():
    out, flags = v.scrub_output("Call the helpline at 1-888-555-0199 today.")
    assert "555" not in out and v.REMOVED in out and flags


def test_unvetted_url_removed():
    out, flags = v.scrub_output("See https://random-dv-help.com/guide for more.")
    assert "random-dv-help" not in out and flags


def test_lookalike_domain_removed():
    out, flags = v.scrub_output("Go to thehotline.org.evil.com")
    assert flags


def test_official_account_pages_and_playbook_domains_allowed():
    out, flags = v.scrub_output("From a safe computer, open account.apple.com or "
                                "myaccount.google.com.")
    assert flags == []


def test_dates_and_short_codes_not_treated_as_phones():
    out, flags = v.scrub_output("Verified 2026-11-06. In an emergency call 911 or 999.")
    assert flags == []


# ---------------------------------------------- Rule 7: unexplained → notice + expert, no "safe"

def test_unexplained_adds_notice_and_expert_resource():
    hyp = {"unexplained": ["conversation_in_car"]}
    r = v.validate_plan(["document_evidence"], "lockdown", region="US", last_hypothesis=hyp)
    assert r["unexplained_notice"] == v.UNEXPLAINED_NOTICE
    assert any(v.EXPERT_HELPS & set(x["helps_with"]) for x in r["resources"])


def test_unexplained_keeps_existing_expert_choice():
    hyp = {"unexplained": ["x"]}
    r = v.validate_plan([], "lockdown", resource_ids=["uk_refuge_tech"], region="UK",
                        last_hypothesis=hyp)
    assert [x["id"] for x in r["resources"]] == ["uk_refuge_tech"]


def test_unexplained_without_vetted_region_falls_back_to_web_guides():
    r = v.validate_plan([], "lockdown", region="India", last_hypothesis={"unexplained": ["x"]})
    assert {x["id"] for x in r["resources"]} <= set(v.GLOBAL_EXPERT_FALLBACK)
    assert r["resources"]


def test_no_unexplained_no_notice():
    r = v.validate_plan(["document_evidence"], "lockdown", last_hypothesis={"unexplained": []})
    assert r["unexplained_notice"] is None


def test_false_reassurance_removed():
    out, flags = v.validate_reply("We checked your settings. You're safe now. "
                                  "Next, let's look at your devices.")
    assert "safe now" not in out
    assert "We checked your settings." in out and "Next, let's look" in out
    assert flags


def test_all_clear_and_imagining_removed():
    out, flags = v.validate_reply("All clear! Maybe you're imagining it.")
    assert out == "" and len(flags) == 2


def test_supportive_phrasing_kept():
    text = ("You're not imagining this. This step is safe to do now because they "
            "won't be notified. You are safe to close this page at any time.")
    out, flags = v.validate_reply(text)
    assert out == text and flags == []


# ---------------------------------------------- resources by region

def test_region_aliases():
    assert v.normalize_region("usa") == "US"
    assert v.normalize_region("United Kingdom") == "UK"
    assert v.normalize_region("US-ny") == "US-NY"
    assert v.normalize_region("us ny") == "US-NY"


def test_us_ny_gets_local_first():
    r = v.resources_for("US-NY")
    ids = [x["id"] for x in r["resources"]]
    assert ids[0] == "cornell_ceta" and "us_ndvh" in ids


def test_other_state_excludes_ny_only_resource():
    ids = [x["id"] for x in v.resources_for("US-CA")["resources"]]
    assert "cornell_ceta" not in ids and "us_ndvh" in ids


def test_uk_resources():
    ids = [x["id"] for x in v.resources_for("england")["resources"]]
    assert "uk_ndah" in ids and "us_ndvh" not in ids


def test_unknown_region_invents_nothing():
    r = v.resources_for("Atlantis")
    assert r["found"] is False and all(x["region"] == "GLOBAL" for x in r["resources"])


def test_missing_region():
    assert v.resources_for(None)["found"] is False
