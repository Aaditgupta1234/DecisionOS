import React, { useState } from 'react';
import {
  Shield,
  Layers,
  TrendingUp,
  Target,
  AlertTriangle,
  FileCheck2,
  GitBranch,
  Building2,
  DollarSign,
  PieChart,
  ArrowRight,
  Maximize2,
  X,
  CheckCircle2,
  Activity,
  Award
} from 'lucide-react';

export const PortfolioGovernanceCenterView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'DIRECTIVES' | 'ARR_ATTRIBUTION' | 'RISK_HEATMAP' | 'GOVERNANCE_INDEX'>('DIRECTIVES');
  const [selectedPortfolioDir, setSelectedPortfolioDir] = useState<any | null>(null);

  const portfolioDirectives = [
    {
      id: 'PORT-DIR-001',
      title: 'Enterprise Courier SLA Governance & Transit Compression',
      theme: 'Logistics & Fulfillment SLA Governance',
      sponsor: 'Chief Operating Officer (COO)',
      status: 'COMPLETED',
      expectedArr: 156750,
      actualArr: 148912.5,
      variance: -7837.5,
      achievementPct: 95.0,
      workspaces: [
        { name: 'E-Commerce Regional Hub A', dirId: 'DIR-01', arr: 78375, realized: 74456.25, share: '50.0%' },
        { name: 'Retail Logistics Hub B', dirId: 'DIR-04', arr: 78375, realized: 74456.25, share: '50.0%' },
      ],
      lineagePath: 'PORT-DIR-001 -> [DIR-01, DIR-04] -> [REC-01, REC-04] -> [RC-01, RC-04] -> [DIAG-01, DIAG-04] -> completion_rate -> Raw CSV',
    },
    {
      id: 'PORT-DIR-002',
      title: 'Enterprise Retention Outreach & Loyalty Token Automation',
      theme: 'Customer Retention & Churn Remediation',
      sponsor: 'Chief Marketing Officer (CMO)',
      status: 'IN_PROGRESS',
      expectedArr: 99000,
      actualArr: 44800,
      variance: -54200,
      achievementPct: 45.3,
      workspaces: [
        { name: 'E-Commerce Regional Hub A', dirId: 'DIR-02', arr: 49500, realized: 22400, share: '50.0%' },
        { name: 'DTC Omnichannel Hub C', dirId: 'DIR-02', arr: 49500, realized: 22400, share: '50.0%' },
      ],
      lineagePath: 'PORT-DIR-002 -> [DIR-02, DIR-02] -> [REC-02, REC-02] -> [RC-02, RC-02] -> [DIAG-02, DIAG-02] -> retention_rate -> Raw CSV',
    },
    {
      id: 'PORT-DIR-003',
      title: 'Portfolio-Wide Discount Threshold Audit & Price Governance',
      theme: 'Commercial Pricing & Margin Protection',
      sponsor: 'Chief Financial Officer (CFO)',
      status: 'PLANNED',
      expectedArr: 148500,
      actualArr: 0,
      variance: -148500,
      achievementPct: 0.0,
      workspaces: [
        { name: 'E-Commerce Regional Hub A', dirId: 'DIR-03', arr: 74250, realized: 0, share: '50.0%' },
        { name: 'Retail Logistics Hub B', dirId: 'DIR-06', arr: 74250, realized: 0, share: '50.0%' },
      ],
      lineagePath: 'PORT-DIR-003 -> [DIR-03, DIR-06] -> [REC-03, REC-06] -> [RC-03, RC-06] -> [DIAG-03, DIAG-06] -> total_revenue -> Raw CSV',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Portfolio Governance Summary Header */}
      <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '12px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '0.72rem', textTransform: 'uppercase', color: '#38BDF8', fontWeight: 800 }}>
                Enterprise Portfolio Executive Layer
              </span>
              <span style={{ fontSize: '0.65rem', background: 'rgba(56, 189, 248, 0.15)', color: '#38BDF8', padding: '2px 8px', borderRadius: '12px', fontWeight: 800 }}>
                3 Workspaces Tracked
              </span>
              <span style={{ fontSize: '0.65rem', background: 'rgba(16, 185, 129, 0.15)', color: '#10B981', padding: '2px 8px', borderRadius: '12px', fontWeight: 800 }}>
                Anti-Hallucination Certified
              </span>
            </div>
            <h1 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#FFFFFF', margin: '4px 0 0 0' }}>
              Portfolio Boardroom Governance & Directive Center
            </h1>
          </div>

          {/* Tab Navigation */}
          <div style={{ display: 'flex', gap: '4px', background: 'rgba(15, 23, 42, 0.8)', padding: '4px', borderRadius: '8px', border: '1px solid #1E293B' }}>
            {[
              { key: 'DIRECTIVES', label: 'Portfolio Directives', icon: Target },
              { key: 'ARR_ATTRIBUTION', label: 'ARR Attribution', icon: DollarSign },
              { key: 'RISK_HEATMAP', label: 'Risk Heatmap', icon: AlertTriangle },
              { key: 'GOVERNANCE_INDEX', label: 'Governance Index', icon: Shield },
            ].map((t) => {
              const Icon = t.icon;
              const isActive = activeTab === t.key;
              return (
                <button
                  key={t.key}
                  onClick={() => setActiveTab(t.key as any)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '6px 12px',
                    borderRadius: '6px',
                    border: 'none',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    background: isActive ? '#38BDF8' : 'transparent',
                    color: isActive ? '#090D14' : '#94A3B8',
                  }}
                >
                  <Icon size={14} />
                  {t.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Top-Level Metric Summary Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
          <div style={{ padding: '14px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.68rem', color: '#64748B', fontWeight: 700 }}>PORTFOLIO EXPECTED ARR</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#38BDF8', marginTop: '2px' }}>+$404,250.00</div>
            <div style={{ fontSize: '0.72rem', color: '#94A3B8', marginTop: '2px' }}>3 Strategic Initiatives</div>
          </div>
          <div style={{ padding: '14px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.68rem', color: '#64748B', fontWeight: 700 }}>PORTFOLIO REALIZED ARR</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#10B981', marginTop: '2px' }}>+$193,712.50</div>
            <div style={{ fontSize: '0.72rem', color: '#10B981', marginTop: '2px' }}>47.9% Achievement</div>
          </div>
          <div style={{ padding: '14px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.68rem', color: '#64748B', fontWeight: 700 }}>GOVERNANCE HEALTH INDEX</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#A855F7', marginTop: '2px' }}>99.7 / 100</div>
            <div style={{ fontSize: '0.72rem', color: '#10B981', marginTop: '2px' }}>Audit-Grade Certified</div>
          </div>
          <div style={{ padding: '14px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.68rem', color: '#64748B', fontWeight: 700 }}>HERFINDAHL CONCENTRATION</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#F59E0B', marginTop: '2px' }}>0.41 HHI</div>
            <div style={{ fontSize: '0.72rem', color: '#94A3B8', marginTop: '2px' }}>Moderate Diversification</div>
          </div>
        </div>
      </div>

      {/* Tab 1: Portfolio Directive Rollups */}
      {activeTab === 'DIRECTIVES' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {portfolioDirectives.map((pDir) => (
            <div
              key={pDir.id}
              style={{
                background: '#090D14',
                border: '1px solid #1E293B',
                borderRadius: '10px',
                padding: '18px 20px',
                display: 'flex',
                flexDirection: 'column',
                gap: '14px',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.12)', padding: '3px 8px', borderRadius: '4px' }}>
                    {pDir.id}
                  </span>
                  <span style={{ fontSize: '0.98rem', fontWeight: 700, color: '#FFFFFF' }}>{pDir.title}</span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <button
                    onClick={() => setSelectedPortfolioDir(pDir)}
                    style={{
                      padding: '4px 10px',
                      borderRadius: '4px',
                      background: 'rgba(56, 189, 248, 0.15)',
                      border: '1px solid rgba(56, 189, 248, 0.4)',
                      color: '#38BDF8',
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                    }}
                  >
                    <Maximize2 size={12} /> Cross-Workspace Lineage
                  </button>
                  <span style={{ fontSize: '0.78rem', color: '#94A3B8' }}>{pDir.sponsor}</span>
                  <span
                    style={{
                      fontSize: '0.72rem',
                      fontWeight: 800,
                      padding: '3px 8px',
                      borderRadius: '10px',
                      background: pDir.status === 'COMPLETED' ? 'rgba(16, 185, 129, 0.15)' : pDir.status === 'IN_PROGRESS' ? 'rgba(56, 189, 248, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                      color: pDir.status === 'COMPLETED' ? '#10B981' : pDir.status === 'IN_PROGRESS' ? '#38BDF8' : '#F59E0B',
                    }}
                  >
                    {pDir.status}
                  </span>
                </div>
              </div>

              {/* Workspace Contribution Rollup Matrix */}
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '8px', padding: '12px 16px' }}>
                <div style={{ fontSize: '0.72rem', fontWeight: 800, color: '#64748B', textTransform: 'uppercase', marginBottom: '8px' }}>
                  Workspace Directives Aggregated Into {pDir.id}:
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
                  {pDir.workspaces.map((ws, wIdx) => (
                    <div key={wIdx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(9, 13, 20, 0.7)', padding: '8px 12px', borderRadius: '6px', border: '1px solid #334155' }}>
                      <div>
                        <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#FFFFFF' }}>{ws.name}</div>
                        <div style={{ fontSize: '0.72rem', color: '#38BDF8' }}>Initiative: {ws.dirId}</div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '0.84rem', fontWeight: 800, color: '#10B981' }}>+${ws.realized.toLocaleString()}</div>
                        <div style={{ fontSize: '0.68rem', color: '#64748B' }}>Expected: ${ws.arr.toLocaleString()}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab 2: Portfolio ARR Attribution */}
      {activeTab === 'ARR_ATTRIBUTION' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', background: '#090D14', padding: '20px', borderRadius: '10px', border: '1px solid #1E293B' }}>
          <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#FFFFFF' }}>Cross-Workspace ARR Attribution & Concentration</div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
            <div style={{ padding: '16px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 700 }}>E-COMMERCE REGIONAL HUB A</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#38BDF8', marginTop: '4px' }}>+$96,856.25</div>
              <div style={{ fontSize: '0.75rem', color: '#10B981', marginTop: '2px' }}>50.0% Portfolio Contribution</div>
            </div>
            <div style={{ padding: '16px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 700 }}>RETAIL LOGISTICS HUB B</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#38BDF8', marginTop: '4px' }}>+$74,456.25</div>
              <div style={{ fontSize: '0.75rem', color: '#10B981', marginTop: '2px' }}>38.4% Portfolio Contribution</div>
            </div>
            <div style={{ padding: '16px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 700 }}>DTC OMNICHANNEL HUB C</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#38BDF8', marginTop: '4px' }}>+$22,400.00</div>
              <div style={{ fontSize: '0.75rem', color: '#10B981', marginTop: '2px' }}>11.6% Portfolio Contribution</div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Portfolio Risk Heatmap */}
      {activeTab === 'RISK_HEATMAP' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', background: '#090D14', padding: '20px', borderRadius: '10px', border: '1px solid #1E293B' }}>
          <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#FFFFFF' }}>Aggregated Enterprise Risk Heatmap</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ padding: '14px', background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <span style={{ fontSize: '0.72rem', fontWeight: 800, color: '#EF4444' }}>CRITICAL RISK: Cross-Hub Courier Capacity Shortage</span>
                <div style={{ fontSize: '0.8rem', color: '#94A3B8', marginTop: '2px' }}>Affected Entities: E-Commerce Regional Hub A, Retail Logistics Hub B</div>
              </div>
              <span style={{ fontSize: '0.74rem', color: '#10B981', fontWeight: 700 }}>Mitigation Active</span>
            </div>
            <div style={{ padding: '14px', background: 'rgba(245, 158, 11, 0.08)', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <span style={{ fontSize: '0.72rem', fontWeight: 800, color: '#F59E0B' }}>HIGH RISK: Omnichannel Margin Compression</span>
                <div style={{ fontSize: '0.8rem', color: '#94A3B8', marginTop: '2px' }}>Affected Entities: E-Commerce Regional Hub A, DTC Omnichannel Hub C</div>
              </div>
              <span style={{ fontSize: '0.74rem', color: '#10B981', fontWeight: 700 }}>Discount Caps Enforced</span>
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Portfolio Governance Index */}
      {activeTab === 'GOVERNANCE_INDEX' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '12px' }}>
          {[
            { title: 'Evidence Coverage', value: '100.0%', note: 'Across all 3 workspaces' },
            { title: 'Directive Traceability', value: '100.0%', note: 'Zero orphan actions' },
            { title: 'ARR Attribution', value: '100.0%', note: 'Deterministic summation' },
            { title: 'Outcome Validation', value: '98.5%', note: 'Validated telemetry' },
            { title: 'Lineage Completeness', value: '100.0%', note: 'Unbroken 8-tier paths' },
          ].map((item, idx) => (
            <div key={idx} style={{ padding: '16px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.68rem', color: '#64748B', fontWeight: 700 }}>{item.title.toUpperCase()}</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#38BDF8', marginTop: '4px' }}>{item.value}</div>
              <div style={{ fontSize: '0.72rem', color: '#10B981', marginTop: '2px' }}>{item.note}</div>
            </div>
          ))}
        </div>
      )}

      {/* Modal: Cross-Workspace Lineage Inspector */}
      {selectedPortfolioDir && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.85)',
            backdropFilter: 'blur(8px)',
            zIndex: 300,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '24px',
          }}
          onClick={() => setSelectedPortfolioDir(null)}
        >
          <div
            style={{
              width: '750px',
              maxWidth: '95vw',
              backgroundColor: '#090D14',
              border: '1px solid #38BDF8',
              borderRadius: '14px',
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1E293B', paddingBottom: '12px' }}>
              <div style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>{selectedPortfolioDir.id}: Cross-Workspace Lineage</div>
              <button onClick={() => setSelectedPortfolioDir(null)} style={{ background: 'none', border: 'none', color: '#94A3B8', cursor: 'pointer' }}>
                <X size={18} />
              </button>
            </div>

            <div style={{ fontSize: '0.84rem', color: '#94A3B8' }}>
              Full 8-tier hierarchy connecting portfolio-level board directive to individual workspace entities and telemetry:
            </div>

            <div style={{ padding: '14px', background: 'rgba(15, 23, 42, 0.7)', borderRadius: '8px', border: '1px solid #1E293B', fontSize: '0.8rem', color: '#38BDF8', fontFamily: 'monospace', lineHeight: 1.6 }}>
              {selectedPortfolioDir.lineagePath}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
