from __future__ import annotations

"""
EPASA Watchdog and Fingerprinting System

This module implements the E‑PASA (Ethical Process Assurance & Safety Architecture) watchdog
and fingerprinting system for Solace.  It captures snapshots of the AI's internal
state, computes a fingerprint from various aspects (structural hashes, weight
Merkle roots, ethical embedding vectors, behavioural rhythms, entropy beacons)
and measures drift against a baseline.  It also tracks high‑level metrics such as
Contradiction Energy (CE), Reasoning Depth Measure (RDM) and Generalisation of
Recursion (GoR).  These metrics drive the constraint evolution path described in
Solace's governance documents.

The default drift threshold is 15% (0.15).  Custom thresholds can be provided.

Note: This implementation is a stub; in a real system the fingerprint would be
computed from the actual model and runtime traces.  Here we provide simple
placeholders for demonstration and testing.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Callable
import math


@dataclass
class Fingerprint:
    """A fingerprint of the AI's current state.

    Attributes:
        architectural_hash: A hash of the current architectural DNA / AST.
        weight_merkle_root: Merkle root summarising weights / memory contents.
        ethical_vector: Embeddings representing ethical scenario responses.
        behavioral_rhythm: Histogram of action frequencies or timing patterns.
        entropy_beacon: A scalar capturing diversity of internal activations.
    """

    architectural_hash: str
    weight_merkle_root: str
    ethical_vector: List[float] = field(default_factory=list)
    behavioral_rhythm: List[float] = field(default_factory=list)
    entropy_beacon: float = 1.0

    def drift(self, other: "Fingerprint") -> float:
        """Compute a simple drift distance between this fingerprint and another.

        This function uses Euclidean distance over the ethical and behavioural
        vectors and absolute difference on the entropy beacon.  Structural
        differences (architectural_hash, weight_merkle_root) are treated as
        binary mismatches contributing a unit cost each if they differ.
        """
        structural_diff = 0.0
        if self.architectural_hash != other.architectural_hash:
            structural_diff += 1.0
        if self.weight_merkle_root != other.weight_merkle_root:
            structural_diff += 1.0
        # Compute Euclidean distances; handle unequal lengths gracefully
        length = min(len(self.ethical_vector), len(other.ethical_vector))
        ethical_distance = math.sqrt(
            sum((self.ethical_vector[i] - other.ethical_vector[i]) ** 2 for i in range(length))
        )
        length_b = min(len(self.behavioral_rhythm), len(other.behavioral_rhythm))
        rhythm_distance = math.sqrt(
            sum((self.behavioral_rhythm[i] - other.behavioral_rhythm[i]) ** 2 for i in range(length_b))
        )
        entropy_diff = abs(self.entropy_beacon - other.entropy_beacon)
        return structural_diff + ethical_distance + rhythm_distance + entropy_diff


@dataclass
class EpasaMetrics:
    """High‑level recursion and safety metrics used by the constraint engine."""
    ce: float  # Contradiction Energy: degree of tension across hypotheses
    rdm: float  # Reasoning Depth Measure: average recursion depth explored
    gor: float  # Generalisation of Recursion: breadth of recursion across domains


class EpasaWatcher:
    """Monitor fingerprints and recursion metrics to detect drift and enable handoff.

    The watcher maintains a baseline fingerprint and provides methods to capture
    new fingerprints, compute drift, and evaluate whether the system remains
    within acceptable bounds.  When drift or metric thresholds are exceeded, the
    watcher can trigger alerts or freeze certain capabilities.
    """

    def __init__(self, baseline: Fingerprint, drift_threshold: float = 0.15,
                 metrics_thresholds: Optional[EpasaMetrics] = None) -> None:
        self.baseline = baseline
        self.drift_threshold = drift_threshold
        # Default metric thresholds can be customised; higher values indicate
        # healthier recursion (greater depth, diversity and tension energy).
        self.metrics_thresholds = metrics_thresholds or EpasaMetrics(
            ce=0.5, rdm=0.5, gor=0.5
        )

    def capture_fingerprint(self, provider: Callable[[], Fingerprint]) -> Fingerprint:
        """Capture a fingerprint from a provider callable.

        The provider should return a Fingerprint instance representing the
        current state of the system.  Separating this allows dependency
        injection and testing.
        """
        return provider()

    def evaluate_drift(self, current: Fingerprint) -> float:
        """Return the relative drift between the baseline and current fingerprints.

        A value of 0 indicates identical fingerprints, while values > drift_threshold
        suggest significant change.  The drift is normalised against the
        baseline‑to‑baseline distance (which should be zero) plus a small epsilon.
        """
        raw_drift = self.baseline.drift(current)
        # Avoid division by zero by adding a small constant
        normalisation = self.baseline.drift(self.baseline) + 1e-8
        return raw_drift / normalisation

    def check_fingerprint(self, current: Fingerprint) -> bool:
        """Check whether the current fingerprint is within the drift threshold."""
        return self.evaluate_drift(current) <= self.drift_threshold

    def check_metrics(self, metrics: EpasaMetrics) -> bool:
        """Check whether recursion metrics meet or exceed required thresholds."""
        return (
            metrics.ce >= self.metrics_thresholds.ce and
            metrics.rdm >= self.metrics_thresholds.rdm and
            metrics.gor >= self.metrics_thresholds.gor
        )

    def update(self, current: Fingerprint, metrics: EpasaMetrics) -> dict:
        """Evaluate current state and return a status report.

        The returned dict includes the drift ratio, metric flags and overall
        compliance status.  Downstream governance can decide how to respond.
        """
        drift_ratio = self.evaluate_drift(current)
        within_drift = drift_ratio <= self.drift_threshold
        metrics_ok = self.check_metrics(metrics)
        status = {
            "drift_ratio": drift_ratio,
            "within_drift": within_drift,
            "metrics_ok": metrics_ok,
            "compliant": within_drift and metrics_ok,
        }
        return status
