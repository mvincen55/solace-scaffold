"""
Pattern Chamber for Solace AI

The PatternChamber accepts weighted inputs and constructs multiple
hypotheses or patterns. It does not collapse contradictions; instead, it
allows divergent patterns to coexist. This skeleton uses a simple
clustering approach based on tension thresholds to group inputs.

Later implementations might use more sophisticated graph models or neural
pattern recognition. Each pattern stores references to its constituent
weighted inputs and a combined tension/debt summary.
"""
from dataclasses import dataclass, field
from typing import List

from weight.chamber import WeightedInput


@dataclass
class Pattern:
    members: List[WeightedInput]
    average_tension: float
    total_debt: float


@dataclass
class PatternChamber:
    patterns: List[Pattern] = field(default_factory=list)

    def construct_patterns(self, inputs: List[WeightedInput], threshold: float = 0.5) -> List[Pattern]:
        high: List[WeightedInput] = [w for w in inputs if w.tension >= threshold]
        low: List[WeightedInput] = [w for w in inputs if w.tension < threshold]

        new_patterns: List[Pattern] = []
        for group in (high, low):
            if group:
                avg_tension = sum(w.tension for w in group) / len(group)
                total_debt = sum(w.debt for w in group)
                pat = Pattern(members=group, average_tension=avg_tension, total_debt=total_debt)
                self.patterns.append(pat)
                new_patterns.append(pat)
        return new_patterns
