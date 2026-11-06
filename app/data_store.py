"""Loads the human-verified data files once. Pure, no LLM."""
import json
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def _load(name: str) -> list[dict]:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


@lru_cache
def channels() -> dict[str, dict]:
    return {c["id"]: c for c in _load("channels.json")}


@lru_cache
def fixes() -> dict[str, dict]:
    return {f["id"]: f for f in _load("fixes.json")}


@lru_cache
def resources() -> dict[str, dict]:
    return {r["id"]: r for r in _load("resources.json")}


@lru_cache
def rights() -> dict[str, dict]:
    """Short official facts about the law per region. Information, not legal advice."""
    return {r["id"]: r for r in _load("rights.json")}
