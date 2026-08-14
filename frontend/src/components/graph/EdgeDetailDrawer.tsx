import React from 'react';
import { X, ArrowRight, Zap, Target } from 'lucide-react';
import { LayoutEdge, LayoutNode } from './dagLayout';
import { RootCauseAnalysisRecord } from '../../types';

interface EdgeDetailDrawerProps {
  edge: LayoutEdge | null;
  nodes: LayoutNode[];
  analyses: RootCauseAnalysisRecord[];
  onClose: () => void;
}

export const EdgeDetailDrawer: React.FC<EdgeDetailDrawerProps> = ({
  edge,
  nodes,
  analyses,
  onClose,
}) => {
  if (!edge) return null;

  const sourceNode = nodes.find((n) => n.id === edge.source_id);
  const targetNode = nodes.find((n) => n.id === edge.target_id);

  // Find exact matching analysis record from backend
  const matchingAnalysis = analyses.find(
    (a) => a.root_cause_finding_id === edge.source_id && a.primary_finding_id === edge.target_id
  );

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
          <span className="badge badge-warning" style={{ marginBottom: '4px' }}>
            Validated Causal Link
          </span>
          <h3 style={{ fontSize: '1.05rem', color: '#ffffff' }}>
            {edge.relationship_type.replace('_', ' ')}
          </h3>
        </div>
        <button onClick={onClose} className="btn btn-ghost btn-sm" aria-label="Close details">
          <X size={16} />
        </button>
      </div>

      {/* Cause -> Effect Flow Card */}
      <div
        style={{
          backgroundColor: 'var(--bg-app)',
          padding: '12px 14px',
          borderRadius: 'var(--radius-sm)',
          marginBottom: '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
        }}
      >
        <div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
            CAUSAL DRIVER (CAUSE)
          </div>
          <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--color-warning)' }}>
            {sourceNode?.title || edge.source_id}
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <ArrowRight size={18} color="var(--color-primary-light)" />
        </div>

        <div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
            BUSINESS SYMPTOM (EFFECT)
          </div>
          <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--color-danger)' }}>
            {targetNode?.title || edge.target_id}
          </div>
        </div>
      </div>

      {/* Causal Metrics */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '10px',
          marginBottom: '16px',
        }}
      >
        <div style={{ backgroundColor: 'var(--bg-app)', padding: '10px', borderRadius: 'var(--radius-sm)' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>STRENGTH</div>
          <div style={{ fontWeight: 600, color: '#ffffff' }}>{edge.relationship_strength}</div>
        </div>

        <div style={{ backgroundColor: 'var(--bg-app)', padding: '10px', borderRadius: 'var(--radius-sm)' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>IMPACT SCORE</div>
          <div style={{ fontWeight: 600, color: 'var(--color-primary-light)' }}>
            {(edge.impact_score * 100).toFixed(0)}%
          </div>
        </div>
      </div>

      {/* Explanatory Narrative from Backend */}
      {matchingAnalysis?.explanation && (
        <div style={{ marginBottom: '16px' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
            Causal Mechanism & Explanation:
          </span>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5, marginTop: '4px' }}>
            {matchingAnalysis.explanation}
          </p>
        </div>
      )}

      {/* Supporting Evidence Snapshot (If Available) */}
      {matchingAnalysis?.supporting_evidence && (
        <div>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
            Statistical Evidence Snapshot:
          </span>
          <pre
            style={{
              marginTop: '4px',
              padding: '10px',
              backgroundColor: 'var(--bg-app)',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.75rem',
              color: 'var(--text-secondary)',
              overflowX: 'auto',
              fontFamily: 'var(--font-mono)',
            }}
          >
            {JSON.stringify(matchingAnalysis.supporting_evidence, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};
