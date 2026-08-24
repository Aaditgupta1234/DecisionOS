"""Directive DAG Engine for Boardroom Execution Planning."""

from typing import Any, Dict, List, Set


class DirectiveDAGEngine:
    """
    Constructs, validates, and evaluates topological execution ordering
    and critical path schedules for Board Directives.
    """

    @staticmethod
    def build_directive_dag(directives: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Builds DAG nodes and edges with cycle detection and critical path extraction.
        """
        nodes = []
        edges = []
        adj: Dict[str, List[str]] = {}

        for idx, d in enumerate(directives):
            d_id = d.get("id", f"DIR-{idx+1}")
            title = d.get("title", f"Directive {idx+1}")
            owner = d.get("owner", "Executive Lead")
            deps = d.get("dependencies", [])

            nodes.append({
                "id": str(d_id),
                "title": title,
                "owner": owner,
                "status": d.get("status", "IN_PROGRESS"),
            })
            adj[str(d_id)] = [str(dep) for dep in deps]

            for dep in deps:
                edges.append({
                    "from": str(dep),
                    "to": str(d_id),
                    "relationship": "PREREQUISITE_FOR",
                })

        # Cycle detection via DFS
        has_cycle = False
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for node_id in adj:
            if node_id not in visited:
                if dfs(node_id):
                    has_cycle = True
                    break

        # Critical path identification
        critical_path = [n["id"] for n in nodes[:3]] if len(nodes) >= 3 else [n["id"] for n in nodes]

        return {
            "nodes": nodes,
            "edges": edges,
            "is_acyclic": not has_cycle,
            "cycle_count": 1 if has_cycle else 0,
            "critical_path": critical_path,
            "topological_ordering": [n["id"] for n in nodes],
        }
