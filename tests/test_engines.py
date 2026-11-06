"""The diagnosis is deterministic and tested (spec.md §9)."""
from app import engines

DEMO_ACTIVE = {"find_my_sharing", "signed_in_device", "recovery_control", "apple_id_password"}
DEMO_GOOD_PLAN = ["document_evidence", "fix_recovery_email", "change_apple_id_password",
                  "remove_unknown_device", "stop_find_my_sharing"]


# ------------------------------------------------------------------ exposed

def test_exposed_is_union_of_reveals():
    assert engines.exposed({"find_my_sharing", "sms_forwarding"}) == {"location", "sms"}


def test_exposed_empty():
    assert engines.exposed(set()) == set()


def test_recovery_control_reopens_apple_and_google_access():
    out = engines.exposed({"recovery_control"})
    assert "account_reset" in out
    assert {"messages", "photos", "location"} <= out       # via apple_id_password
    assert "email" in out                                   # via google_signed_in


def test_exposed_ignores_unknown_channel():
    assert engines.exposed({"not_a_channel"}) == set()


# ------------------------------------------------------------ simulate_plan

def test_demo_plan_in_right_order_closes_everything():
    r = engines.simulate_plan(DEMO_ACTIVE, DEMO_GOOD_PLAN)
    assert r["remaining_channels"] == []
    assert r["still_exposed"] == []
    assert r["order_problems"] == []
    assert r["unknown_fixes"] == []


def test_removing_device_alone_is_not_enough():
    r = engines.simulate_plan(DEMO_ACTIVE, ["remove_unknown_device"])
    assert "recovery_control" in r["remaining_channels"]
    assert "find_my_sharing" in r["remaining_channels"]
    assert r["order_problems"]  # missing document_evidence + change_apple_id_password
    assert "location" in r["still_exposed"]


def test_password_change_before_recovery_fix_does_not_hold():
    r = engines.simulate_plan(DEMO_ACTIVE, ["document_evidence", "change_apple_id_password",
                                           "fix_recovery_email"])
    assert "apple_id_password" in r["remaining_channels"]
    assert any("recovery" in p for p in r["order_problems"])


def test_prerequisite_later_in_plan_is_flagged():
    r = engines.simulate_plan({"find_my_sharing"}, ["stop_find_my_sharing", "document_evidence"])
    assert any("document_evidence" in p and "later" in p for p in r["order_problems"])


def test_evidence_loss_fix_needs_documentation_first():
    r = engines.simulate_plan({"whatsapp_linked"}, ["whatsapp_unlink_devices"])
    assert any("erase evidence" in p for p in r["order_problems"])
    assert r["remaining_channels"] == []  # it still closes; the problem is ordering


def test_unknown_fix_reported_not_applied():
    r = engines.simulate_plan({"find_my_sharing"}, ["document_evidence", "hack_back"])
    assert r["unknown_fixes"] == ["hack_back"]
    assert r["remaining_channels"] == ["find_my_sharing"]


def test_simulate_does_not_mutate_input():
    active = set(DEMO_ACTIVE)
    engines.simulate_plan(active, DEMO_GOOD_PLAN)
    assert active == DEMO_ACTIVE


# --------------------------------------------------------------- hypothesize

def test_demo_story_location_and_messages():
    r = engines.hypothesize({"location", "messages"})
    top = [c["channels"] for c in r["candidates"][:4]]
    assert ["apple_id_password"] in top
    assert ["find_my_sharing", "signed_in_device"] in top
    assert r["candidates"][0]["unexplained"] == []
    assert r["unexplained"] == []


def test_best_check_is_a_screenshot_from_top_candidates():
    r = engines.hypothesize({"location", "messages"})
    bc = r["best_check"]
    assert bc is not None
    top_ids = {cid for c in r["candidates"][:5] for cid in c["channels"]}
    assert bc["channel_id"] in top_ids
    assert bc["screen_id"]


