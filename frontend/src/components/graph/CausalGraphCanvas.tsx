import React, { useRef, useState, useMemo } from 'react';
import { CausalGraphNode, CausalGraphEdge } from '../../types';
import { computeDagLayout, LayoutNode, LayoutEdge } from './dagLayout';

interface CausalGraphCanvasProps {
  nodes: CausalGraphNode[];
  edges: CausalGraphEdge[];
  selectedNodeId: string | null;
  selectedEdgeId: string | null;
  activeChainNodeIds?: string[];
  onSelectNode: (node: LayoutNode | null) => void;
  onSelectEdge: (edge: LayoutEdge | null) => void;
  selectedSeverity?: string;
  selectedCategory?: string;
  highlightRootsOnly?: boolean;
  zoom: number;
  panOffset: { x: number; y: number };
  onPanChange: (offset: { x: number; y: number }) => void;
  onZoomChange: (zoom: number) => void;
}

export const CausalGraphCanvas: React.FC<CausalGraphCanvasProps> = ({
  nodes,
  edges,
  selectedNodeId,
  selectedEdgeId,
  activeChainNodeIds = [],
  onSelectNode,
  onSelectEdge,
  selectedSeverity = 'ALL',
  selectedCategory = 'ALL',
  highlightRootsOnly = false,
  zoom,
  panOffset,
  onPanChange,
  onZoomChange,
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  // Compute Layout
  const layout = useMemo(() => {
    return computeDagLayout(nodes, edges, {
      nodeWidth: 220,
      nodeHeight: 92,
      rankSep: 140,
      nodeSep: 32,
    });
  }, [nodes, edges]);

  // Handle Pan
  const handleMouseDown = (e: React.MouseEvent<SVGSVGElement>) => {
    if ((e.target as HTMLElement).tagName === 'svg' || (e.target as HTMLElement).id === 'canvas-bg') {
      setIsDragging(true);
      setDragStart({ x: e.clientX - panOffset.x, y: e.clientY - panOffset.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent<SVGSVGElement>) => {
    if (isDragging) {
      onPanChange({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Handle Wheel Zoom
  const handleWheel = (e: React.WheelEvent<SVGSVGElement>) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
    const newZoom = Math.min(2.5, Math.max(0.4, zoom * zoomFactor));
    onZoomChange(newZoom);
  };

  // Node severity color mapping
  const getSeverityColor = (sev: string) => {
    switch (sev.toUpperCase()) {
      case 'CRITICAL':
        return 'var(--color-danger)';
      case 'HIGH':
        return 'var(--color-danger)';
      case 'MEDIUM':
        return 'var(--color-warning)';
      case 'LOW':
        return 'var(--color-primary-light)';
      default:
        return 'var(--text-muted)';
    }
  };

  const activeChainSet = useMemo(() => new Set(activeChainNodeIds), [activeChainNodeIds]);

  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        height: '540px',
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-default)',
        borderRadius: 'var(--radius-lg)',
        overflow: 'hidden',
        cursor: isDragging ? 'grabbing' : 'grab',
      }}
    >
      <svg
        ref={svgRef}
        width="100%"
        height="100%"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        style={{ display: 'block', userSelect: 'none' }}
      >
        <defs>
          {/* Default Arrow Marker */}
          <marker
            id="arrow-default"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="6"
            markerHeight="6"
            orient="auto-start-reverse"
          >
            <path d="M 0 1 L 10 5 L 0 9 z" fill="var(--color-primary)" />
          </marker>

          {/* Active / Highlighted Arrow Marker */}
          <marker
            id="arrow-active"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="7"
            markerHeight="7"
            orient="auto-start-reverse"
          >
            <path d="M 0 1 L 10 5 L 0 9 z" fill="var(--color-warning)" />
          </marker>

          {/* Glow Filter for Active Paths */}
          <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Canvas Background */}
        <rect id="canvas-bg" width="100%" height="100%" fill="transparent" />

        {/* Scaled & Panned Group */}
        <g transform={`translate(${panOffset.x}, ${panOffset.y}) scale(${zoom})`}>
          {/* Edges Layer */}
          {layout.edges.map((edge) => {
            const isSelected = selectedEdgeId === edge.id;
            const isInActiveChain =
              activeChainSet.has(edge.source_id) && activeChainSet.has(edge.target_id);

            const strokeColor = isSelected
              ? 'var(--color-warning)'
              : isInActiveChain
              ? 'var(--color-primary-light)'
              : 'rgba(59, 130, 246, 0.4)';

            const strokeWidth = isSelected || isInActiveChain ? 3 : 1.8;
            const markerEnd = isSelected || isInActiveChain ? 'url(#arrow-active)' : 'url(#arrow-default)';

            return (
              <g key={edge.id} onClick={() => onSelectEdge(edge)} style={{ cursor: 'pointer' }}>
                {/* Wider transparent hit area */}
                <path
                  d={edge.pathD}
                  fill="none"
                  stroke="transparent"
                  strokeWidth="14"
                />
                {/* Visible Edge */}
                <path
                  d={edge.pathD}
                  fill="none"
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  markerEnd={markerEnd}
                  strokeDasharray={edge.relationship_strength === 'WEAK' ? '4 4' : undefined}
                  filter={isInActiveChain || isSelected ? 'url(#glow)' : undefined}
                />
                {/* Edge Label on Midpoint */}
                <text
                  x={(edge.sourceX + edge.targetX) / 2}
                  y={(edge.sourceY + edge.targetY) / 2 - 8}
                  fill="var(--text-muted)"
                  fontSize="10"
                  textAnchor="middle"
                  style={{ pointerEvents: 'none', background: 'var(--bg-app)' }}
                >
                  {edge.relationship_type.replace('_', ' ')}
                </text>
              </g>
            );
          })}

          {/* Nodes Layer */}
          {layout.nodes.map((node) => {
            const isSelected = selectedNodeId === node.id;
            const isInActiveChain = activeChainSet.has(node.id);

            // Filter conditions
            const matchesSeverity =
              selectedSeverity === 'ALL' || node.severity.toUpperCase() === selectedSeverity;
            const matchesCategory =
              selectedCategory === 'ALL' || node.category.toUpperCase() === selectedCategory;
            const matchesRoots = !highlightRootsOnly || node.isRootCause;

            const isDimmed = !matchesSeverity || !matchesCategory || !matchesRoots;
            const sevColor = getSeverityColor(node.severity);

            return (
              <g
                key={node.id}
                transform={`translate(${node.x}, ${node.y})`}
                onClick={() => onSelectNode(isSelected ? null : node)}
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    onSelectNode(isSelected ? null : node);
                  }
                }}
                style={{
                  cursor: 'pointer',
                  opacity: isDimmed ? 0.3 : 1,
                  transition: 'opacity var(--transition-fast)',
                  outline: 'none',
                }}
              >
                {/* Card Background */}
                <rect
                  width={node.width}
                  height={node.height}
                  rx="8"
                  ry="8"
                  fill="var(--bg-surface-elevated)"
                  stroke={
                    isSelected
                      ? 'var(--color-primary-light)'
                      : isInActiveChain
                      ? 'var(--color-warning)'
                      : 'var(--border-default)'
                  }
                  strokeWidth={isSelected || isInActiveChain ? 2.5 : 1}
                  filter={isSelected || isInActiveChain ? 'url(#glow)' : undefined}
                />

                {/* Left Severity Accent Bar */}
                <rect
                  x="0"
                  y="0"
                  width="5"
                  height={node.height}
                  rx="3"
                  ry="3"
                  fill={sevColor}
                />

                {/* Category & Root Badge */}
                <text
                  x="12"
                  y="20"
                  fill="var(--text-muted)"
                  fontSize="10"
                  fontWeight="600"
                  style={{ textTransform: 'uppercase', letterSpacing: '0.04em' }}
                >
                  {node.category}
                </text>

                {node.isRootCause && (
                  <rect
                    x={node.width - 74}
                    y="10"
                    width="64"
                    height="16"
                    rx="4"
                    fill="rgba(245, 158, 11, 0.15)"
                    stroke="var(--color-warning)"
                    strokeWidth="1"
                  />
                )}
                {node.isRootCause && (
                  <text
                    x={node.width - 42}
                    y="21"
                    fill="var(--color-warning)"
                    fontSize="9"
                    fontWeight="700"
                    textAnchor="middle"
                  >
                    ROOT CAUSE
                  </text>
                )}

                {/* Node Title (Truncated) */}
                <text
                  x="12"
                  y="44"
                  fill="#ffffff"
                  fontSize="12"
                  fontWeight="600"
                  style={{ pointerEvents: 'none' }}
                >
                  {node.title.length > 24 ? `${node.title.slice(0, 24)}...` : node.title}
                </text>

                {/* Severity & Confidence Footer */}
                <text
                  x="12"
                  y="74"
                  fill={sevColor}
                  fontSize="10"
                  fontWeight="600"
                >
                  {node.severity}
                </text>

                <text
                  x={node.width - 12}
                  y="74"
                  fill="var(--text-muted)"
                  fontSize="10"
                  textAnchor="end"
                >
                  Conf: {(node.confidence_score * 100).toFixed(0)}%
                </text>
              </g>
            );
          })}
        </g>
      </svg>
    </div>
  );
};
