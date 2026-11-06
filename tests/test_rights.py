"""Rights basics: official-source facts per region; never invented, never legal advice."""
from app import data_store, tools, validator
from app.export import build_summary
from app.main import _new_session, _public_state

KEYS = {"id", "region", "summary", "source", "verified_on"}


def test_rights_data_integrity():
    rights = data_store.rights()
    assert len(rights) >= 10
    for r in rights.values():
        assert KEYS <= r.keys(), r["id"]
        assert r["source"].startswith("https://"), r["id"]
        assert len(r["summary"]) <= 220, r["id"]
        assert r["region"] in {"US", "US-NY", "UK"}, r["id"]
        assert r["verified_on"] == "UNVERIFIED" or len(r["verified_on"]) == 10


def test_rights_region_precedence():
    ny = [r["region"] for r in validator.rights_for("US-NY")]
    assert ny and ny[: ny.index("US")].count("US-NY") == ny.count("US-NY") > 0
    assert all(r["region"] == "US" for r in validator.rights_for("usa"))
    assert all(r["region"] == "UK" for r in validator.rights_for("England"))
    assert validator.rights_for("Atlantis") == [] and validator.rights_for(None) == []


def test_uk_items_say_their_scope():
    assert all(r.get("scope") == "England & Wales"
               for r in validator.rights_for("UK") if r["id"] != "uk_unauthorised_access")


def test_rights_sources_and_numbers_survive_reply_scrub():
    text = ("See legislation.gov.uk and opdv.ny.gov. The NYS hotline is 800-942-6906 "
            "and you can text 844-997-2121.")
    out, flags = validator.scrub_output(text)
    assert out == text and flags == []


def test_get_resources_returns_rights_and_rule():
    s = _new_session()
    out = tools.get_resources(s, "US-NY")
    assert out["rights"] and "not legal advice" in out["rights_rule"]
    assert {"id", "summary", "source"} <= out["rights"][0].keys()
    assert _public_state(s)["rights"][0]["region"] == "US-NY"


def test_export_includes_rights_section_only_when_region_known():
    s = _new_session()
    assert "RIGHTS BASICS" not in build_summary(s)
    tools.set_context(s, region="UK")
    t = build_summary(s)
    assert "RIGHTS BASICS" in t and "not legal advice" in t and "[England & Wales]" in t
