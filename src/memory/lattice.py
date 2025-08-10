from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..pattern.chamber import Pattern

@dataclass
class LatticeNode:
    pattern: Pattern
    tension: float
    connections: List[int] = field(default_factory=list)

class ContradictionLattice:
    """
    Manages a lattice of patterns and their tensions, supports resonance propagation,
    bleeding of low-tension nodes, and tracking of epistemic debt.
    """
    def __init__(self) -> None:
        self.nodes: Dict[int, LatticeNode] = {}
        self.next_id: int = 0
        self.epistemic_debt: float = 0.0

    def insert(self, pattern: Pattern, tension: float) -> int:
        """
        Insert a new pattern into the lattice with its tension and return its node id.
        """
        node_id = self.next_id
        self.nodes[node_id] = LatticeNode(pattern, tension)
        self.next_id += 1
        self.epistemic_debt += tension
        return node_id

    def connect(self, a: int, b: int) -> None:
        """
        Create a bidirectional connection between two nodes.
        """
        if a in self.nodes and b in self.nodes:
            if b not in self.nodes[a].connections:
                self.nodes[a].connections.append(b)
            if a not in self.nodes[b].connections:
                self.nodes[b].connections.append(a)

    def update_tension(self, node_id: int, new_tension: float) -> None:
        """
        Update the tension of a node and adjust epistemic debt accordingly.
        """
        node = self.nodes.get(node_id)
        if node is not None:
            self.epistemic_debt += new_tension - node.tension
            node.tension = new_tension

    def resonance_loop(self, iterations: int = 1, damping: float = 0.5) -> None:
        """
        Propagate tension among connected nodes. Each iteration moves each node's tension
        toward the average of its neighbors by a factor of `damping`.
        """
        for _ in range(iterations):
            new_tensions: Dict[int, float] = {}
            for node_id, node in self.nodes.items():
                if not node.connections:
                    new_tensions[node_id] = node.tension
                    continue
                total = sum(self.nodes[n_id].tension for n_id in node.connections)
                avg = total / len(node.connections)
                new_tensions[node_id] = node.tension + damping * (avg - node.tension)
            # update tensions and recompute epistemic debt
            self.epistemic_debt = 0.0
            for node_id, t in new_tensions.items():
                self.nodes[node_id].tension = t
                self.epistemic_debt += t

    def bleed(self, threshold: Optional[float] = None, fraction: Optional[float] = None) -> None:
        """
        Remove low-tension nodes from the lattice. If `fraction` is provided, remove that fraction
        of the lowest tension nodes. Otherwise, remove all nodes with tension below `threshold`.
        """
        if not self.nodes:
            return
        if fraction is not None:
            # Remove a fraction of the lowest tension nodes, at least one
            count = max(1, int(len(self.nodes) * fraction))
            sorted_nodes = sorted(self.nodes.items(), key=lambda kv: kv[1].tension)
            to_remove = [nid for nid, _ in sorted_nodes[:count]]
        else:
            if threshold is None:
                return
            to_remove = [nid for nid, node in self.nodes.items() if node.tension < threshold]
        for nid in to_remove:
            # Adjust epistemic debt by subtracting the node's tension
            self.epistemic_debt -= self.nodes[nid].tension
            # Remove this node from its neighbors' connection lists
            for neighbor_id in self.nodes[nid].connections:
                if nid in self.nodes[neighbor_id].connections:
                    self.nodes[neighbor_id].connections.remove(nid)
            # Delete the node
            del self.nodes[nid]
        # Note: we intentionally leave gaps in node IDs rather than reindexing

    def get_epistemic_debt(self) -> float:
        """Return the current total tension across all patterns."""
        return self.epistemic_debt
