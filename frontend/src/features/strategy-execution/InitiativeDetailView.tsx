import React, { useState } from 'react';
import {
  Target,
  Clock,
  CheckCircle2,
  AlertTriangle,
  History,
  ShieldAlert,
  GitMerge,
  FileCheck,
  TrendingUp,
  ArrowLeft,
  Sparkles,
} from 'lucide-react';
import { Link, useParams } from 'react-router-dom';

export const InitiativeDetailView: React.FC = () => {
  const { id } = useParams();
  const [activeTab, setActiveTab] = useState<'OVERVIEW' | 'VERSIONS' | 'RISKS' | 'ATTRIBUTION'>('OVERVIEW');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Back Link & Header */}
      <div>
        <Link
          to="/strategy-execution"
          style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: '#64748B', fontSize: '0.8rem', fontWeight: 700, textDecoration: 'none', marginBottom: '8px' }}
        >
          <ArrowLeft size={14} />
          <span>Back to Strategy Execution Center</span>
        </Link>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginTop: '4px' }}>
          <span style={{ fontSize: '0.82rem', fontWeight: 800, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.12)', padding: '3px 10px', borderRadius: '6px' }}>
            INIT-2026-001 • V3
          </span>
          <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#10B981', background: 'rgba(16, 185, 129, 0.15)', padding: '3px 10px', borderRadius: '12px' }}>
            IN PROGRESS (78%)
          </span>
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '8px 0 0 0' }}>
          Secondary Hub Courier Rebalancing & Automated SLA Penalties
        </h1>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid #1E293B', paddingBottom: '8px' }}>
        {[
          { key: 'OVERVIEW', label: 'Milestones & Execution' },
          { key: 'VERSIONS', label: 'Revision History (V1 → V3)' },
          { key: 'RISKS', label: 'Risk Register & Mitigations' },
          { key: 'ATTRIBUTION', label: 'Outcome Attribution & Evidence' },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            style={{
              padding: '8px 16px',
              borderRadius: '8px',
              border: 'none',
              background: activeTab === tab.key ? '#0284C7' : 'rgba(15, 23, 42, 0.8)',
              color: '#FFFFFF',
              fontSize: '0.82rem',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab 1: Overview & Milestones */}
      {activeTab === 'OVERVIEW' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Realized Metrics Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px' }}>
            <div style={{ background: '#090D14', border: '1px solid #1E293B', padding: '16px', borderRadius: '10px' }}>
              <div style={{ fontSize: '0.68rem', color: '#64748B', fontWeight: 800 }}>EXPECTED VS ACTUAL ARR</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#10B981', marginTop: '2px' }}>+$118,000</div>
              <div style={{ fontSize: '0.72rem', color: '#94A3B8' }}>Expected: +$124,000 (95.2% Realized)</div>
            </div>
            <div style={{ background: '#090D14', border: '1px solid #1E293B', padding: '16px', borderRadius: '10px' }}>
              <div style={{ fontSize: '0.68rem', color: '#64748B', fontWeight: 800 }}>HEALTH SCORE LIFT</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#38BDF8', marginTop: '2px' }}>+10.5 pts</div>
              <div style={{ fontSize: '0.72rem', color: '#94A3B8' }}>Expected: +11.0 pts</div>
            </div>
            <div style={{ background: '#090D14', border: '1px solid #1E293B', padding: '16px', borderRadius: '10px' }}>
              <div style={{ fontSize: '0.68rem', color: '#64748B', fontWeight: 800 }}>RISK REDUCTION</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#F59E0B', marginTop: '2px' }}>-9.8 pts</div>
              <div style={{ fontSize: '0.72rem', color: '#94A3B8' }}>Expected: -10.2 pts</div>
            </div>
          </div>

          {/* Milestones Checklist */}
          <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>Initiative Execution Milestones</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {[
                { title: 'Deploy Automated SLA Penalty Billing Rules', status: 'COMPLETED', date: 'Completed 28 days ago', pct: '100%' },
                { title: 'Southeastern Hub Transit Load Rebalancing', status: 'COMPLETED', date: 'Completed 12 days ago', pct: '100%' },
                { title: 'Finalize 90-Day Retention Lift Audit', status: 'IN_PROGRESS', date: 'Target: In 20 days', pct: '60%' },
              ].map((m, idx) => (
                <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 16px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '8px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <CheckCircle2 size={16} color={m.status === 'COMPLETED' ? '#10B981' : '#38BDF8'} />
                    <div>
                      <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#FFFFFF' }}>{m.title}</div>
                      <div style={{ fontSize: '0.72rem', color: '#64748B' }}>{m.date}</div>
                    </div>
                  </div>
                  <span style={{ fontSize: '0.75rem', fontWeight: 800, color: m.status === 'COMPLETED' ? '#10B981' : '#38BDF8' }}>
                    {m.pct}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Revision History */}
      {activeTab === 'VERSIONS' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {[
            { version: 'Version 3 (Active)', date: '10 days ago', arr: '+$118,000 ARR', summary: 'Calibrated ARR recovery expectation to +$118K based on actual Southeastern courier data.' },
            { version: 'Version 2', date: '30 days ago', arr: '+$95,000 ARR', summary: 'Added $25.8K win-back tokens into scope.' },
            { version: 'Version 1', date: '60 days ago', arr: '+$124,000 ARR', summary: 'Initial scope approved by Board of Directors and Chief Operating Officer.' },
          ].map((v, idx) => (
            <div key={idx} style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '12px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 800, color: '#38BDF8' }}>{v.version}</span>
                <span style={{ fontSize: '0.75rem', color: '#64748B' }}>{v.date}</span>
              </div>
              <div style={{ fontSize: '1rem', fontWeight: 800, color: '#10B981' }}>{v.arr}</div>
              <p style={{ fontSize: '0.82rem', color: '#94A3B8', margin: 0 }}>{v.summary}</p>
            </div>
          ))}
        </div>
      )}

      {/* Tab 3: Risk Register */}
      {activeTab === 'RISKS' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {[
            { title: 'Courier Churn During SLA Transition', sev: 'HIGH', prob: '25%', impact: '40%', plan: 'Dynamically route 30% volume to secondary regional carrier partners during transition.', status: 'MITIGATING' },
            { title: 'Support Ticket Spikes', sev: 'MEDIUM', prob: '15%', impact: '20%', plan: 'Deploy automated tracking webhook push alerts directly to customer mobile apps.', status: 'MITIGATED' },
          ].map((r, idx) => (
            <div key={idx} style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '12px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.9rem', fontWeight: 800, color: '#FFFFFF' }}>{r.title}</span>
                <span style={{ fontSize: '0.7rem', fontWeight: 800, color: r.sev === 'HIGH' ? '#EF4444' : '#F59E0B', background: 'rgba(239, 68, 68, 0.15)', padding: '2px 8px', borderRadius: '4px' }}>
                  {r.sev} SEVERITY
                </span>
              </div>
              <div style={{ fontSize: '0.78rem', color: '#94A3B8' }}>
                Probability: {r.prob} • Potential Impact: {r.impact}
              </div>
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '10px 14px', borderRadius: '6px', fontSize: '0.78rem', color: '#F1F5F9' }}>
                <strong>Mitigation Plan:</strong> {r.plan}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab 4: Outcome Attribution & Evidence */}
      {activeTab === 'ATTRIBUTION' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
              Deterministic Outcome Attribution Chain
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {[
                { stage: '1. INITIATIVE', label: 'Secondary Hub Courier Rebalancing & SLA Enforcement' },
                { stage: '2. RECOMMENDATION', label: 'Recommendation #1: Enforce 15% courier billing penalties (94% certainty)' },
                { stage: '3. ROOT CAUSE', label: 'Root Cause #4: Southeastern Secondary Hub Transit Delays (100% Resolved)' },
                { stage: '4. KPI MOVEMENT', label: 'Delivery Latency 5.4d → 3.4d | Customer Retention 79.5% → 84.2% (+4.7% Lift)' },
                { stage: '5. REALIZED ARR', label: '+$118,000 Verified Realized ARR Lift (95.2% Realization Score)' },
              ].map((step, idx) => (
                <div key={idx} style={{ padding: '12px 16px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '8px' }}>
                  <div style={{ fontSize: '0.68rem', fontWeight: 800, color: '#38BDF8' }}>{step.stage}</div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#FFFFFF', marginTop: '2px' }}>{step.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
