import { CausalGraphNode, CausalGraphEdge } from '../../types';

export interface LayoutNode extends CausalGraphNode {
  x: number;
  y: number;
  width: number;
  height: number;
  rank: number;
  isRootCause: boolean;
  isTerminalEffect: boolean;
}

export interface LayoutEdge extends CausalGraphEdge {
  id: string;
  pathD: string;
  sourceX: number;
  sourceY: number;
  targetX: number;
  targetY: number;
}

export interface GraphLayoutResult {
  nodes: LayoutNode[];
  edges: LayoutEdge[];
  width: number;
  height: number;
}

export interface LayoutOptions {
  nodeWidth?: number;
  nodeHeight?: number;
  rankSep?: number;
  nodeSep?: number;
  paddingX?: number;
  paddingY?: number;
}

/**
 * Computes a deterministic layered DAG layout (Sugiyama-style topological ranking)
 * purely in TypeScript without external graph layout dependencies.
 */
export function computeDagLayout(
  nodes: CausalGraphNode[],
  edges: CausalGraphEdge[],
  options: LayoutOptions = {}
): GraphLayoutResult {
  const nodeWidth = options.nodeWidth ?? 220;
  const nodeHeight = options.nodeHeight ?? 90;
  const rankSep = options.rankSep ?? 160;
  const nodeSep = options.nodeSep ?? 40;
  const paddingX = options.paddingX ?? 60;
  const paddingY = options.paddingY ?? 60;

  if (!nodes || nodes.length === 0) {
    return { nodes: [], edges: [], width: 400, height: 300 };
  }

  // 1. Build in-degree and adjacency maps
  const inDegree: Record<string, number> = {};
  const outDegree: Record<string, number> = {};
  const forwardAdj: Record<string, string[]> = {};
  const reverseAdj: Record<string, string[]> = {};

  nodes.forEach((n) => {
    inDegree[n.id] = 0;
    outDegree[n.id] = 0;
    forwardAdj[n.id] = [];
    reverseAdj[n.id] = [];
  });

  edges.forEach((e) => {
    if (inDegree[e.target_id] !== undefined) inDegree[e.target_id]++;
    if (outDegree[e.source_id] !== undefined) outDegree[e.source_id]++;
    if (forwardAdj[e.source_id]) forwardAdj[e.source_id].push(e.target_id);
    if (reverseAdj[e.target_id]) reverseAdj[e.target_id].push(e.source_id);
  });

  // 2. Compute topological rank (Layer assignment) using longest path from root causes
  const ranks: Record<string, number> = {};
  nodes.forEach((n) => {
    ranks[n.id] = 0;
  });

  // Queue of nodes with in-degree 0 (Root Causes)
  const queue: string[] = nodes.filter((n) => inDegree[n.id] === 0).map((n) => n.id);

  // If all nodes have in-degrees (e.g. disconnected or cyclic edge edge-cases), start with first node
  if (queue.length === 0 && nodes.length > 0) {
    queue.push(nodes[0].id);
  }

  const visited = new Set<string>();
  while (queue.length > 0) {
    const currId = queue.shift()!;
    visited.add(currId);
    const currRank = ranks[currId];

    for (const targetId of forwardAdj[currId] || []) {
      ranks[targetId] = Math.max(ranks[targetId] || 0, currRank + 1);
      if (!visited.has(targetId)) {
        queue.push(targetId);
      }
    }
  }

  // Group nodes by rank
  const rankGroups: Record<number, CausalGraphNode[]> = {};
  let maxRank = 0;

  nodes.forEach((node) => {
    const r = ranks[node.id] || 0;
    if (r > maxRank) maxRank = r;
    if (!rankGroups[r]) rankGroups[r] = [];
    rankGroups[r].push(node);
  });

  // 3. Compute coordinates for each node
  const layoutNodes: LayoutNode[] = [];
  const nodePositionMap: Record<string, { x: number; y: number }> = {};
  let maxColumnHeight = 0;

  for (let r = 0; r <= maxRank; r++) {
    const group = rankGroups[r] || [];
    const colX = paddingX + r * (nodeWidth + rankSep);
    const totalColH = group.length * nodeHeight + Math.max(0, group.length - 1) * nodeSep;
    if (totalColH > maxColumnHeight) maxColumnHeight = totalColH;

    group.forEach((node, idx) => {
      const nodeY = paddingY + idx * (nodeHeight + nodeSep);
      const isRoot = (inDegree[node.id] || 0) === 0;
      const isTerminal = (outDegree[node.id] || 0) === 0;

      const lNode: LayoutNode = {
        ...node,
        x: colX,
        y: nodeY,
        width: nodeWidth,
        height: nodeHeight,
        rank: r,
        isRootCause: isRoot,
        isTerminalEffect: isTerminal,
      };

      layoutNodes.push(lNode);
      nodePositionMap[node.id] = { x: colX, y: nodeY };
    });
  }

  // 4. Compute layout edges and cubic bezier paths (from source right edge to target left edge)
  const layoutEdges: LayoutEdge[] = [];
  edges.forEach((edge, idx) => {
    const srcPos = nodePositionMap[edge.source_id];
    const tgtPos = nodePositionMap[edge.target_id];

    if (srcPos && tgtPos) {
      const srcX = srcPos.x + nodeWidth;
      const srcY = srcPos.y + nodeHeight / 2;
      const tgtX = tgtPos.x;
      const tgtY = tgtPos.y + nodeHeight / 2;

      // Cubic bezier curve control points
      const dx = Math.max(40, (tgtX - srcX) * 0.5);
      const cp1X = srcX + dx;
      const cp1Y = srcY;
      const cp2X = tgtX - dx;
      const cp2Y = tgtY;

      const pathD = `M ${srcX} ${srcY} C ${cp1X} ${cp1Y}, ${cp2X} ${cp2Y}, ${tgtX} ${tgtY}`;

      layoutEdges.push({
        ...edge,
        id: `edge-${edge.source_id}-${edge.target_id}-${idx}`,
        pathD,
        sourceX: srcX,
        sourceY: srcY,
        targetX: tgtX,
        targetY: tgtY,
      });
    }
  });

  const totalWidth = paddingX * 2 + (maxRank + 1) * nodeWidth + maxRank * rankSep;
  const totalHeight = paddingY * 2 + maxColumnHeight;

  return {
    nodes: layoutNodes,
    edges: layoutEdges,
    width: Math.max(600, totalWidth),
    height: Math.max(400, totalHeight),
  };
}
