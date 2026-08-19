import React, { useState } from 'react';
import { FileText, Download, CheckCircle2, Sparkles, Scale, TrendingUp, ShieldCheck, Play, ArrowRight, Layers } from 'lucide-react';
import { Card, Badge, Button, MetricTile } from '../../design-system';

export const BoardroomCenterView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'BOARD_PACKS' | 'EXECUTIVE_NARRATIVE' | 'QBR'>('BOARD_PACKS');
  const [downloadSuccess, setDownloadSuccess] = useState(false);

  const slides = [
    { num: 1, title: 'Executive Summary & Enterprise Intelligence Score (93.1)', content: 'ARR: $12.4M (+12.4% YoY) • Operating Grade: A+ (94.8) • Trust Score: 93.2' },
    { num: 2, title: 'Capital Allocation Optimization ($1M Deployment)', content: 'Recommended: 62% SaaS ($620K, 7.2x ROI) • 28% Retail ($280K, 4.8x) • Expected ARR: +$601,800' },
    { num: 3, title: 'Enterprise Drag Diagnosis: APAC Regional Logistics', content: 'Latency drag (-$140K ARR) modeled by Digital Twin. Automated route rebalancing active.' },
    { num: 4, title: 'Closed-Loop Governance Outcomes & Value Realization', content: '42 decisions closed with 91.8% accuracy producing +$312K in audited ARR gains.' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#F59E0B', fontWeight: 800 }}>
            C-Suite & Board of Directors Executive Layer
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Executive Boardroom Intelligence & Meeting Packs
          </h1>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <Button
            variant="primary"
            size="sm"
            icon={<Download size={14} />}
            onClick={() => setDownloadSuccess(true)}
          >
            Export Complete Board Pack (PDF + Markdown)
          </Button>
        </div>
      </div>

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <MetricTile label="ENTERPRISE INTELLIGENCE SCORE" value="93.1" sublabel="Grade A+ Certified Platform" valueColor="#10B981" />
        <MetricTile label="Q1 REALIZED VALUE (ARR)" value="+$312,000" sublabel="91.8% Decision Accuracy" valueColor="#38BDF8" />
        <MetricTile label="CAPITAL DEPLOYMENT ROI" value="6.02x" sublabel="$1M Investment Model" valueColor="#A855F7" />
        <MetricTile label="BOARD SIGNOFF STATUS" value="APPROVED" sublabel="Signed Off by Alexander Vance (CEO)" valueColor="#F59E0B" />
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '8px', padding: '3px', width: 'fit-content' }}>
        <button
          onClick={() => setActiveTab('BOARD_PACKS')}
          style={{
            padding: '6px 14px',
            borderRadius: '6px',
            border: 'none',
            background: activeTab === 'BOARD_PACKS' ? '#38BDF8' : 'transparent',
            color: activeTab === 'BOARD_PACKS' ? '#090D14' : '#94A3B8',
            fontWeight: 700,
            fontSize: '0.78rem',
            cursor: 'pointer',
          }}
        >
          Board Slides (4)
        </button>
        <button
          onClick={() => setActiveTab('EXECUTIVE_NARRATIVE')}
          style={{
            padding: '6px 14px',
            borderRadius: '6px',
            border: 'none',
            background: activeTab === 'EXECUTIVE_NARRATIVE' ? '#A855F7' : 'transparent',
            color: activeTab === 'EXECUTIVE_NARRATIVE' ? '#FFFFFF' : '#94A3B8',
            fontWeight: 700,
            fontSize: '0.78rem',
            cursor: 'pointer',
          }}
        >
          Executive Narrative
        </button>
        <button
          onClick={() => setActiveTab('QBR')}
          style={{
            padding: '6px 14px',
            borderRadius: '6px',
            border: 'none',
            background: activeTab === 'QBR' ? '#10B981' : 'transparent',
            color: activeTab === 'QBR' ? '#090D14' : '#94A3B8',
            fontWeight: 700,
            fontSize: '0.78rem',
            cursor: 'pointer',
          }}
        >
          QBR Briefing
        </button>
      </div>

      {activeTab === 'BOARD_PACKS' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
          {slides.map((s) => (
            <Card key={s.num} style={{ padding: '22px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800 }}>SLIDE {s.num} OF 4</span>
                <Badge variant="sky" size="sm">
                  BOARD DECK
                </Badge>
              </div>
              <h3 style={{ fontSize: '0.98rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>{s.title}</h3>
              <div style={{ fontSize: '0.8rem', color: '#94A3B8', lineHeight: 1.5, background: 'rgba(15, 23, 42, 0.6)', padding: '12px', borderRadius: '8px' }}>
                {s.content}
              </div>
            </Card>
          ))}
        </div>
      )}

      {activeTab === 'EXECUTIVE_NARRATIVE' && (
        <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '1.05rem', fontWeight: 800, color: '#FFFFFF' }}>
              Southeastern Courier Latency Mitigation Protected $312K in At-Risk ARR
            </span>
            <Badge variant="purple" size="sm">
              CONFIDENCE: 96.4%
            </Badge>
          </div>
          <p style={{ fontSize: '0.84rem', color: '#94A3B8', lineHeight: 1.6, margin: 0 }}>
            Telemetry signals identified a 3.4-day delivery latency spike in Southeastern nodes, which was modeled by the Digital Twin as a 6.8% retention drag. Autonomous Operations Agent proposed DEC-042 enforcing 15% billing penalties and reallocating 40% of parcel volume to Northern carrier lines. Human VP sign-off executed the initiative within 2 hours, resulting in a full latency recovery to 2.8 days and protecting +$312K in enterprise ARR.
          </p>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '6px' }}>
            <span style={{ fontSize: '0.7rem', color: '#38BDF8', fontFamily: 'monospace' }}>URN: KPI:RETENTION:SNP-042</span>
            <span style={{ fontSize: '0.7rem', color: '#38BDF8', fontFamily: 'monospace' }}>URN: ROOTCAUSE:RC-004</span>
            <span style={{ fontSize: '0.7rem', color: '#38BDF8', fontFamily: 'monospace' }}>URN: DEC:DEC-042</span>
            <span style={{ fontSize: '0.7rem', color: '#38BDF8', fontFamily: 'monospace' }}>URN: INIT:INIT-051</span>
          </div>
        </Card>
      )}

      {activeTab === 'QBR' && (
        <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Quarterly Business Review (QBR) Strategic Summary</span>
          <div style={{ fontSize: '0.82rem', color: '#94A3B8', lineHeight: 1.6 }}>
            DecisionOS closed Q1 2026 with an Enterprise Intelligence Score of 93.1/100, driven by +$312K in realized ARR gains from Southeastern courier SLA enforcement. Capital allocation modeling demonstrated a 6.02x blended ROI, with Enterprise SaaS performing at 7.2x multiple. Primary enterprise drag remains APAC Regional Logistics (-$140K).
          </div>
        </Card>
      )}

      {downloadSuccess && (
        <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.25)', padding: '16px', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <CheckCircle2 size={18} color="#10B981" />
            <span style={{ fontSize: '0.84rem', color: '#F1F5F9' }}>
              Board Meeting Package generated successfully: <strong>BMP-2026-Q1-ANNUAL.pdf</strong> (Includes slides, narrative citations & CEO sign-off).
            </span>
          </div>
          <Button variant="ghost" size="sm" onClick={() => setDownloadSuccess(false)}>
            Dismiss
          </Button>
        </div>
      )}
    </div>
  );
};
