"""Data-file integrity: every cross-reference points at a real ID."""
from app import data_store


def test_fix_closes_reference_real_channels():
    chans = data_store.channels()
    for f in data_store.fixes().values():
        for c in f["closes"]:
            assert c in chans, f"{f['id']} closes unknown channel {c}"


def test_fix_prerequisites_reference_real_fixes():
    fixes = data_store.fixes()
    for f in fixes.values():
        for p in f["prerequisites"]:
            assert p in fixes, f"{f['id']} has unknown prerequisite {p}"


def test_every_channel_has_a_fix():
    closed = {c for f in data_store.fixes().values() for c in f["closes"]}
    assert set(data_store.channels()) <= closed


def test_fix_required_fields():
    keys = {"id", "title", "platform", "closes", "steps", "may_notify_abuser",
            "loses_access", "evidence_loss", "risk_note", "prerequisites",
            "source", "verified_on"}
    for f in data_store.fixes().values():
        assert keys <= f.keys(), f["id"]


def test_resources_have_contact():
    for r in data_store.resources().values():
        assert r["contact"] and r["region"]