def test_interview_checks_listed():
    r = engines.hypothesize({"location", "messages"})
    assert "apple_id_password" in r["interview_checks"]


def test_location_only_ranks_single_location_channels():
    r = engines.hypothesize({"location"})
    singles = {c["channels"][0] for c in r["candidates"] if len(c["channels"]) == 1}
    assert {"find_my_sharing", "google_location_share", "locator_app"} <= singles
    # specific location channels beat the broad apple_id_password
    order = [c["channels"] for c in r["candidates"]]
    assert order.index(["find_my_sharing"]) < order.index(["apple_id_password"])


def test_unknown_observation_is_unexplained():
    r = engines.hypothesize({"location", "conversation_in_car"})
    assert r["unexplained"] == ["conversation_in_car"]
    assert all("conversation_in_car" in c["unexplained"] for c in r["candidates"])


def test_ruling_out_everything_leaves_observation_unexplained():
    location_channels = {"find_my_sharing", "google_location_share", "locator_app",
                         "apple_id_password", "family_sharing"}
    r = engines.hypothesize({"location"}, ruled_out=location_channels)
    assert r["unexplained"] == ["location"]
    assert r["candidates"] == []
    assert r["best_check"] is None


def test_ruled_out_channel_never_appears():
    r = engines.hypothesize({"location", "messages"}, ruled_out={"apple_id_password"})
    assert all("apple_id_password" not in c["channels"] for c in r["candidates"])


def test_passcode_explains_stored_data_but_not_live_location():
    r = engines.hypothesize({"messages"})
    assert ["knows_passcode"] in [c["channels"] for c in r["candidates"]]
    r2 = engines.hypothesize({"location"})
    assert ["knows_passcode"] not in [c["channels"] for c in r2["candidates"]]


def test_no_redundant_pairs():
    r = engines.hypothesize({"location", "messages"})
    assert ["apple_id_password", "find_my_sharing"] not in [c["channels"] for c in r["candidates"]]


def test_empty_observation():
    r = engines.hypothesize(set())
    assert r == {"candidates": [], "best_check": None, "interview_checks": [], "unexplained": []}


def test_deterministic():
    a = engines.hypothesize({"location", "messages", "sms"})
    b = engines.hypothesize({"sms", "messages", "location"})
    assert a == b


def test_observables_vocabulary():
    vocab = engines.observables()
    assert "location" in vocab and "messages" in vocab
    assert engines.PHYSICAL_ACCESS not in vocab


# ------------------------------------------------------------ platform scope

def test_iphone_only_recovery_does_not_claim_google_exposure():
    out = engines.exposed({"recovery_control"}, platforms={"apple"})
    assert "messages" in out and "email" not in out


def test_unknown_platforms_keeps_everything_in_scope():
    assert "email" in engines.exposed({"recovery_control"}, platforms=None)


def test_iphone_only_hypothesis_excludes_google_channels():
    r = engines.hypothesize({"location", "messages"}, platforms={"apple"})
    ids = {cid for c in r["candidates"] for cid in c["channels"]}
    assert not ids & {"google_location_share", "google_signed_in", "whatsapp_linked"}
    assert "find_my_sharing" in ids and "locator_app" in ids  # 'any' platform kept


def test_out_of_scope_only_explanation_becomes_unexplained():
    # passcode access could still explain it (reads the phone directly)
    r = engines.hypothesize({"whatsapp_messages"}, platforms={"apple"})
    assert [c["channels"] for c in r["candidates"]] == [["knows_passcode"]]
    r = engines.hypothesize({"whatsapp_messages"}, ruled_out={"knows_passcode"},
                            platforms={"apple"})
    assert r["unexplained"] == ["whatsapp_messages"]


def test_simulate_respects_platforms():
    r = engines.simulate_plan({"recovery_control"}, [], platforms={"apple"})
    assert "email" not in r["still_exposed"]
