"""Pure Python Directed Acyclic Graph (DAG) for Root Cause Discovery and Chain Traversal."""

from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Set

from app.models.diagnostic_finding import DiagnosticFinding


@dataclass
class CausalNode:
    """Represents a diagnostic finding vertex in the causal graph."""
    id: str
    title: str
    category: str
    subtype: str
    severity: str
    confidence_score: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CausalEdge:
    """Represents a validated causal relationship directed from cause to effect."""
    source_id: str  # Cause finding ID
    target_id: str  # Effect finding ID
    relationship_type: str
    relationship_strength: str
    confidence_score: float
    impact_score: float

    def to_dict(self) -> dict:
        return asdict(self)


class RootCauseGraph:
    """
    Lightweight, in-memory Directed Acyclic Graph (DAG) for business causal discovery.
    
    Avoids external graph database dependencies while enabling:
    - Multi-hop causal chain discovery (A -> B -> C)
    - Root cause origin detection (nodes with no incoming causal drivers)
    - Cycle detection and validation
    - Serialization for frontend visualization and LLM prompts
    """

    def __init__(self):
        self.nodes: Dict[str, CausalNode] = {}
        # Forward edges: source_id -> list of CausalEdge (outgoing)
        self._adj_forward: Dict[str, List[CausalEdge]] = defaultdict(list)
        # Reverse edges: target_id -> list of CausalEdge (incoming)
        self._adj_reverse: Dict[str, List[CausalEdge]] = defaultdict(list)

    def add_node(self, finding: DiagnosticFinding) -> CausalNode:
        """Adds a diagnostic finding as a node in the graph."""
        f_id = str(finding.id)
        if f_id not in self.nodes:
            category = finding.supporting_data.get("category", "GENERAL") if finding.supporting_data else "GENERAL"
            subtype = finding.supporting_data.get("subtype", finding.finding_type.value) if finding.supporting_data else finding.finding_type.value
            severity = finding.severity.value if hasattr(finding.severity, "value") else str(finding.severity)

            node = CausalNode(
                id=f_id,
                title=finding.title,
                category=category,
                subtype=subtype,
                severity=severity,
                confidence_score=finding.confidence_score,
            )
            self.nodes[f_id] = node
        return self.nodes[f_id]

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        relationship_strength: str,
        confidence_score: float,
        impact_score: float,
    ) -> bool:
        """
        Adds a directed causal edge (source_id -> target_id).
        Returns True if successfully added without creating a cycle.
        """
        if source_id == target_id:
            return False  # Self-loops not allowed

        # Check for duplicate edge
        for existing in self._adj_forward[source_id]:
            if existing.target_id == target_id and existing.relationship_type == relationship_type:
                return True

        edge = CausalEdge(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            relationship_strength=relationship_strength,
            confidence_score=confidence_score,
            impact_score=impact_score,
        )

        # Speculatively add edge
        self._adj_forward[source_id].append(edge)
        self._adj_reverse[target_id].append(edge)

        # Check if adding edge introduced a cycle
        if self.has_cycle():
            # Rollback edge
            self._adj_forward[source_id].pop()
            self._adj_reverse[target_id].pop()
            return False

        return True

    def has_cycle(self) -> bool:
        """Detects whether the graph contains any cycles using DFS."""
        visited: Set[str] = set()
        recursion_stack: Set[str] = set()

        def dfs(curr: str) -> bool:
            visited.add(curr)
            recursion_stack.add(curr)

            for edge in self._adj_forward.get(curr, []):
                neighbor = edge.target_id
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in recursion_stack:
                    return True

            recursion_stack.remove(curr)
            return False

        for node_id in self.nodes:
            if node_id not in visited:
                if dfs(node_id):
                    return True

        return False

    def get_direct_causes(self, target_id: str) -> List[str]:
        """Returns direct 1-hop upstream cause node IDs for a target finding."""
        return [edge.source_id for edge in self._adj_reverse.get(target_id, [])]

    def get_root_causes(self, target_id: str) -> List[str]:
        """
        Traverses upstream to discover all ultimate root cause node IDs
        (upstream nodes that have no further incoming causal drivers).
        """
        if target_id not in self.nodes:
            return []

        direct_causes = self.get_direct_causes(target_id)
        if not direct_causes:
            return []

        root_causes: Set[str] = set()
        visited: Set[str] = set()
        queue = deque(direct_causes)

        while queue:
            curr_id = queue.popleft()
            if curr_id in visited:
                continue
            visited.add(curr_id)

            upstream = self.get_direct_causes(curr_id)
            if not upstream:
                # Node has no further causes -> It is an ultimate root cause
                root_causes.add(curr_id)
            else:
                for parent_id in upstream:
                    if parent_id not in visited:
                        queue.append(parent_id)

        # If no ultimate root found (or empty), return direct causes
        return list(root_causes) if root_causes else list(direct_causes)

    def get_causal_chains(self, target_id: str) -> List[List[str]]:
        """
        Reconstructs all complete multi-hop causal paths leading to target_id.
        Each path is ordered from root origin to target:
        [Root_Cause_ID -> Intermediate_Cause_ID -> Target_ID]
        """
        if target_id not in self.nodes:
            return []

        all_paths: List[List[str]] = []

        def backtrack(curr_node: str, current_path: List[str], visited_in_path: Set[str]):
            parents = self.get_direct_causes(curr_node)
            if not parents:
                # Reached a root origin
                all_paths.append(list(reversed(current_path)))
                return

            for parent_id in parents:
                if parent_id not in visited_in_path:
                    visited_in_path.add(parent_id)
                    current_path.append(parent_id)
                    backtrack(parent_id, current_path, visited_in_path)
                    current_path.pop()
                    visited_in_path.remove(parent_id)

        backtrack(target_id, [target_id], {target_id})
        return all_paths

    def get_edges(self) -> List[CausalEdge]:
        """Returns a flat list of all edges in the graph."""
        edges = []
        for edge_list in self._adj_forward.values():
            edges.extend(edge_list)
        return edges

    def to_dict(self) -> Dict[str, Any]:
        """Serializes nodes and edges to a JSON-compatible dictionary."""
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.get_edges()],
        }
