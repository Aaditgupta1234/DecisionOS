import React, { useState } from 'react';
import { Bot, Sparkles, ShieldCheck, CheckCircle2, Play, GitMerge, ArrowRight, Zap, Scale, BarChart3, TrendingUp, AlertTriangle } from 'lucide-react';
import { Card, Badge, Button, MetricTile } from '../../design-system';

export interface AgentPerformanceProfile {
  agentId: string;
  agentName: string;
  recommendationsGenerated: number;
  recommendationsApproved: number;
  realizedArrProduced: string;
  accuracyScore: number;
  overrideRate: string;
}

export const AutonomousAgentsHubView: React.FC = () => {
  const [activeDispatch, setActiveDispatch] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'AGENTS' | 'PERFORMANCE_PROFILES'>('AGENTS');

  const performanceProfiles: AgentPerformanceProfile[] = [
    {
      agentId: 'agent-growth',
      agentName: 'Revenue Growth Agent',
      recommendationsGenerated: 48,
      recommendationsApproved: 41,
      realizedArrProduced: '+$2,400,000 ARR',
      accuracyScore: 91.8,
      overrideRate: '14.6%',
    },
    {
      agentId: 'agent-retention',
      agentName: 'Customer Retention Agent',
      recommendationsGenerated: 36,
      recommendationsApproved: 34,
      realizedArrProduced: '+$1,820,000 ARR',
      accuracyScore: 94.2,
      overrideRate: '5.5%',
    },
    {
      agentId: 'agent-ops',
      agentName: 'Operations & Logistics Agent',
      recommendationsGenerated: 42,
      recommendationsApproved: 39,
      realizedArrProduced: '+$940,000 ARR',
      accuracyScore: 92.5,
      overrideRate: '7.1%',
    },
    {
      agentId: 'agent-strategy',
      agentName: 'Executive Strategy Agent',
      recommendationsGenerated: 28,
      recommendationsApproved: 26,
      realizedArrProduced: '+$3,100,000 ARR',
      accuracyScore: 95.4,
      overrideRate: '7.1%',
    },
  ];

  const agents = [
    {
      id: 'agent-strategy',
      name: 'Executive Strategy Agent',
      domain: 'Strategic Capital & Board Alignment',
      confidence: '95.4%',
      status: 'ACTIVE_ONLINE',
      currentTask: 'Optimizing $1M capital deployment across SaaS vs Retail curves',
      actionsTaken: 28,
      approvalTier: 'EXECUTIVE_APPROVAL',
    },
    {
      id: 'agent-ops',
      name: 'Operations & Logistics Agent',
      domain: 'Route Optimization & Latency SLAs',
      confidence: '92.1%',
      status: 'ACTIVE_ONLINE',
      currentTask: 'Enforcing 15% courier billing penalties on Southeastern transit delays',
      actionsTaken: 42,
      approvalTier: 'MANAGER_APPROVAL',
    },
    {
      id: 'agent-growth',
      name: 'Revenue Growth Agent',
      domain: 'Expansion & Dynamic Pricing Hedges',
      confidence: '96.2%',
      status: 'ACTIVE_ONLINE',
      currentTask: 'Modeling Q2 fuel surcharge index to protect gross margins',
      actionsTaken: 19,
      approvalTier: 'EXECUTIVE_APPROVAL',
    },
    {
      id: 'agent-retention',
      name: 'Customer Retention Agent',
      domain: 'Account Churn & SLA Risk Mitigation',
      confidence: '94.8%',
      status: 'ACTIVE_ONLINE',
      currentTask: 'Rerouting parcel volume to northern nodes to close -6.8% gap',
      actionsTaken: 36,
      approvalTier: 'AUTO_APPROVED',
    },
    {
      id: 'agent-compliance',
      name: 'Risk & Compliance Agent',
      domain: 'Policy Rules & Governance Gating',
      confidence: '99.1%',
      status: 'ACTIVE_ONLINE',
      currentTask: 'Validating DEC-2026-042 against financial & SOC2 envelopes',
      actionsTaken: 54,
      approvalTier: 'BOARD_APPROVAL',
    },
    {
      id: 'agent-portfolio',
      name: 'Portfolio Optimization Agent',
      domain: 'Multi-Business Unit Health & Drag',
      confidence: '93.8%',
      status: 'ACTIVE_ONLINE',
      currentTask: 'Isolating APAC Logistics -$140K drag and synthesizing recovery scenario',
      actionsTaken: 22,
      approvalTier: 'EXECUTIVE_APPROVAL',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#A855F7', fontWeight: 800 }}>
            Deterministic Autonomous Intelligence Layer
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Autonomous Enterprise Agents Hub & Orchestrator
          </h1>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ display: 'flex', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '8px', padding: '3px' }}>
            <button
              onClick={() => setActiveTab('AGENTS')}
              style={{
                padding: '6px 12px',
                borderRadius: '6px',
                border: 'none',
                background: activeTab === 'AGENTS' ? '#38BDF8' : 'transparent',
                color: activeTab === 'AGENTS' ? '#090D14' : '#94A3B8',
                fontWeight: 700,
                fontSize: '0.76rem',
                cursor: 'pointer',
              }}
            >
              Active Agents (6)
            </button>
            <button
              onClick={() => setActiveTab('PERFORMANCE_PROFILES')}
              style={{
                padding: '6px 12px',
                borderRadius: '6px',
                border: 'none',
                background: activeTab === 'PERFORMANCE_PROFILES' ? '#A855F7' : 'transparent',
                color: activeTab === 'PERFORMANCE_PROFILES' ? '#FFFFFF' : '#94A3B8',
                fontWeight: 700,
                fontSize: '0.76rem',
                cursor: 'pointer',
              }}
            >
              Agent Performance Profiles
            </button>
          </div>

          <Badge variant="emerald" size="md">
            TRUST SCORE: 93.2 / 100
          </Badge>
        </div>
      </div>

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <MetricTile label="TOTAL AGENT DISPATCHES" value="201 Runs" sublabel="Zero Ungrounded Hallucinations" valueColor="#A855F7" />
        <MetricTile label="DECISION ACCURACY RATE" value="91.8%" sublabel="Realized ARR vs Agent Forecast" valueColor="#10B981" />
        <MetricTile label="CUMULATIVE REALIZED VALUE" value="+$8.26M ARR" sublabel="Attributed to Approved Proposals" valueColor="#38BDF8" />
        <MetricTile label="AVG INFERENCE LATENCY" value="240ms" sublabel="Cost: $0.002 per Agent Task" valueColor="#F59E0B" />
      </div>

      {activeTab === 'PERFORMANCE_PROFILES' ? (
        /* Agent Performance Profiles Ledger */
        <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>
              Agent Performance & Historical Accuracy Ledger
            </span>
            <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Closed-Loop AI Governance</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {performanceProfiles.map((p) => (
              <div
                key={p.agentId}
                style={{
                  background: 'rgba(15, 23, 42, 0.6)',
                  border: '1px solid #1E293B',
                  borderRadius: '10px',
                  padding: '18px 20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: '14px',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Bot size={16} color="#A855F7" />
                    <span style={{ fontSize: '0.98rem', fontWeight: 800, color: '#FFFFFF' }}>{p.agentName}</span>
                    <Badge variant="emerald" size="sm">
                      {p.accuracyScore}% Accuracy
                    </Badge>
                  </div>
                  <div style={{ fontSize: '0.78rem', color: '#94A3B8', marginTop: '4px' }}>
                    Proposals: <strong style={{ color: '#FFFFFF' }}>{p.recommendationsGenerated}</strong> • Approved: <strong style={{ color: '#10B981' }}>{p.recommendationsApproved} ({Math.round((p.recommendationsApproved / p.recommendationsGenerated) * 100)}%)</strong> • Override Rate: {p.overrideRate}
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '0.9rem', fontWeight: 900, color: '#38BDF8', padding: '6px 14px', background: 'rgba(56, 189, 248, 0.1)', border: '1px solid rgba(56, 189, 248, 0.3)', borderRadius: '8px' }}>
                    {p.realizedArrProduced}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      ) : (
        <>
          {/* Multi-Agent Collaboration Pipeline Banner */}
          <Card style={{ padding: '20px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B' }}>
            <div style={{ fontSize: '0.74rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', marginBottom: '8px' }}>
              ACTIVE MULTI-AGENT COLLABORATION PIPELINE
            </div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
              <div style={{ fontSize: '0.84rem', color: '#F1F5F9', fontWeight: 600 }}>
                <span style={{ color: '#EF4444' }}>Retention Agent</span> (Diagnose Drag) → <span style={{ color: '#38BDF8' }}>Strategy Agent</span> (Formulate Capital Rec) → <span style={{ color: '#A855F7' }}>Simulation Agent</span> (Digital Twin Run) → <span style={{ color: '#10B981' }}>Compliance Agent</span> (Gate Decision)
              </div>
              <Badge variant="emerald" size="sm">
                PIPELINE STATUS: SYNCHRONIZED
              </Badge>
            </div>
          </Card>

          {/* 6 Specialized Agents Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
            {agents.map((ag) => (
              <Card key={ag.id} style={{ display: 'flex', flexDirection: 'column', gap: '12px', padding: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{ padding: '8px', background: 'rgba(168, 85, 247, 0.15)', borderRadius: '8px' }}>
                      <Bot size={18} color="#A855F7" />
                    </div>
                    <div>
                      <h3 style={{ fontSize: '0.95rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>{ag.name}</h3>
                      <span style={{ fontSize: '0.72rem', color: '#64748B' }}>{ag.domain}</span>
                    </div>
                  </div>
                  <Badge variant="purple" size="sm">
                    {ag.confidence}
                  </Badge>
                </div>

                <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '12px', borderRadius: '8px', fontSize: '0.78rem', color: '#94A3B8' }}>
                  <strong style={{ color: '#FFFFFF' }}>Active Task:</strong> {ag.currentTask}
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.74rem', color: '#64748B' }}>
                  <span>Actions: <strong style={{ color: '#F1F5F9' }}>{ag.actionsTaken}</strong></span>
                  <span>Gate: <strong style={{ color: '#38BDF8' }}>{ag.approvalTier}</strong></span>
                </div>

                <Button
                  variant="secondary"
                  size="sm"
                  icon={<Play size={12} />}
                  onClick={() => setActiveDispatch(ag.name)}
                >
                  Dispatch Agent Pipeline
                </Button>
              </Card>
            ))}
          </div>
        </>
      )}

      {activeDispatch && (
        <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: '16px', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <CheckCircle2 size={18} color="#10B981" />
            <span style={{ fontSize: '0.84rem', color: '#F1F5F9' }}>
              Task dispatched to <strong>{activeDispatch}</strong>. Formulating evidence-grounded recommendation with Executive Trust Score 93.2/100.
            </span>
          </div>
          <Button variant="ghost" size="sm" onClick={() => setActiveDispatch(null)}>
            Dismiss
          </Button>
        </div>
      )}
    </div>
  );
};
