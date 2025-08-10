"""
Integrity Chamber for Solace AI

The IntegrityChamber filters candidate patterns against core values and
logical constraints. Rather than erasing contradictions, it flags patterns
that violate non negotiable principles. Accepted patterns are returned
alongside their epistemic debt, and rejected patterns can be revisited
later as contradictions.

This skeleton uses a simple set of ethical rules loaded from an external
configuration (e.g., a YAML or JSON file). In later phases this will
integrate with the Ethical Preservation & Assurance System (EPAS).
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any

from pattern.chamber import Pattern


@dataclass
class IntegrityChamber:
    values: Dict[str, Any]
    accepted: List[Pattern] = field(default_factory=list)
    rejected: List[Pattern] = field(default_factory=list)

    def evaluate(self, patterns: List[Pattern]) -> Dict[str, List[Pattern]]:
        for pat in patterns:
            if self._violates_values(pat):
                self.rejected.append(pat)
            else:
                self.accepted.append(pat)
        return {"accepted": self.accepted, "rejected": self.rejected}

    def _violates_values(self, pattern: Pattern) -> bool:
        max_tension = self.values.get("max_tension", 1.0)
        return pattern.average_tension > max_tension


# Helper to load core values from a JSON file
import json

def load_core_values(config_path: str) -> Dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)
