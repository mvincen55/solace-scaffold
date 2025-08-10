from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, Optional, Set
import random
import re

@dataclass
class WeightedInput:
    content: Any
    weight: float
    epistemic_debt: float

class WeightChamber:
    """Assigns tension (weight) to inputs using a contradiction heuristic.

    Heuristic: higher contradiction → higher weight.
    We estimate contradiction as average Jaccard distance to prior inputs,
    blended with a Beta prior sample for stochasticity/antifragility.
    """
    def __init__(self, prior_alpha: float = 2.0, prior_beta: float = 2.0) -> None:
        self.alpha, self.beta = prior_alpha, prior_beta
        self._history: List[Set[str]] = []

    def _tokenize(self, text: str) -> Set[str]:
        return set(re.findall(r"\w+", str(text).lower()))

    def _jaccard_distance(self, a: Set[str], b: Set[str]) -> float:
        union = a | b
        if not union:
            return 0.0
        return 1.0 - (len(a & b) / len(union))

    def assign(self, content: Any, contradiction_metric: Optional[float] = None) -> WeightedInput:
        tokens = self._tokenize(str(content))
        if contradiction_metric is not None:
            base_tension = max(0.0, min(1.0, float(contradiction_metric)))
        else:
            if not self._history:
                base_tension = 0.5
            else:
                base_tension = sum(self._jaccard_distance(tokens, h) for h in self._history) / len(self._history)
        beta_sample = random.betavariate(self.alpha, self.beta)
        tension = (base_tension + beta_sample) / 2.0
        tension = max(0.0, min(1.0, tension))
        wi = WeightedInput(content=content, weight=tension, epistemic_debt=tension)
        self._history.append(tokens)
        return wi

    def update(self, resolved: bool, amount: float = 1.0) -> None:
        if resolved:
            self.alpha += amount
        else:
            self.beta += amount
