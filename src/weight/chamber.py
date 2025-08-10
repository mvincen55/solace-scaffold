"""
Weight Chamber for Solace AI

This module defines the WeightChamber class responsible for assigning
"tension" scores to incoming hypotheses or pieces of data.  In the Solace
architecture the Weight chamber inverts the usual filtration order: rather
than filtering out contradictions, it prioritises them.  Data that challenges
existing models is given higher weight to encourage exploration.

Key features:

- Uses a Beta(2, 2) prior to initialise tension scores, avoiding over confidence.
- Accepts arbitrary data inputs and returns weighted entries.
- Records epistemic debt (amount of unresolved contradiction) alongside tension.
- Provides methods to update the prior distribution as new evidence arrives.

This is a skeleton implementation intended to be expanded in later phases.
"""
from dataclasses import dataclass, field
from typing import Any, List, Optional
import random


def beta_prior(alpha: float = 2.0, beta: float = 2.0) -> float:
    """Generate a random sample from a Beta(alpha, beta) distribution.
    In a full implementation this would use a proper RNG or statistical
    library. For now we approximate by sampling from uniform and
    adjusting the shape slightly.
    """
    return (random.random() + random.random()) / 2.0


@dataclass
class WeightedInput:
    data: Any
    tension: float
    debt: float = 0.0


@dataclass
class WeightChamber:
    history: List[WeightedInput] = field(default_factory=list)
    alpha: float = 2.0
    beta: float = 2.0

    def assign(self, item: Any, contradiction_metric: Optional[float] = None) -> WeightedInput:
        if contradiction_metric is not None:
            tension = 0.5 * contradiction_metric + 0.5 * beta_prior(self.alpha, self.beta)
        else:
            tension = beta_prior(self.alpha, self.beta)
        weighted = WeightedInput(data=item, tension=tension, debt=tension)
        self.history.append(weighted)
        return weighted

    def update_priors(self, resolved: bool) -> None:
        if resolved:
            self.alpha += 0.1
        else:
            self.beta += 0.1

    def get_last_n(self, n: int = 10) -> List[WeightedInput]:
        return self.history[-n:]
