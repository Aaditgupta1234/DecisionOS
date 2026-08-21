import React, { useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  Node,
  Edge,
  MarkerType,
  Position,
  Handle,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Info } from 'lucide-react';
import { CausalGraphData, CausalGraphEdge, CausalGraphNode } from '../../../types';

export interface CausalNodeData {
  label: string;
  category?: string;
  severity?: string;
  confidence?: number;
  isRoot?: boolean;
  isDriver?: boolean;
  isMetric?: boolean;
  [key: string]: any;
}

const CustomCausalNode = ({ data, selected }: { data: CausalNodeData; selected: boolean }) => {
  const isRoot = data.isRoot;
  const isMetric = data.isMetric;

  return (
    <div style={{
      background: selected
        ? 'rgba(56, 189, 248, 0.18)'
        : isRoot
        ? '#130B10'
        : isMetric
        ? '#08121A'
        : '#090D14',
      border: `1.5px solid ${selected ? '#38BDF8' : isRoot ? '#EF4444' : isMetric ? '#0284C7' : '#1E293B'}`,
      borderRadius: '8px',
      padding: '12px 14px',
      minWidth: '200px',
      maxWidth: '240px',
      color: '#FFFFFF',
      boxShadow: selected ? '0 0 16px rgba(56, 189, 248, 0.4)' : '0 8px 20px rgba(0, 0, 0, 0.6)',
      fontSize: '12px',
      fontFamily: 'Inter, system-ui, sans-serif',
      transition: 'all 0.15s ease',
    }}>
      <Handle type="target" position={Position.Top} style={{ background: '#38BDF8', width: '6px', height: '6px' }} />

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
        <span style={{
          fontSize: '9.5px',
          fontWeight: 800,
          color: isRoot ? '#F87171' : isMetric ? '#38BDF8' : '#F59E0B',
          textTransform: 'uppercase',
          letterSpacing: '0.04em',
        }}>
          {isRoot ? 'ROOT CAUSE' : isMetric ? 'AFFECTED METRIC' : 'DIAGNOSTIC FINDING'}
        </span>

        {data.confidence !== undefined && (
          <span style={{ fontSize: '9px', color: '#64748B', fontWeight: 600 }}>
            {data.confidence}% conf
          </span>
        )}
      </div>

      <div style={{ fontWeight: 700, fontSize: '12px', color: '#FFFFFF', marginBottom: '4px', lineHeight: 1.3 }}>
        {data.label}
      </div>

      {data.severity && (
        <div style={{ fontSize: '10.5px', color: '#94A3B8', fontWeight: 600 }}>
          Severity: <span style={{ color: '#E2E8F0', fontWeight: 700 }}>{data.severity}</span>
        </div>
      )}

      <Handle type="source" position={Position.Bottom} style={{ background: '#38BDF8', width: '6px', height: '6px' }} />
    </div>
  );
};

const nodeTypes = {
  causalNode: CustomCausalNode,
};

interface Props {
  graph?: CausalGraphData;
  onSelectNode?: (nodeId: string, nodeData: CausalNodeData) => void;
}

export const ReactFlowCausalGraph: React.FC<Props> = ({ graph, onSelectNode }) => {
  const { nodes: flowNodes, edges: flowEdges } = useMemo(() => {
    const rawNodes: CausalGraphNode[] = graph?.nodes || [];
    const rawEdges: CausalGraphEdge[] = graph?.edges || [];

    const sourceIds = new Set(rawEdges.map((e: CausalGraphEdge) => e.source_id));
    const targetIds = new Set(rawEdges.map((e: CausalGraphEdge) => e.target_id));

    const nodes: Node[] = rawNodes.map((n: CausalGraphNode, idx: number) => {
      const isRoot = sourceIds.has(n.id) && !targetIds.has(n.id);
      const isMetric = targetIds.has(n.id);

      const col = idx % 2;
      const row = Math.floor(idx / 2);

      return {
        id: n.id,
        type: 'causalNode',
        position: { x: 80 + col * 280, y: 60 + row * 160 },
        data: {
          label: n.title,
          category: n.category,
          severity: n.severity,
          confidence: Math.round((n.confidence_score || 0.9) * 100),
          isRoot,
          isMetric,
        },
      };
    });

    const edges: Edge[] = rawEdges.map((e: CausalGraphEdge) => ({
      id: `e-${e.source_id}-${e.target_id}`,
      source: e.source_id,
      target: e.target_id,
      animated: true,
      style: { stroke: '#EF4444', strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: '#EF4444' },
    }));

    return { nodes, edges };
  }, [graph]);

  const [nodes, setNodes, onNodesChange] = useNodesState(flowNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(flowEdges);

  React.useEffect(() => {
    setNodes(flowNodes);
    setEdges(flowEdges);
  }, [flowNodes, flowEdges, setNodes, setEdges]);

  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      if (onSelectNode) {
        onSelectNode(node.id, node.data as CausalNodeData);
      }
    },
    [onSelectNode]
  );

  const hasEdges = (graph?.edges?.length ?? 0) > 0;

  return (
    <div style={{
      width: '100%',
      height: '460px',
      background: '#040609',
      border: '1px solid #1A2230',
      borderRadius: '12px',
      overflow: 'hidden',
      position: 'relative',
    }}>
      {!hasEdges && (
        <div style={{
          position: 'absolute',
          top: '12px',
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 10,
          background: 'rgba(15, 23, 42, 0.9)',
          border: '1px solid rgba(56, 189, 248, 0.3)',
          borderRadius: '6px',
          padding: '6px 14px',
          fontSize: '11.5px',
          fontWeight: 600,
          color: '#38BDF8',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          backdropFilter: 'blur(4px)',
        }}>
          <Info size={14} color="#38BDF8" />
          <span>No validated causal relationships identified for the current dataset.</span>
        </div>
      )}

      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        onNodeClick={handleNodeClick}
        fitView
        attributionPosition="bottom-right"
      >
        <Background variant={BackgroundVariant.Dots} gap={16} size={1} color="#141C28" />
        <Controls
          style={{
            background: '#090D14',
            border: '1px solid #1E293B',
            borderRadius: '6px',
            fill: '#94A3B8',
          }}
        />
      </ReactFlow>
    </div>
  );
};
