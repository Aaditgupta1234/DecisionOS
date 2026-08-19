import React, { useState } from 'react';
import { Sliders, Zap, TrendingUp, CheckSquare, Square, ShieldCheck, ArrowRight } from 'lucide-react';

interface SimulatorOption {
  id: string;
  title: string;
  revenueGain: number;
  healthLift: number;
  retentionLift: number;
  selected: boolean;
}

export const ImpactSimulatorCard: React.FC = () => {
  const [options, setOptions] = useState<SimulatorOption[]>([
    { id: 'rec_1', title: 'Targeted Win-Back Campaign & Courier SLA Penalties', revenueGain: 180, healthLift: 4, retentionLift: 3.6, selected: true },
    { id: 'rec_2', title: 'Dynamic Dispatch Load-Balancing Across Secondary Hubs', revenueGain: 140, healthLift: 3, retentionLift: 1.8, selected: true },
    { id: 'rec_3', title: 'Automated Post-Purchase Cross-Sell Engine', revenueGain: 85, healthLift: 2, retentionLift: 0.9, selected: false },
    { id: 'rec_4', title: 'One-Click Payment Gateway Integration', revenueGain: 40, healthLift: 1, retentionLift: 0.4, selected: false },
  ]);

  const toggleOption = (id: string) => {
    setOptions(options.map(o => o.id === id ? { ...o, selected: !o.selected } : o));
  };

  const baseHealth = 82;
  const baseRetention = 85.8;

  const totalGain = options.filter(o => o.selected).reduce((acc, curr) => acc + curr.revenueGain, 0);
  const totalHealthLift = options.filter(o => o.selected).reduce((acc, curr) => acc + curr.healthLift, 0);
  const totalRetentionLift = options.filter(o => o.selected).reduce((acc, curr) => acc + curr.retentionLift, 0);

  const projectedHealth = Math.min(100, baseHealth + totalHealthLift);
  const projectedRetention = Math.min(100, Number((baseRetention + totalRetentionLift).toFixed(1)));

  return (
    <div style={{
      background: 'linear-gradient(135deg, #090E17 0%, #06090F 100%)',
      border: '1px solid #1E293B',
      borderRadius: '12px',
      padding: '20px 22px',
      marginBottom: '24px',
      boxShadow: '0 12px 30px rgba(0, 0, 0, 0.6)',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sliders size={16} color="#10B981" />
          <h3 style={{ fontSize: '14.5px', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.01em', margin: 0, textTransform: 'uppercase' }}>
            Executive Recommendation Impact Simulator
          </h3>
        </div>
        <span style={{ fontSize: '10.5px', color: '#10B981', fontWeight: 700, background: 'rgba(16, 185, 129, 0.1)', padding: '2px 8px', borderRadius: '4px' }}>
          Deterministic Scenario Sandbox
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '20px' }}>
        {/* Left: Initiative Toggles */}
        <div>
          <div style={{ fontSize: '11px', color: '#94A3B8', fontWeight: 700, textTransform: 'uppercase', marginBottom: '10px' }}>
            Toggle Initiatives to Model Combined Business Outcomes:
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {options.map((opt) => (
              <div
                key={opt.id}
                onClick={() => toggleOption(opt.id)}
                style={{
                  background: opt.selected ? 'rgba(16, 185, 129, 0.08)' : '#05070B',
                  border: `1px solid ${opt.selected ? 'rgba(16, 185, 129, 0.3)' : '#141C28'}`,
                  borderRadius: '6px',
                  padding: '10px 12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  cursor: 'pointer',
                  fontSize: '12px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  {opt.selected ? (
                    <CheckSquare size={16} color="#10B981" />
                  ) : (
                    <Square size={16} color="#64748B" />
                  )}
                  <span style={{ fontWeight: opt.selected ? 700 : 500, color: opt.selected ? '#FFFFFF' : '#94A3B8' }}>
                    {opt.title}
                  </span>
                </div>

                <span style={{ fontWeight: 800, color: opt.selected ? '#10B981' : '#64748B' }}>
                  +${opt.revenueGain}K ARR
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Projected Business Lift Scorecards */}
        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '16px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontSize: '11px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700, marginBottom: '12px' }}>
              Simulated Performance Projection
            </div>

            {/* Projected Health Score */}
            <div style={{ marginBottom: '14px' }}>
              <span style={{ fontSize: '11px', color: '#94A3B8' }}>Projected Health Score</span>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                <span style={{ fontSize: '22px', fontWeight: 800, color: '#FFFFFF' }}>{projectedHealth} / 100</span>
                <span style={{ fontSize: '12px', fontWeight: 800, color: '#10B981' }}>+{totalHealthLift} pts lift</span>
              </div>
            </div>

            {/* Projected Retention */}
            <div style={{ marginBottom: '14px' }}>
              <span style={{ fontSize: '11px', color: '#94A3B8' }}>Projected Customer Retention</span>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                <span style={{ fontSize: '18px', fontWeight: 800, color: '#FFFFFF' }}>{projectedRetention}%</span>
                <span style={{ fontSize: '12px', fontWeight: 800, color: '#38BDF8' }}>+{totalRetentionLift}%</span>
              </div>
            </div>

            {/* Projected Net ARR Recovery */}
            <div>
              <span style={{ fontSize: '11px', color: '#94A3B8' }}>Net Projected ARR Recovery</span>
              <div style={{ fontSize: '20px', fontWeight: 800, color: '#10B981' }}>
                +${totalGain}K ARR
              </div>
            </div>
          </div>

          <div style={{ fontSize: '10.5px', color: '#64748B', borderTop: '1px solid #0F1622', paddingTop: '10px', marginTop: '12px' }}>
            Telemetry derived from active dataset elasticity models.
          </div>
        </div>
      </div>
    </div>
  );
};
