from __future__ import annotations
from dataclasses import dataclass
from typing import List, Set
import re
from weight.advanced_chamber import WeightedInput

@dataclass
class Pattern:
    items: List[WeightedInput]
    average_tension: float
    total_debt: float

class PatternChamber:
    """Groups weighted inputs into similarity clusters (connected components).

    Two items are connected if Jaccard similarity >= threshold.
    """
    def __init__(self, threshold: float = 0.3) -> None:
        self.threshold = threshold

    def _tokenize(self, text: str) -> Set[str]:
        return set(re.findall(r"\w+", str(text).lower()))

    def _similarity(self, a: Set[str], b: Set[str]) -> float:
        union = a | b
        return (len(a & b) / len(union)) if union else 1.0

    def construct_patterns(self, weighted_inputs: List[WeightedInput]) -> List[Pattern]:
        n = len(weighted_inputs)
        if n == 0:
            return []
        toks = [self._tokenize(wi.content) for wi in weighted_inputs]
        visited = [False] * n
        patterns: List[Pattern] = []

        for i in range(n):
            if visited[i]:
                continue
            queue = [i]
            visited[i] = True
            cluster: List[int] = []
            while queue:
                j = queue.pop()
                cluster.append(j)
                for k in range(n):
                    if not visited[k] and self._similarity(toks[j], toks[k]) >= self.threshold:
                        visited[k] = True
                        queue.append(k)
            items = [weighted_inputs[idx] for idx in cluster]
            avg_tension = sum(w.weight for w in items) / len(items)
            total_debt = sum(w.epistemic_debt for w in items)
            patterns.append(Pattern(items=items, average_tension=avg_tension, total_debt=total_debt))
        return patterns
