import json
import re
from typing import Any

_NUMBER_PATTERN = re.compile(r"\b\d+(?:\.\d+)?\b")


def _collect_numbers(obj: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(obj, dict):
        for v in obj.values():
            found |= _collect_numbers(v)
    elif isinstance(obj, list):
        for v in obj:
            found |= _collect_numbers(v)
    elif isinstance(obj, (int, float)):
        found.add(str(int(obj)) if isinstance(obj, float) and obj.is_integer() else str(obj))
        if isinstance(obj, float):
            found.add(f"{obj:.2f}")
            found.add(f"{obj:.1f}")
    elif isinstance(obj, str) and re.fullmatch(r"\d+(?:\.\d+)?", obj):
        found.add(obj)
    return found


def find_unsupported_numbers(answer: str, evidence: dict[str, Any]) -> list[str]:
    """Return numbers in the answer that do not appear anywhere in the evidence JSON."""
    allowed = _collect_numbers(evidence)
    # Common benign numbers in prose
    allowed.update({"1", "2", "3", "4", "5", "6", "20"})
    mentioned = _collect_numbers(json.loads(json.dumps(evidence)))
    allowed |= mentioned
    suspicious: list[str] = []
    for token in _NUMBER_PATTERN.findall(answer):
        if token not in allowed:
            suspicious.append(token)
    return suspicious
