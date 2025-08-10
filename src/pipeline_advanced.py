from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional

from weight.advanced_chamber import WeightChamber, WeightedInput
from pattern.advanced_chamber import PatternChamber
from integrity.advanced_chamber import IntegrityChamber
from memory.lattice import ContradictionLattice
from epasa.watcher import EpasaWatcher, EpasaMetrics, Fingerprint
from epasa.fingerprint_v2 import compute_fingerprint


class TriChamberPipelineAdvanced:
    def __init__(
        self,
        core_values: Dict[str, float],
        fingerprint_provider: Optional[Callable[[List[float]], Fingerprint]] = None,
        metrics_provider: Optional[Callable[[List[Any]], EpasaMetrics]] = None,
    ) -> None:
        """Initialize the advanced tri-chamber pipeline with ethical core values.

        Args:
            core_values: Dictionary of ethical core values for the Integrity chamber.
            fingerprint_provider: Optional function to compute Fingerprint from weight values.
            metrics_provider: Optional function to compute EpasaMetrics from weight values.
        """
        # Initialize chambers
        self.weight = WeightChamber()
        self.pattern = PatternChamber()
        self.integrity = IntegrityChamber(values=core_values)
        # Providers
        self.fingerprint_provider = fingerprint_provider or compute_fingerprint
        self.metrics_provider = metrics_provider
        # Baseline fingerprint and watcher initialization
        baseline_fp = self.fingerprint_provider([])
        self.watcher = EpasaWatcher(baseline_fp)
        # Contradiction lattice memory
        self.lattice = ContradictionLattice()

    def process(
        self,
        items: List[Any],
        contradiction_metrics: Optional[List[Optional[float]]] = None,
    ) -> Dict[str, Any]:
        """Run the advanced tri-chamber pipeline on a batch of inputs.

        Args:
            items: List of raw inputs to process.
            contradiction_metrics: Optional list of tension values; if None, weights are derived.

        Returns:
            A dictionary with the integrity evaluation results and EPASA status.
        """
        weighted_inputs: List[WeightedInput] = []
        if contradiction_metrics is None:
            contradiction_metrics = [None] * len(items)
        # Assign weights
        for item, metric in zip(items, contradiction_metrics):
            weighted_inputs.append(self.weight.assign(item, metric))
        # Construct and evaluate patterns
        patterns = self.pattern.construct_patterns(weighted_inputs)
        evaluation = self.integrity.evaluate(patterns)
        # Store patterns in memory lattice
        for pattern in patterns:
            self.lattice.insert(pattern)
        # Propagate resonance and bleed low-tension patterns
        self.lattice.resonance_loop()
        self.lattice.bleed()
        # Compute fingerprint using current weight values
        weight_values = [wi.weight for wi in weighted_inputs]
        current_fp = self.fingerprint_provider(weight_values)
        # Compute metrics if provider exists
        current_metrics: Optional[EpasaMetrics] = None
        if self.metrics_provider is not None:
            current_metrics = self.metrics_provider(weight_values)
        # Update watcher
        status = self.watcher.update(current_fp, current_metrics)
        return {
            'results': evaluation,
            'epasa_status': status,
        }
