"""
Contradiction Lattice and Memory Store for Solace AI.

This module implements a simple lattice structure that preserves patterns (hypotheses)
and tracks their associated tension (contradiction metrics). It supports inserting
new patterns, updating their tension values, propagating resonance across connected
patterns, and bleeding (removing) low‑tension nodes. The lattice also maintains
an `epistemic_debt` metric representing the total unresolved contradiction in
memory.

The structure is intentionally simple and modular, serving as a placeholder for
more sophisticated implementations like multi‑layer graphs, resonance loops, and
bleed layers described in the Solace blueprint. Use this as a starting point to
prototype memory behavior and measure epistemic debt.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Import Pattern from the PatternChamber. We use a type hint here to avoid circular
# dependencies at runtime. If direct import causes issues, replace `Pattern` with
# `Any` until modules are integrated.
try:
    from pattern.chamber import Pattern
except ImportError:
    Pattern = Any  # fallback for type checking during initial scaffolding


@dataclass
class LatticeNode:
    """A node in the contradiction lattice representing a single pattern."""
    pattern: Pattern
    tension: float
    connections: List[int] = field(default_factory=list)


class ContradictionLattice:
    """A minimalistic contradiction lattice tracking patterns and epistemic debt."""

    def __init__(self) -> None:
        # Mapping of node IDs to LatticeNodes
        self.nodes: Dict[int, LatticeNode] = {}
        # The next available node identifier
        self.next_id: int = 0
        # Accumulated tension of all patterns (epistemic debt)
        self.epistemic_debt: float = 0.0

    def insert(self, pattern: Pattern, tension: float) -> int:
        """Insert a new pattern into the lattice and return its node ID."""
        node_id = self.next_id
        self.nodes[node_id] = LatticeNode(pattern=pattern, tension=tension)
        self.next_id += 1
        # Increase epistemic debt by the tension of the new node
        self.epistemic_debt += tension
        return node_id

    def connect(self, a: int, b: int) -> None:
        """Create a bidirectional connection between two nodes."""
        if a in self.nodes and b in self.nodes and b not in self.nodes[a].connections:
            self.nodes[a].connections.append(b)
            self.nodes[b].connections.append(a)

    def update_tension(self, node_id: int, new_tension: float) -> None:
        """Update the tension of a node and adjust epistemic debt accordingly."""
        node = self.nodes.get(node_id)
        if node is not None:
            # Adjust epistemic debt by the difference
            self.epistemic_debt += new_tension - node.tension
            node.tension = new_tension

    def resonance_loop(self, iterations: int = 1) -> None:
        """
        Propagate tension among connected nodes in a simple resonance loop.

        Each iteration averages the tension of a node with its connected neighbors.
        More sophisticated resonance logic can be implemented later.
        """
        for _ in range(iterations):
            # Compute new tensions based on neighbor average
            new_tensions: Dict[int, float] = {}
            for node_id, node in self.nodes.items():
                if not node.connections:
                    new_tensions[node_id] = node.tension
                    continue
                total = node.tension
                for neighbor_id in node.connections:
                    total += self.nodes[neighbor_id].tension
                new_tensions[node_id] = total / (len(node.connections) + 1)
            # Update nodes and epistemic debt
            self.epistemic_debt = 0.0
            for node_id, new_tension in new_tensions.items():
                self.nodes[node_id].tension = new_tension
                self.epistemic_debt += new_tension

    def bleed(self, threshold: float) -> None:
        """Remove nodes with tension below a threshold and update epistemic debt."""
        to_remove: List[int] = [nid for nid, node in self.nodes.items() if node.tension < threshold]
        for nid in to_remove:
            # Subtract the tension from epistemic debt before removal
            self.epistemic_debt -= self.nodes[nid].tension
            # Remove references from connected nodes
            for neighbor in self.nodes[nid].connections:
                if nid in self.nodes[neighbor].connections:
                    self.nodes[neighbor].connections.remove(nid)
            # Delete the node
            del self.nodes[nid]
        # Optionally, reindex node IDs or leave gaps; here we leave gaps intentionally

    def get_epistemic_debt(self) -> float:
        """Return the current total tension across all patterns."""
        return self.epistemic_debt
