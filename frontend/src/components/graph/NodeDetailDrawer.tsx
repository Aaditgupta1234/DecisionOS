import React from 'react';
import { X, ShieldAlert, GitCommit, ArrowRight, CheckCircle2 } from 'lucide-react';
import { LayoutNode } from './dagLayout';
import { RootCauseAnalysisRecord } from '../../types';
import { Link } from 'react-router-dom';

interface NodeDetailDrawerProps {
  node: LayoutNode | null;
  analyses: RootCauseAnalysisRecord[];
  onClose: () => void;
  onSelectRelatedNodeId?: (nodeId: string) => void;
}

export const NodeDetailDrawer: React.FC<NodeDetailDrawerProps> = ({
  node,
  analyses,
  onClose,
  onSelectRelatedNodeId,
}) => {
  if (!node) return null;

  // Upstream drivers where this node is the effect (target)
  const upstreamAnalyses = analyses.filter((a) => a.primary_finding_id === node.id);
  // Downstream effects where this node is the cause (driver)
  const downstreamAnalyses = analyses.filter((a) => a.root_cause_finding_id === node.id);

  return (
    <div
      style={{
        width: '360px',
        backgroundColor: 'var(--bg-surface-elevated)',
        borderLeft: '1px solid var(--border-default)',
        borderRadius: 'var(--radius-lg)',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        maxHeight: '540px',
        overflowY: 'auto',
        padding: '20px',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
            <span
              className={`badge ${
                node.severity === 'CRITICAL' || node.severity === 'HIGH'
                  ? 'badge-danger'
                  : node.severity === 'MEDIUM'
                  ? 'badge-warning'
                  : 'badge-primary'
              }`}
            >
              {node.severity}
            </span>
            <span className="badge badge-neutral">{node.category}</span>
            {node.isRootCause && <span className="badge badge-warning">Root Origin</span>}
          </div>
          <h3 style={{ fontSize: '1.1rem', color: '#ffffff' }}>{node.title}</h3>
        </div>
        <button onClick={onClose} className="btn btn-ghost btn-sm" aria-label="Close details">
          <X size={16} />
        </button>
      </div>

      {/* Confidence & Subtype */}
      <div
        style={{
          backgroundColor: 'var(--bg-app)',
          padding: '12px',
          borderRadius: 'var(--radius-sm)',
          marginBottom: '16px',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '6px' }}>
          <span style={{ color: 'var(--text-muted)' }}>Confidence Level:</span>
          <strong style={{ color: 'var(--color-success)' }}>
            {(node.confidence_score * 100).toFixed(0)}%
          </strong>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
          <span style={{ color: 'var(--text-muted)' }}>Finding Subtype:</span>
          <span style={{ color: 'var(--text-main)', fontFamily: 'var(--font-mono)' }}>{node.subtype}</span>
        </div>
      </div>

      {/* Downstream Business Effects (Triggered by this node) */}
      <div style={{ marginBottom: '18px' }}>
        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
          Triggers Downstream Effects ({downstreamAnalyses.length}):
        </span>
        {downstreamAnalyses.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '8px' }}>
            {downstreamAnalyses.map((a) => (
              <div
                key={a.id}
                onClick={() => onSelectRelatedNodeId?.(a.primary_finding_id)}
                style={{
                  padding: '8px 10px',
                  backgroundColor: 'var(--bg-app)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.8rem',
                  cursor: 'pointer',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2px' }}>
                  <span style={{ fontWeight: 600, color: 'var(--color-primary-light)' }}>
                    {a.relationship_type.replace('_', ' ')}
                  </span>
                  <span className="badge badge-neutral" style={{ fontSize: '0.65rem' }}>
                    Impact: {(a.impact_score * 100).toFixed(0)}%
                  </span>
                </div>
                <div style={{ color: 'var(--text-main)' }}>
                  {a.primary_finding?.title || a.primary_finding_id}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Terminal business outcome (does not trigger further symptoms).
          </div>
        )}
      </div>

      {/* Upstream Causes (Initiating this node) */}
      <div style={{ marginBottom: '18px' }}>
        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
          Driven By Upstream Causes ({upstreamAnalyses.length}):
        </span>
        {upstreamAnalyses.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '8px' }}>
            {upstreamAnalyses.map((a) => (
              <div
                key={a.id}
                onClick={() => onSelectRelatedNodeId?.(a.root_cause_finding_id)}
                style={{
                  padding: '8px 10px',
                  backgroundColor: 'var(--bg-app)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.8rem',
                  cursor: 'pointer',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2px' }}>
                  <span style={{ fontWeight: 600, color: 'var(--color-warning)' }}>
                    {a.relationship_type.replace('_', ' ')}
                  </span>
                  <span className="badge badge-neutral" style={{ fontSize: '0.65rem' }}>
                    {a.relationship_strength}
                  </span>
                </div>
                <div style={{ color: 'var(--text-main)' }}>
                  {a.root_cause_finding?.title || a.root_cause_finding_id}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Independent root origin (no upstream causes detected).
          </div>
        )}
      </div>

      {/* Action Navigation */}
      <div style={{ marginTop: 'auto', paddingTop: '14px', borderTop: '1px solid var(--border-subtle)' }}>
        <Link to="/recommendations" className="btn btn-secondary btn-sm" style={{ width: '100%', justifyContent: 'center' }}>
          <span>View Prescribed Actions</span>
          <ArrowRight size={14} />
        </Link>
      </div>
    </div>
  );
};
