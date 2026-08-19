import React, { useState } from 'react';
import { CheckSquare, ShieldCheck, Play, ArrowRight, CheckCircle2, AlertTriangle, ChevronRight, FileText } from 'lucide-react';
import { ExplainabilityDrawer } from '../../components/workspace/ExplainabilityDrawer';

export const DecisionCopilotView: React.FC = () => {
  const [sessionStatus, setSessionStatus] = useState<'PROPOSED' | 'APPROVED' | 'EXECUTING'>('APPROVED');
  const [isExplainOpen, setIsExplainOpen] = useState(false);

  const rankedOptions = [
    { rank: 1, name: 'Recovery Path A: Retention First & Courier SLA Fix', expected_arr: '+$124,000', health_lift: '+11.0 pts', confidence: 0.94, selected: true },
    { rank: 2, name: 'Recovery Path B: Growth First & Regional Expansion', expected_arr: '+$98,000', health_lift: '+7.5 pts', confidence: 0.88, selected: false },
    { rank: 3, name: 'Recovery Path C: Conservative Minimum Intervention', expected_arr: '+$45,000', health_lift: '+3.2 pts', confidence: 0.79, selected: false },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#F59E0B', fontWeight: 800 }}>
            Boardroom Decision Intelligence & Governance
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Strategic Decision Copilot
          </h1>
        </div>

        {/* Status Pill */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '6px 14px', borderRadius: '20px' }}>
          <CheckCircle2 size={14} color="#10B981" />
          <span style={{ fontSize: '0.78rem', color: '#10B981', fontWeight: 800 }}>Decision Session: {sessionStatus}</span>
        </div>
      </div>

      {/* Main Boardroom Decision Package Card */}
      <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '12px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '18px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#38BDF8', fontWeight: 800 }}>
              Boardroom Decision Package
            </div>
            <h2 style={{ fontSize: '1.3rem', fontWeight: 800, color: '#FFFFFF', margin: '4px 0 0 0' }}>
              Ratified Directive: Recovery Path A (Retention First)
            </h2>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '14px' }}>
          <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '14px', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 700 }}>EXPECTED ARR RECOVERY</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#10B981', marginTop: '2px' }}>+$124,000</div>
          </div>
          <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '14px', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 700 }}>PORTFOLIO HEALTH LIFT</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#38BDF8', marginTop: '2px' }}>+11.0 pts</div>
          </div>
          <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '14px', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 700 }}>RISK REDUCTION</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#F59E0B', marginTop: '2px' }}>-10.2 pts</div>
          </div>
          <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '14px', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 700 }}>DECISION CONFIDENCE</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#A855F7', marginTop: '2px' }}>94.0%</div>
          </div>
        </div>

        {/* Ranked Options Table */}
        <div>
          <div style={{ fontSize: '0.85rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '10px' }}>
            Ranked Strategic Alternative Paths
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {rankedOptions.map((opt) => (
              <div
                key={opt.rank}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '12px 16px',
                  background: opt.selected ? 'rgba(56, 189, 248, 0.1)' : 'rgba(15, 23, 42, 0.6)',
                  border: `1px solid ${opt.selected ? '#38BDF8' : '#1E293B'}`,
                  borderRadius: '8px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 800, color: opt.selected ? '#38BDF8' : '#64748B' }}>
                    #{opt.rank}
                  </span>
                  <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#FFFFFF' }}>{opt.name}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 800, color: '#10B981' }}>{opt.expected_arr}</span>
                  <span style={{ fontSize: '0.78rem', color: '#A855F7', fontWeight: 700 }}>{Math.round(opt.confidence * 100)}% Conf</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Governance Transition Buttons */}
        <div style={{ display: 'flex', gap: '12px', borderTop: '1px solid #1E293B', paddingTop: '16px' }}>
          <button
            onClick={() => setSessionStatus('EXECUTING')}
            style={{
              padding: '10px 20px',
              background: '#0284C7',
              border: 'none',
              borderRadius: '6px',
              color: '#FFFFFF',
              fontSize: '0.85rem',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            Transition to EXECUTING
          </button>
          <button
            onClick={() => setIsExplainOpen(true)}
            style={{
              padding: '10px 20px',
              background: 'rgba(30, 41, 59, 0.8)',
              border: '1px solid #334155',
              borderRadius: '6px',
              color: '#F1F5F9',
              fontSize: '0.85rem',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            Inspect Decision Provenance
          </button>
        </div>
      </div>

      {/* Explainability Drawer */}
      <ExplainabilityDrawer
        isOpen={isExplainOpen}
        onClose={() => setIsExplainOpen(false)}
        title="Decision Session Ratification Provenance"
        metricValue="Recovery Path A — +$124,000 Expected ARR"
      />
    </div>
  );
};
