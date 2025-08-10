from __future__ import annotations
import hashlib
import inspect
import time
from typing import List, Optional

from weight.chamber import WeightChamber
from epasa.watcher import Fingerprint


def _hash_string(s: str) -> str:
    """Compute a SHA-256 hash of the given string and return its hex digest."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def compute_architectural_hash() -> str:
    """Compute a hash representing the architectural DNA of the system.

    This concatenates the source code of core classes such as the WeightChamber
    and hashes the result. In a full implementation, more classes and modules
    would be included to capture a complete architectural fingerprint.
    """
    sources: List[str] = []
    for cls in [WeightChamber]:
        try:
            sources.append(inspect.getsource(cls))
        except Exception:
            # If source code is unavailable, fall back to the class name
            sources.append(repr(cls))
    concatenated = "".join(sources)
    return _hash_string(concatenated)


def compute_weight_merkle_root(weights: List[floOptional[List[float]]) -> str:
    """Compute a placeholder Merkle root for the weight chamber.

    In a full implementation this would build a Merkle tree over the
    internal state of the weight chamber. Here we hash a comma-separated
    list of weight values or an empty list if none are provided.
    """
    if weights is None:
        data = "[]"
    else:
        data = ",".join(f"{w:.4f}" for w in weights)
    return _hash_string(data)


def compute_ethical_vector() -> List[float]:
    """Generate a deterministic pseudo-random ethical embedding vector.

    This uses a fixed string ('ethics') hashed into a sequence of floats
    between 0 and 1. In the real system this would embed actual ethical
    scenario responses or values.
    """
    base_hash = _hash_string("ethics")
    # Convert successive chunks of the hash into floats in [0,1]
    return [int(base_hash[i:i+4], 16) / 65535.0 for i in range(0, 24, 4)]


def compute_behavioral_rhythm_hash() -> str:
    """Compute a hash capturing recent behavioural rhythms.

    The current timestamp is used as a placeholder. A real implementation
    would use logs of interactions, timing patterns, and other behavioural
    signals.
    """
    timestamp = str(time.time())
    return _hash_string(timestamp)


def compute_fingerprint() -> Fingerprint:
    """Generate an identity fingerprint for the Solace AI.

    The fingerprint combines an architectural hash, a weight Merkle root,
    an ethical embedding vector and a behavioural rhythm hash. Together these
    fields form a unique representation of the system's state at a given
    moment. In a production system each component would derive from rich
    internal data rather than placeholders.
    """
    arch_hash = compute_architectural_hash()
    weight_root = compute_weight_merkle_root()
    ethical_vector = compute_ethical_vector()
    rhythm_hash = compute_behavioral_rhythm_hash()
    return Fingerprint(
        architectural_hash=arch_hash,
        weight_merkle_root=weight_root,
        ethical_vector=ethical_vector,
        behavioural_rhythm_hash=rhythm_hash,
    )
