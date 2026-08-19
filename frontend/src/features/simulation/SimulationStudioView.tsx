import React, { useState } from 'react';
import { Play, TrendingUp, DollarSign, ShieldAlert, CheckCircle2, ChevronRight, Zap, RefreshCw } from 'lucide-react';
import { ExplainabilityDrawer } from '../../components/workspace/ExplainabilityDrawer';

export const SimulationStudioView: React.FC = () => {
  const [selectedPath, setSelectedPath] = useState<'PATH_A' | 'PATH_B' | 'PATH_C'>('PATH_A');
  const [isExplainOpen, setIsExplainOpen] = useState(false);

  const paths = [
    {
      id: 'PATH_A',
      name: 'Recovery Path A: Retention First & Courier SLA Fix',
      confidence: 0.94,
      expected_arr: '+$124,000',
      health_lift: '+11.0 pts',
      risk: 'Low (-10.2)',
      roi: '4.8x ROI',
      desc: 'Focuses on regional carrier rebalancing in Southeastern corridors. Resolves dispatch bottlenecks and churn.',
      recommended: true,
    },
    {
      id: 'PATH_B',
      name: 'Recovery Path B: Growth First & Corridor Expansion',
      confidence: 0.88,
      expected_arr: '+$98,000',
      health_lift: '+7.5 pts',
      risk: 'Moderate (-4.5)',
      roi: '3.2x ROI',
      desc: 'Expands into adjacent northern regional corridors with new carrier contracts.',
      recommended: false,
    },
    {
      id: 'PATH_C',
      name: 'Recovery Path C: Conservative Minimum Intervention',
      confidence: 0.79,
      expected_arr: '+$45,000',
      health_lift: '+3.2 pts',
      risk: 'Minimal (-1.5)',
      roi: '2.1x ROI',
      desc: 'Applies automated software retries with zero discretionary carrier budget.',
      recommended: false,
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#38BDF8', fontWeight: 800 }}>
            Enterprise Digital Twin & Monte Carlo Engine
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Simulation & Recovery Studio
          </h1>
        </div>

        <button
          onClick={() => {}}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            background: '#0284C7',
            border: 'none',
            borderRadius: '6px',
            color: '#FFFFFF',
            fontSize: '0.85rem',
            fontWeight: 700,
            cursor: 'pointer',
          }}
        >
          <Play size={14} />
          <span>Run Monte Carlo Sim</span>
        </button>
      </div>

      {/* Multi-Run Simulation Comparison Matrix */}
      <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '12px', padding: '20px' }}>
        <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '14px' }}>
          Multi-Run Simulation Comparison Matrix (SIM-V1 vs SIM-V2 vs SIM-V3)
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #1E293B', color: '#64748B', textTransform: 'uppercase', fontSize: '0.7rem' }}>
                <th style={{ padding: '10px 14px' }}>Simulation Run</th>
                <th style={{ padding: '10px 14px' }}>Scenario Name</th>
                <th style={{ padding: '10px 14px' }}>Projected ARR Recovery</th>
                <th style={{ padding: '10px 14px' }}>Retention Lift</th>
                <th style={{ padding: '10px 14px' }}>Health Delta</th>
                <th style={{ padding: '10px 14px' }}>Certainty Score</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: '1px solid #141A24', background: 'rgba(56, 189, 248, 0.04)' }}>
                <td style={{ padding: '12px 14px', fontWeight: 700, color: '#38BDF8' }}>SIM-V3 (Active)</td>
                <td style={{ padding: '12px 14px', color: '#F1F5F9' }}>Carrier Rebalancing & Courier SLA Penalties</td>
                <td style={{ padding: '12px 14px', fontWeight: 800, color: '#10B981' }}>+$124,000</td>
                <td style={{ padding: '12px 14px', color: '#10B981' }}>+4.7% (84.2%)</td>
                <td style={{ padding: '12px 14px', fontWeight: 700, color: '#38BDF8' }}>+11.0 pts</td>
                <td style={{ padding: '12px 14px', fontWeight: 800, color: '#A855F7' }}>94.0%</td>
              </tr>
              <tr style={{ borderBottom: '1px solid #141A24' }}>
                <td style={{ padding: '12px 14px', fontWeight: 700, color: '#94A3B8' }}>SIM-V2</td>
                <td style={{ padding: '12px 14px', color: '#F1F5F9' }}>Win-Back Email Incentives Alone</td>
                <td style={{ padding: '12px 14px', fontWeight: 800, color: '#F59E0B' }}>+$82,000</td>
                <td style={{ padding: '12px 14px', color: '#F59E0B' }}>+2.5% (82.0%)</td>
                <td style={{ padding: '12px 14px', color: '#94A3B8' }}>+6.2 pts</td>
                <td style={{ padding: '12px 14px', color: '#94A3B8' }}>86.5%</td>
              </tr>
              <tr>
                <td style={{ padding: '12px 14px', fontWeight: 700, color: '#94A3B8' }}>SIM-V1 (Baseline)</td>
                <td style={{ padding: '12px 14px', color: '#F1F5F9' }}>Status Quo (No Remedial Intervention)</td>
                <td style={{ padding: '12px 14px', fontWeight: 800, color: '#EF4444' }}>-$42,000</td>
                <td style={{ padding: '12px 14px', color: '#EF4444' }}>-7.3% (79.5%)</td>
                <td style={{ padding: '12px 14px', color: '#EF4444' }}>-5.0 pts</td>
                <td style={{ padding: '12px 14px', color: '#94A3B8' }}>74.0%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Recovery Paths Selection Grid */}
      <div>
        <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#FFFFFF', marginBottom: '12px' }}>
          Autonomous Recovery Paths Explorer
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
          {paths.map((p) => {
            const isSelected = selectedPath === p.id;
            return (
              <div
                key={p.id}
                onClick={() => setSelectedPath(p.id as any)}
                style={{
                  background: isSelected ? 'linear-gradient(135deg, rgba(56, 189, 248, 0.12), rgba(9, 13, 20, 0.95))' : '#090D14',
                  border: `1px solid ${isSelected ? '#38BDF8' : '#1E293B'}`,
                  borderRadius: '12px',
                  padding: '20px',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '12px',
                  boxShadow: isSelected ? '0 10px 30px rgba(56, 189, 248, 0.15)' : 'none',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  {p.recommended ? (
                    <span style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#10B981', padding: '3px 8px', borderRadius: '4px', fontSize: '0.68rem', fontWeight: 800, textTransform: 'uppercase' }}>
                      ★ Recommended Path
                    </span>
                  ) : (
                    <span style={{ color: '#64748B', fontSize: '0.68rem', fontWeight: 700 }}>ALTERNATIVE PATH</span>
                  )}
                  <span style={{ color: '#A855F7', fontSize: '0.78rem', fontWeight: 800 }}>
                    {Math.round(p.confidence * 100)}% Certainty
                  </span>
                </div>

                <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#FFFFFF' }}>{p.name}</div>
                <div style={{ fontSize: '0.82rem', color: '#94A3B8', lineHeight: 1.5 }}>{p.desc}</div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '6px', padding: '10px', marginTop: 'auto' }}>
                  <div>
                    <div style={{ fontSize: '0.68rem', color: '#64748B' }}>Expected ARR</div>
                    <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#10B981' }}>{p.expected_arr}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '0.68rem', color: '#64748B' }}>Health Lift</div>
                    <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#38BDF8' }}>{p.health_lift}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '0.68rem', color: '#64748B' }}>ROI Multiplier</div>
                    <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#A855F7' }}>{p.roi}</div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Explainability Drawer */}
      <ExplainabilityDrawer
        isOpen={isExplainOpen}
        onClose={() => setIsExplainOpen(false)}
        title="Recovery Path A Digital Twin Simulation"
        metricValue="+$124,000 Expected ARR Yield (94.0% Confidence)"
      />
    </div>
  );
};
