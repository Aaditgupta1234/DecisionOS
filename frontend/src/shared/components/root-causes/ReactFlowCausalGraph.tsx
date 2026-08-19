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
import { ShieldCheck, GitMerge, AlertTriangle, TrendingDown } from 'lucide-react';

export interface CausalNodeData {
  label: string;
  category?: string;
  impactScore?: string;
  confidence?: number;
  isRoot?: boolean;
  isDriver?: boolean;
  isMetric?: boolean;
  [key: string]: any;
}

// Custom Node Renderer with Glassmorphic Executive Styling
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
      minWidth: '180px',
      maxWidth: '220px',
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
          {isRoot ? 'ROOT CAUSE' : isMetric ? 'AFFECTED METRIC' : 'DRIVER FACTOR'}
        </span>

        {data.confidence && (
          <span style={{ fontSize: '9px', color: '#64748B', fontWeight: 600 }}>
            {data.confidence}% conf
          </span>
        )}
      </div>

      <div style={{ fontWeight: 700, fontSize: '12px', color: '#FFFFFF', marginBottom: '4px', lineHeight: 1.3 }}>
        {data.label}
      </div>

      {data.impactScore && (
        <div style={{ fontSize: '11px', color: isRoot ? '#EF4444' : '#10B981', fontWeight: 700 }}>
          {data.impactScore}
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
  onSelectNode?: (nodeId: string, nodeData: CausalNodeData) => void;
}

export const ReactFlowCausalGraph: React.FC<Props> = ({ onSelectNode }) => {
  const initialNodes: Node[] = [
    {
      id: 'node-root',
      type: 'causalNode',
      position: { x: 260, y: 30 },
      data: {
        label: 'Courier Transit Delays (SE Corridor)',
        isRoot: true,
        impactScore: '-$104.6K Impact',
        confidence: 94,
      },
    },
    {
      id: 'node-driver-1',
      type: 'causalNode',
      position: { x: 100, y: 170 },
      data: {
        label: 'Late Delivery Review Rating Drop',
        isDriver: true,
        impactScore: '2.1★ Avg Rating',
        confidence: 92,
      },
    },
    {
      id: 'node-driver-2',
      type: 'causalNode',
      position: { x: 420, y: 170 },
      data: {
        label: 'Customer Churn in Southeastern Region',
        isDriver: true,
        impactScore: '-4.3% Retention Delta',
        confidence: 91,
      },
    },
    {
      id: 'node-metric-1',
      type: 'causalNode',
      position: { x: 100, y: 310 },
      data: {
        label: 'Customer Retention Rate (85.8%)',
        isMetric: true,
        impactScore: '-$78K ARR',
        confidence: 96,
      },
    },
    {
      id: 'node-metric-2',
      type: 'causalNode',
      position: { x: 420, y: 310 },
      data: {
        label: 'Total Net Revenue ($4.2M)',
        isMetric: true,
        impactScore: '-$218K Net Impact',
        confidence: 98,
      },
    },
  ];

  const initialEdges: Edge[] = [
    {
      id: 'e-root-d1',
      source: 'node-root',
      target: 'node-driver-1',
      animated: true,
      style: { stroke: '#EF4444', strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: '#EF4444' },
    },
    {
      id: 'e-root-d2',
      source: 'node-root',
      target: 'node-driver-2',
      animated: true,
      style: { stroke: '#EF4444', strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: '#EF4444' },
    },
    {
      id: 'e-d1-m1',
      source: 'node-driver-1',
      target: 'node-metric-1',
      style: { stroke: '#38BDF8', strokeWidth: 1.5 },
      markerEnd: { type: MarkerType.ArrowClosed, color: '#38BDF8' },
    },
    {
      id: 'e-d2-m2',
      source: 'node-driver-2',
      target: 'node-metric-2',
      style: { stroke: '#38BDF8', strokeWidth: 1.5 },
      markerEnd: { type: MarkerType.ArrowClosed, color: '#38BDF8' },
    },
  ];

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      if (onSelectNode) {
        onSelectNode(node.id, node.data as CausalNodeData);
      }
    },
    [onSelectNode]
  );

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
