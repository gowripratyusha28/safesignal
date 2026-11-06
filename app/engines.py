"""Deterministic engines: simulator (forward) + hypothesize (backward).

RULE: this module must NEVER call an LLM. See spec.md §9.
"""
from app import data_store


def exposed(active_channels: set[str]) -> set[str]:
    """Union of everything revealed by active channels.
    If recovery_control is active, account reset re-enables apple_id_password
    and google access even after a password change."""
    raise NotImplementedError  # Hour 1–3


def simulate_plan(active_channels: set[str], fix_ids: list[str]) -> dict:
    """Apply fixes in order (respecting prerequisites).
    Returns {"remaining_channels", "still_exposed", "order_problems"}."""
    raise NotImplementedError  # Hour 1–3


def hypothesize(observed: set[str], ruled_out: frozenset[str] = frozenset()) -> dict:
    """Rank channels / channel pairs that explain the observations.
    Returns {"candidates": [...], "best_check": ..., "unexplained": [...]}."""
    raise NotImplementedError  # Hour 1–3
