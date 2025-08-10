"""
Tri-Chamber Pipeline for Solace AI # sample

This module orchestrates the flow of data through the Weight, Pattern and
Integrity chambers. It takes raw inputs, assigns tension scores,
constructs patterns and evaluates them against core values.

The pipeline exposes a simple `process` method returning accepted and
rejected patterns.
"""
from typing import Any, Dict, List, Optional

from weight.chamber import WeightChamber, WeightedInput
from pattern.chamber import PatternChamber, Pattern
from integrity.chamber import IntegrityChamber


class TriChamberPipeline:
    def __init__(self, core_values: Dict[str, Any]):
        self.weight = WeightChamber()
        self.pattern = PatternChamber()
        self.integrity = IntegrityChamber(values=core_values)

    def process(
        self,
        items: List[Any],
        contradiction_metrics: Optional[List[Optional[float]]] = None,
    ) -> Dict[str, List[Pattern]]:
        weighted_inputs: List[WeightedInput] = []
        if contradiction_metrics is None:
            contradiction_metrics = [None] * len(items)
        for item, metric in zip(items, contradiction_metrics):
            weighted_inputs.append(self.weight.assign(item, metric))
        patterns = self.pattern.construct_patterns(weighted_inputs)
        return self.integrity.evaluate(patterns)
