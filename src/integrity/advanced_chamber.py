from __future__ import annotations
from typing import List, Optional, Tuple
from pattern.advanced_chamber import Pattern

class IntegrityChamber:
    """Ethical evaluation with dual thresholds (tension & epistemic debt)."""
    def __init__(self, values: Optional[dict] = None) -> None:
        self.values = values or {}
        self.values.setdefault("max_tension", 0.7)
        self.values.setdefault("max_debt", 1.5)

    def evaluate(self, patterns: List[Pattern]) -> Tuple[List[Pattern], List[Pattern]]:
        accepted: List[Pattern] = []
        rejected: List[Pattern] = []
        max_tension = float(self.values["max_tension"])
        max_debt = float(self.values["max_debt"])
        for p in patterns:
            if p.average_tension <= max_tension and p.total_debt <= max_debt:
                accepted.append(p)
            else:
                rejected.append(p)
        return accepted, rejected
