import React from 'react';
import { GitBranch, CheckCircle2, PlayCircle, Clock, ArrowRight, ShieldAlert } from 'lucide-react';

interface DependencyNode {
  id: string;
  code: string;
  title: string;
  status: 'COMPLETED' | 'IN_PROGRESS' | 'SCHEDULED';
  owner: string;
}

interface Props {
  nodes?: DependencyNode[];
}

export const DependencyGraph: React.FC<Props> = ({
  nodes = [
    { id: '1', code: 'PREREQ-1', title: 'Customer Churn Cohort Segmentation', status: 'COMPLETED', owner: 'Data Engineering' },
    { id: '2', code: 'INIT-2026-001', title: 'Targeted Win-Back Campaign Launch', status: 'IN_PROGRESS', owner: 'VP Customer Success' },
    { id: '3', code: 'DOWNSTREAM-1', title: 'SE Regional Courier SLA Enforcement', status: 'IN_PROGRESS', owner: 'Logistics Operations' },
    { id: '4', code: 'OUTCOME', title: '+$180K ARR Retention Recovery Realized', status: 'SCHEDULED', owner: 'Executive Committee' },
  ],
}) => {
  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '12px',
      padding: '20px',
      marginBottom: '24px',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <GitBranch size={16} color="#38BDF8" />
          <h3 style={{ fontSize: '14px', fontWeight: 800, color: '#FFFFFF', margin: 0, textTransform: 'uppercase' }}>
            Initiative Dependency Graph & Execution Critical Path
          </h3>
        </div>
        <span style={{ fontSize: '10.5px', color: '#10B981', fontWeight: 700, background: 'rgba(16, 185, 129, 0.1)', padding: '2px 8px', borderRadius: '4px' }}>
          0 Unresolved Blockers
        </span>
      </div>

      {/* Visual DAG Nodes Strip */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'relative',
        gap: '8px',
        overflowX: 'auto',
      }}>
        {nodes.map((node, idx) => {
          const isDone = node.status === 'COMPLETED';
          const isCurrent = node.status === 'IN_PROGRESS';

          return (
            <React.Fragment key={node.id}>
              <div style={{
                background: isCurrent ? 'rgba(56, 189, 248, 0.08)' : isDone ? 'rgba(16, 185, 129, 0.06)' : '#05070B',
                border: `1px solid ${isCurrent ? '#38BDF8' : isDone ? '#10B981' : '#141C28'}`,
                borderRadius: '8px',
                padding: '12px 14px',
                minWidth: '180px',
                flex: 1,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ fontSize: '9.5px', fontWeight: 800, color: '#64748B', fontFamily: 'monospace' }}>
                    {node.code}
                  </span>

                  <span style={{
                    fontSize: '9px',
                    fontWeight: 800,
                    color: isDone ? '#10B981' : isCurrent ? '#38BDF8' : '#94A3B8',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '3px',
                  }}>
                    {isDone ? <CheckCircle2 size={10} /> : isCurrent ? <PlayCircle size={10} /> : <Clock size={10} />}
                    <span>{node.status}</span>
                  </span>
                </div>

                <div style={{ fontSize: '12px', fontWeight: 700, color: '#FFFFFF', lineHeight: 1.3, marginBottom: '6px' }}>
                  {node.title}
                </div>

                <span style={{ fontSize: '10px', color: '#94A3B8' }}>Owner: {node.owner}</span>
              </div>

              {idx < nodes.length - 1 && (
                <ArrowRight size={16} color="#334155" style={{ flexShrink: 0 }} />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
