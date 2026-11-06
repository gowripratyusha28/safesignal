"""Plan/output validator. RULE: never calls an LLM. See spec.md §11."""
from app import data_store


def validate_plan(fix_ids: list[str], safety_mode: str, findings: list[dict],
                  last_hypothesis: dict | None) -> dict:
    """Enforce IDs, covert-mode filtering, prerequisite order, evidence levels."""
    raise NotImplementedError  # Hour 1–3


def scrub_output(text: str) -> tuple[str, list[str]]:
    """Strip phone numbers / URLs not present in resources.json."""
    raise NotImplementedError  # Hour 1–3
