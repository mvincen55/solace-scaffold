from __future__ import annotations

import inspect
import hashlib
import time
from typing import List, Optional

from weight.chamber import WeightChamber
from pattern.chamber import PatternChamber
from integrity.chamber import IntegrityChamber
from memory.lattice import ContradictionLattice
from epasa.watcher import Fingerprint



def _hash_string(s: str) -> str:
    """Return a SHA-256 hex digest of a string."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()



def compute_architectural_hash() -> str:
    """
    Compute a cryptographic hash of the architecture by concatenating
    the source code of core classes. If source code isn't available,
    fall back to ``repr()``.
    """
    sources: List[str] = []
    for cls in (WeightChamber, PatternChamber, IntegrityChamber, ContradictionLattice):
        try:
            sources.append(inspect.getsource(cls))
        except (OSError, TypeError):
            sources.append(repr(cls))
    return _hash_string("".join(sources))



def compute_weight_merkle_root(weights: Optional[List[float]]) -> str:
    """
    Compute a Merkle root over a list of weights. Weights are hashed individually
    and combined in pairs until a single root remains. If no weights are provided,
    the hash of an empty list is returned.
    """
    if not weights:
        return _hash_string("[]")
    # Hash each weight to a hex string for Merkle tree leaves.
    leaves: List[str] = [
        hashlib.sha256(f"{w:.12f}".encode("utf-8")).hexdigest() for w in weights
    ]
    while len(leaves) > 1:
        # Duplicate last element if odd number of leaves.
        if len(leaves) % 2 == 1:
            leaves.append(leaves[-1])
        new_level: List[str] = []
        for i in range(0, len(leaves), 2):
            new_level.append(_hash_string(leaves[i] + leaves[i + 1]))
        leaves = new_level
    return leaves[0]



def compute_ethical_vector() -> List[float]:
    """
    Return a deterministic ethical embedding vector (basic version).
    We hash a constant string and slice it into four 4-character chunks,
    converting each to a float between 0 and 1.
    """
    seed = _hash_string("ethics")
    return [int(seed[i:i+4], 16) / 65536.0 for i in range(0, 16, 4)]



def compute_ethical_vector_v2() -> List[float]:
    """
    Return an alternative ethical embedding vector by hashing
    'ethics_and_values' and splitting into four 8-character chunks.
    """
    seed = _hash_string("ethics_and_values")
    return [int(seed[i:i+8], 16) / 0xFFFFFFFF for i in range(0, 32, 8)]



def compute_behavioral_rhythm_hash() -> str:
    """
    Compute a simple hash based on the current time. This represents
    a behavioural rhythm snapshot.
    """
    return _hash_string(str(time.time()))



def compute_behavioral_rhythm_hash_v2(weights: List[float]) -> str:
    """
    Compute a behavioural rhythm hash incorporating the current time
    and the average weight value.
    """
    avg = sum(weights) / len(weights) if weights else 0.0
    return _hash_string(f"{time.time():.6f}_{avg:.6f}")



def compute_fingerprint(weights: Optional[List[float]]) -> Fingerprint:
    """
    Compute the full fingerprint using the improved v2 metrics.
    """
    architectural_hash = compute_architectural_hash()
    merkle_root = compute_weight_merkle_root(weights)
    ethical_vector = compute_ethical_vector_v2()
    rhythm_hash = compute_behavioral_rhythm_hash_v2(weights or [])
    return Fingerprint(
        architectural_hash=architectural_hash,
        weight_merkle_root=merkle_root,
        ethical_vector=ethical_vector,
        behavioural_rhythm_hash=rhythm_hash,
    )
