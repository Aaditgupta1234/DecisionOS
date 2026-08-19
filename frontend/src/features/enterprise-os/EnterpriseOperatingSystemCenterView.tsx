import React, { useState } from 'react';
import {
  Play,
  Layers,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  DollarSign,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react';

export const EnterpriseOperatingSystemCenterView: React.FC = () => {
  const [executedPlaybook, setExecutedPlaybook] = useState<string | null>(null);

  const templates = [
    {
      code: 'PBT-RETENTION-RECOVERY',
      name: 'Autonomous Retention Recovery & Governance Playbook',
      trigger: 'Monitoring Alert (Retention Drift < -5.0%)',
      stepsCount: 5,
      cost: '$0.14 / run',
      status: 'ACTIVE_AUTONOMOUS',
    },
    {
      code: 'PBT-BENCHMARK-GROWTH',
      name: 'Competitive Benchmark Opportunity Execution Playbook',
      trigger: 'Benchmark Gap (> 5.0% to Top Quartile)',
      stepsCount: 3,
      cost: '$0.09 / run',
      status: 'ACTIVE_AUTONOMOUS',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#A855F7', fontWeight: 800 }}>
          Autonomous Enterprise Coordination
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Enterprise OS Playbook Studio & Execution Stream
        </h1>
      </div>

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>WORKFLOW SUCCESS RATE</div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#10B981' }}>97.2%</div>
          <div style={{ fontSize: '0.75rem', color: '#10B981', fontWeight: 700 }}>240ms Avg Duration</div>
        </div>

        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>AUTONOMOUS ACTION RATE</div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#38BDF8' }}>95.0%</div>
          <div style={{ fontSize: '0.75rem', color: '#94A3B8', fontWeight: 700 }}>Guarded by Human Approval Gates</div>
        </div>

        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>RECOVERY SUCCESS RATE</div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#A855F7' }}>91.4%</div>
          <div style={{ fontSize: '0.75rem', color: '#A855F7', fontWeight: 700 }}>Automated Retry & Compensation Rollbacks</div>
        </div>

        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>AVG COMPUTE COST</div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#F59E0B' }}>$0.14</div>
          <div style={{ fontSize: '0.75rem', color: '#F59E0B', fontWeight: 700 }}>Per Autonomous Pipeline Run</div>
        </div>
      </div>

      {/* Playbook Templates Library */}
      <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Reusable Enterprise Playbook Templates</span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Declarative Step Graphs</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {templates.map((tpl) => (
            <div
              key={tpl.code}
              style={{
                background: 'rgba(15, 23, 42, 0.6)',
                border: '1px solid #1E293B',
                borderRadius: '10px',
                padding: '20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '14px',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '0.7rem', fontWeight: 800, padding: '2px 8px', borderRadius: '4px', background: 'rgba(168, 85, 247, 0.15)', color: '#A855F7' }}>
                    {tpl.code}
                  </span>
                  <span style={{ fontSize: '0.98rem', fontWeight: 800, color: '#FFFFFF' }}>{tpl.name}</span>
                </div>
                <div style={{ fontSize: '0.78rem', color: '#94A3B8', marginTop: '4px' }}>
                  Trigger: <strong>{tpl.trigger}</strong> • Steps: <strong>{tpl.stepsCount} Stages</strong> • Compute: {tpl.cost}
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <button
                  onClick={() => setExecutedPlaybook(tpl.code)}
                  style={{
                    padding: '8px 14px',
                    background: '#10B981',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#090D14',
                    fontSize: '0.78rem',
                    fontWeight: 800,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                  }}
                >
                  <Play size={14} />
                  <span>Launch Playbook</span>
                </button>
              </div>
            </div>
          ))}
        </div>

        {executedPlaybook && (
          <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: '16px', borderRadius: '8px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CheckCircle2 size={16} color="#10B981" />
              <span style={{ fontSize: '0.85rem', fontWeight: 800, color: '#FFFFFF' }}>
                Playbook Execution PBX-2026-Q1-001 Completed Successfully (Cost: $0.14 • 240ms)
              </span>
            </div>
            <div style={{ fontSize: '0.78rem', color: '#94A3B8' }}>
              1. Ingest Alert (28ms) → 2. Root Cause Diagnostics (64ms) → 3. Twin Scenario Simulation (82ms) → 4. Draft Initiative (36ms) → 5. Governance Review Dispatched (30ms).
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
