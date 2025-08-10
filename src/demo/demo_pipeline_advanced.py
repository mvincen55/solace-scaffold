#!/usr/bin/env python3
"""
Demo script for running the TriChamberPipelineAdvanced with example data.
This script creates a pipeline instance using the advanced Weight, Pattern, and Integrity chambers,
feeds a sample list of items through it, and prints the evaluation results along with EPASA status and epistemic debt.
"""

from typing import Any, List

from pipeline_advanced import TriChamberPipelineAdvanced
from epasa.fingerprint_v2 import compute_fingerprint

# Example metric provider that assigns tension based on type of content.
def metric_provider(item: Any) -> float:
    """
    Return a simple tension score for demonstration:
    - Strings representing contradictions get higher tension.
    - Numbers and tuples/lists return low tension.
    """
    return 1.0 if isinstance(item, str) else 0.5


def main() -> None:
    # Example inputs demonstrating consistency and contradictions.
    items: List[Any] = [
        "The sky is blue",
        "The sky is not blue",
        ("fire", "cold"),
        ["light", "dark"],
        42
    ]
pipeline = TriChamberPipelineAdvanced(metric_provider=metric_provider, fingerprint_provider=compute_fingerprint)

    # Process the items and print results
    for evaluation, epasa_status, epistemic_debt in pipeline.process(items):
        accepted, rejected = evaluation
        print("Accepted patterns:", accepted)
        print("Rejected patterns:", rejected)
        print("EPASA Status:", epasa_status)
        print("Epistemic debt:", epistemic_debt)
        print("---")


if __name__ == "__main__":
    main()
