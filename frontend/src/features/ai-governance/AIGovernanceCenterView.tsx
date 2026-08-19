import React from 'react';
import { Bot, Sparkles, ShieldCheck, CheckCircle2, DollarSign, Clock, Layers, ArrowRight } from 'lucide-react';
import { Card, Badge, Button, MetricTile } from '../../design-system';

export const AIGovernanceCenterView: React.FC = () => {
  const audits = [
    {
      id: 'ai-01',
      user: 'Alexander Vance (CEO)',
      query: 'Synthesize Q1 Board Narrative on Southeastern Courier Delays',
      urns: ['KPI:RETENTION:SNP-042', 'ROOTCAUSE:RC-004', 'DEC:DEC-042'],
      model: 'gemini-1.5-pro',
      latency: '218ms',
      cost: '$0.002',
      status: 'VERIFIED_GROUNDED',
      time: '14m ago',
    },
    {
      id: 'ai-02',
      user: 'Elena Rostova (CFO)',
      query: 'Evaluate $1M capital allocation ROI for Enterprise SaaS vs Retail',
      urns: ['CAPITAL:SAAS:7.2X', 'CAPITAL:RETAIL:4.8X'],
      model: 'gemini-1.5-pro',
      latency: '245ms',
      cost: '$0.003',
      status: 'VERIFIED_GROUNDED',
      time: '42m ago',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#A855F7', fontWeight: 800 }}>
          AI Transparency, Safety & Token Cost Governance
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          AI Usage & Prompt Governance Center
        </h1>
      </div>

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <MetricTile label="TOTAL AUDITED AI PROMPTS" value="4,820" sublabel="100% Grounded in Evidence URNs" valueColor="#A855F7" />
        <MetricTile label="HALLUCINATION RATE" value="0.0%" sublabel="Zero Ungrounded Generative Output" valueColor="#10B981" />
        <MetricTile label="MONTHLY INFERENCE SPEND" value="$28.42" sublabel="Avg: $0.002 per Reasoning Trace" valueColor="#38BDF8" />
        <MetricTile label="EXECUTIVE TRUST SCORE" value="93.2 / 100" sublabel="C-Suite Verified Confidence" valueColor="#F59E0B" />
      </div>

      {/* Prompt Audit Table */}
      <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>AI Prompt & Evidence Citation Ledger</span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Deterministic Traceability</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {audits.map((a) => (
            <div
              key={a.id}
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
                  <span style={{ fontSize: '0.96rem', fontWeight: 800, color: '#FFFFFF' }}>{a.query}</span>
                  <Badge variant="purple" size="sm">
                    {a.status}
                  </Badge>
                </div>
                <div style={{ fontSize: '0.76rem', color: '#94A3B8', marginTop: '4px' }}>
                  User: <strong style={{ color: '#F1F5F9' }}>{a.user}</strong> • Model: {a.model} • Latency: {a.latency} • Cost: <strong style={{ color: '#10B981' }}>{a.cost}</strong>
                </div>
                <div style={{ display: 'flex', gap: '6px', marginTop: '6px', flexWrap: 'wrap' }}>
                  {a.urns.map((u) => (
                    <span key={u} style={{ fontSize: '0.68rem', color: '#38BDF8', fontFamily: 'monospace', background: 'rgba(56, 189, 248, 0.1)', padding: '2px 6px', borderRadius: '4px' }}>
                      {u}
                    </span>
                  ))}
                </div>
              </div>

              <span style={{ fontSize: '0.74rem', color: '#64748B' }}>{a.time}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
