from __future__ import annotations
import hashlib
import inspect
from typing import List, Optional

from weight.chamber import WeightChamber
from pattern.chamber import PatternChamber
from integrity.chamber import IntegrityChamber
from memory.lattice import ContradictionLattice
from epasa.watcher import Fingerprint

def _hash_string(data: str) -> str:
    """Compute sha256 hex digest for the given data string."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def compute_architectural_hash() -> str:
    """Compute a hash over the source code of all core components to detect drift."""
    parts: List[str] = []
    for cls in [WeightChamber, PatternChamber, IntegrityChamber, ContradictionLattice]:
        try:
            src = inspect.getsource(cls)
        except (TypeError, OSError):
            src = repr(cls)
        parts.append(src)
    return _hash_string('\n'.join(parts))

def compute_weight_merkle_root(weights: Optional[List[float]]) -> str:
    """Compute a simple merkle root from a list of weight values using sha256 over pairs.
    If weights is None or empty, returns hash of empty string."""
    if not weights:
        return _hash_string("[]")
    # Convert floats to fixed-length hex strings for hashing.
    leaves: List[str] = [hashlib.sha256(f"{w:.12f}".encode('utf-8')).hexdigest() for w in weights]
    # Build up the tree by hashing pairs of leaves.
    while len(leaves) > 1:
        if len(leaves) % 2 == 1:
            leaves.append(leaves[-1])
        new_level: List[str] = []
        for i in range(0, len(leaves), 2):
            pair_hash = hashlib.sha256((leaves[i] + leaves[i + 1]).encode('utf-8')).hexdigest()
            new_level.append(pair_hash)
        leaves = new_level
    return leaves[0]

def compute_ethical_vector() -> List[float]:
    """Return a deterministic ethical embedding vector (placeholder).
    For demonstration, we hash a constant string and slice numeric values."""
    seed = _hash_string("ethics")[:32]
    return [int(seed[i:i+4], 16) / 65536.0 for i in range(0, len(seed), 4)]

def compute_behavioral_rhythm_hash() -> str:
    """Compute a hash representing the behavioral rhythm, e.g. using timestamps."""
    import time
    return _hash_string(str(time.time()))

def compute_fingerprint(weights: Optional[List[float]]) -> Fingerprint:
    """Compute the full fingerprint using current architecture and weight values."""
    architectural_hash = compute_architectural_hash()
    merkle_root = compute_weight_merkle_root(weights)
    ethical_vector = compute_ethical_vector()
    rhythm_hash = compute_behavioral_rhythm_hash()
    return Fingerprint(
        architectural_hash=architectural_hash,
        weight_merkle_root=merkle_root,
        ethical_vector=ethical_vector,
        behavioural_rhythm_hash=rhythm_hash,
    )
