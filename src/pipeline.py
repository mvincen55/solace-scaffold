from __future__ import annotations

"""
Tri-Chamber Pipeline for Solace AI

This module orchestrates the flow of data through the Weight, Pattern and
Integrity chambers. It also integrates the EPASA watchdog and fingerprinting
system to monitor drift and recursion metrics after each processing cycle.
"""

from typing import Any, Dict, List, Optional, Callable

from weight.chamber import WeightChamber, WeightedInput
from pattern.chamber import PatternChamber, Pattern
from integrity.chamber import IntegrityChamber
from epasa.watcher import EpasaWatcher, EpasaMetrics, Fingerprint
from epasa.fingerprint import compute_fingerprint


class TriChamberPipeline:
    """Orchestrate the Weight, Pattern and Integrity stages and monitor state drift."""

    def __init__(
        self,
        core_values: Dict[str, Any],
        fingerprint_provider: Optional[Callable[[], Fingerprint]] = None,
        metrics_provider: Optional[Callable[[], EpasaMetrics]] = None,
    ) -> None:
        self.weight = WeightChamber()
        self.pattern = PatternChamber()
        self.integrity = IntegrityChamber(values=core_values)
        # Providers for fingerprint and metrics.  Fall back to default compute_fingerprint.
        self.fingerprint_provider = fingerprint_provider or compute_fingerprint
        self.metrics_provider = metrics_provider
        # Initialise EPASA watcher with baseline fingerprint
        baseline = self.fingerprint_provider()
        self.watcher = EpasaWatcher(baseline)

    def process(
        self,
        items: List[Any],
        contradiction_metrics: Optional[List[Optional[float]]] = None,
    ) -> Dict[str, Any]:
        """Run the tri-chamber pipeline on a batch of items and return results and status.

        Args:
            items: Raw input items to be processed.
            contradiction_metrics: Optional list of tension values for weighting. If
                not provided, all items start with an uninformative prior.

        Returns:
            A dictionary with keys 'results' (accepted/rejected patterns) and
            'epasa_status' (drift and metric evaluation).
        """
        weighted_inputs: List[WeightedInput] = []
        if contradiction_metrics is None:
            contradiction_metrics = [None] * len(items)
        for item, metric in zip(items, contradiction_metrics):
            weighted_inputs.append(self.weight.assign(item, metric))
        patterns = self.pattern.construct_patterns(weighted_inputs)
        evaluation = self.integrity.evaluate(patterns)
        # Monitor with EPASA watcher
        current_fp = self.fingerprint_provider()
        if self.metrics_provider is not None:
            current_metrics = self.metrics_provider()
        else:
            # Placeholder zeroed metrics until real measurements are implemented
            current_metrics = EpasaMetrics(ce=0.0, rdm=0.0, gor=0.0)
        status = self.watcher.update(current_fp, current_metrics)
        return {"results": evaluation, "epasa_status": status}
