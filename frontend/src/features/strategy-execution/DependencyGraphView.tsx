import React from 'react';
import { GitMerge, AlertTriangle, ArrowRight, ShieldCheck, CheckCircle2, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';

export const DependencyGraphView: React.FC = () => {
  const dagNodes = [
    {
      code: 'INIT-2026-001',
      title: 'Secondary Hub SLA Enforcement',
      duration: '30 Days',
      status: 'IN_PROGRESS',
      isCritical: true,
      isBlocked: false,
    },
    {
      code: 'INIT-2026-002',
      title: 'Customer Win-Back Discount Automation',
      duration: '45 Days',
      status: 'IN_PROGRESS',
      isCritical: true,
      isBlocked: false,
    },
    {
      code: 'INIT-2026-003',
      title: 'Northern Hub Fulfillment Expansion',
      duration: '60 Days',
      status: 'PLANNED',
      isCritical: true,
      isBlocked: true,
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#38BDF8', fontWeight: 800 }}>
          Deterministic Strategy Dependency Layer
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Initiative Dependency Graph & Critical Path
        </h1>
      </div>

      {/* Critical Path Overview Bar */}
      <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>CRITICAL PATH DURATION</div>
          <div style={{ fontSize: '2rem', fontWeight: 900, color: '#38BDF8', marginTop: '2px' }}>135 Days</div>
        </div>
        <div>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>BLOCKING BOTTLENECKS</div>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#EF4444', marginTop: '2px' }}>1 Identified Blocker</div>
        </div>
        <div>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>DELAY RISK SCORE</div>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#10B981', marginTop: '2px' }}>LOW (3.2%)</div>
        </div>
      </div>

      {/* Interactive DAG Chain */}
      <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '32px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
        <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
          Critical Execution Sequence
        </h3>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
          {dagNodes.map((node, idx) => (
            <React.Fragment key={node.code}>
              <div
                style={{
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: `1px solid ${node.isBlocked ? '#EF4444' : '#10B981'}`,
                  borderRadius: '12px',
                  padding: '20px',
                  minWidth: '240px',
                  flex: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px',
                  position: 'relative',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '0.72rem', fontWeight: 800, color: '#38BDF8' }}>{node.code}</span>
                  <span style={{ fontSize: '0.68rem', fontWeight: 800, padding: '2px 6px', borderRadius: '4px', background: node.isBlocked ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)', color: node.isBlocked ? '#EF4444' : '#10B981' }}>
                    {node.isBlocked ? 'BLOCKED' : node.status}
                  </span>
                </div>
                <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#FFFFFF' }}>{node.title}</div>
                <div style={{ fontSize: '0.75rem', color: '#94A3B8' }}>Est. Duration: {node.duration}</div>
                {node.isBlocked && (
                  <div style={{ fontSize: '0.72rem', color: '#EF4444', fontWeight: 700, marginTop: '4px' }}>
                    ⚠️ Waiting for INIT-2026-002 completion
                  </div>
                )}
              </div>

              {idx < dagNodes.length - 1 && (
                <div style={{ color: '#64748B', display: 'flex', alignItems: 'center' }}>
                  <ArrowRight size={24} />
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
};
