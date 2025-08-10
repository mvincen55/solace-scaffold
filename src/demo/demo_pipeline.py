#!/usr/bin/env python3

"""
Demo script for running the Tri Chamber pipeline with example data.
This script creates a pipeline instance using Weight, Pattern and Integrity chambers,
feeds a sample list of items through it, and prints the evaluation results along with EPASA status and epistemic debt.
"""

from typing import Any, List

from pipeline_v2 import TriChamberPipeline
from weight.chamber import WeightChamber
from pattern.chamber import PatternChamber
from integrity.chamber import IntegrityChamber
from epasa.fingerprint_v2 import compute_fingerprint


def metric_provider(item: Any) -> float:
    """Return a simple tension score for demonstration."""
    # Simple heuristic: assign high tension to tuples/lists (representing contradictions),
    # and lower tension to plain strings or other data.
    return 1.0 if isinstance(item, (tuple, list)) else 0.5


def main() -> None:
    # Example inputs demonstrating consistency and contradictions
    items: List[Any] = [
        "The sky is blue",
        "The sky is not blue",
        ("A", "A"),
        ("A", "B"),
    ]

    # Initialize the pipeline with our chambers and metric provider.
    pipeline = TriChamberPipeline(
        weight_cls=WeightChamber,
        pattern_cls=PatternChamber,
        integrity_cls=IntegrityChamber,
        metric_provider=metric_provider,
        fingerprint_provider=lambda weights: compute_fingerprint(weights),
    )

    # Process the items through the pipeline
    results, epasa_status = pipeline.process(items)

    # Output the results
    print("Evaluation results:", results)
    print("EPASA status:", epasa_status)
    # Display the epistemic debt tracked by the memory lattice, if available
    try:
        print("Epistemic debt:", pipeline.lattice.epistemic_debt)
    except AttributeError:
        pass


if __name__ == "__main__":
    main()
