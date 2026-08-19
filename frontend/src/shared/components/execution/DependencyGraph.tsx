import React from 'react';
import { GitBranch, CheckCircle2, PlayCircle, Clock, ArrowRight, ShieldAlert, Lock, AlertCircle, Zap } from 'lucide-react';
import { DependencyType } from '../../utils/InitiativeDependencyGuard';

export interface DependencyNode {
  id: string;
  code: string;
  title: string;
  type?: DependencyType;
  status: 'COMPLETED' | 'IN_PROGRESS' | 'SCHEDULED';
  owner: string;
}

interface Props {
  nodes?: DependencyNode[];
}

export const DependencyGraph: React.FC<Props> = ({
  nodes = [
    { id: '1', code: 'PREREQ-1', title: 'Customer Churn Cohort Segmentation', type: 'HARD_BLOCKER', status: 'COMPLETED', owner: 'Data Engineering' },
    { id: '2', code: 'INIT-2026-001', title: 'Targeted Win-Back Campaign Launch', type: 'HARD_BLOCKER', status: 'IN_PROGRESS', owner: 'VP Customer Success' },
    { id: '3', code: 'DOWNSTREAM-1', title: 'SE Regional Courier SLA Concession', type: 'EXTERNAL', status: 'IN_PROGRESS', owner: 'Logistics Operations' },
    { id: '4', code: 'OUTCOME', title: '+$180K ARR Retention Recovery Realized', type: 'SOFT_BLOCKER', status: 'SCHEDULED', owner: 'Executive Committee' },
  ],
}) => {
  const getBadgeColor = (type?: DependencyType) => {
    switch (type) {
      case 'HARD_BLOCKER':
        return '#EF4444';
      case 'SOFT_BLOCKER':
        return '#F59E0B';
      case 'EXTERNAL':
        return '#A855F7';
      default:
        return '#38BDF8';
    }
  };

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

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '10px', color: '#EF4444', background: 'rgba(239, 68, 68, 0.1)', padding: '2px 6px', borderRadius: '4px', fontWeight: 700 }}>
            HARD_BLOCKER: Enforced
          </span>
          <span style={{ fontSize: '10px', color: '#F59E0B', background: 'rgba(245, 158, 11, 0.1)', padding: '2px 6px', borderRadius: '4px', fontWeight: 700 }}>
            SOFT_BLOCKER: Warning
          </span>
          <span style={{ fontSize: '10px', color: '#A855F7', background: 'rgba(168, 85, 247, 0.1)', padding: '2px 6px', borderRadius: '4px', fontWeight: 700 }}>
            EXTERNAL: Risk Flag
          </span>
        </div>
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
          const typeColor = getBadgeColor(node.type);

          return (
            <React.Fragment key={node.id}>
              <div style={{
                background: isCurrent ? 'rgba(56, 189, 248, 0.08)' : isDone ? 'rgba(16, 185, 129, 0.06)' : '#05070B',
                border: `1px solid ${isCurrent ? '#38BDF8' : isDone ? '#10B981' : '#141C28'}`,
                borderRadius: '8px',
                padding: '12px 14px',
                minWidth: '190px',
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

                {node.type && (
                  <span style={{
                    fontSize: '8.5px',
                    fontWeight: 800,
                    color: typeColor,
                    display: 'inline-block',
                    marginBottom: '3px',
                    textTransform: 'uppercase',
                  }}>
                    {node.type}
                  </span>
                )}

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
