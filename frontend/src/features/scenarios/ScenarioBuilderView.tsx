import React, { useState } from 'react';
import {
  Sliders,
  Play,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  DollarSign,
  ShieldCheck,
  Zap,
  Target,
  Sparkles,
} from 'lucide-react';

export const ScenarioBuilderView: React.FC = () => {
  const [retentionLift, setRetentionLift] = useState(5.0);
  const [courierPenalty, setCourierPenalty] = useState(15.0);
  const [marketingSpend, setMarketingSpend] = useState(25.0);
  const [costReduction, setCostReduction] = useState(10.0);

  // Dynamic simulation calculations
  const expectedArr = Math.round(retentionLift * 18000 + courierPenalty * 1500 + marketingSpend * 800 + costReduction * 1200);
  const healthLift = (retentionLift * 1.4 + courierPenalty * 0.25).toFixed(1);
  const riskReduction = (-1 * (retentionLift * 1.2 + courierPenalty * 0.3)).toFixed(1);
  const strategicScore = Math.min(99.0, Math.max(50.0, 70.0 + retentionLift * 3.5 + courierPenalty * 0.4)).toFixed(1);

  // Capacity constraint check: if marketing > 60% or retention > 8%
  const isSupportViolated = marketingSpend > 60.0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#06B6D4', fontWeight: 800 }}>
          Interactive Simulation Studio
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Scenario Builder & Parameter Tuning
        </h1>
      </div>

      {isSupportViolated && (
        <div style={{ padding: '14px 18px', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '10px', display: 'flex', alignItems: 'center', gap: '10px', color: '#EF4444' }}>
          <AlertTriangle size={18} />
          <div>
            <div style={{ fontSize: '0.85rem', fontWeight: 800 }}>Capacity Constraint Violation: Support Team Headcount</div>
            <div style={{ fontSize: '0.78rem', opacity: 0.9 }}>
              Marketing spend &gt; 60% requires 62 FTEs (exceeding the 50 FTE limit). Strategy may produce customer ticket backlog.
            </div>
          </div>
        </div>
      )}

      {/* Main Grid: Parameters & Real-Time Output Preview */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '20px' }}>
        {/* Tuning Controls */}
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sliders size={18} color="#38BDF8" />
            <span>Adjust Candidate Levers</span>
          </h2>

          {/* Slider 1: Customer Retention */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#F1F5F9' }}>Customer Retention Lift</span>
              <span style={{ fontSize: '0.85rem', fontWeight: 800, color: '#10B981' }}>+{retentionLift}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="10"
              step="0.5"
              value={retentionLift}
              onChange={(e) => setRetentionLift(parseFloat(e.target.value))}
              style={{ width: '100%', accentColor: '#10B981', cursor: 'pointer' }}
            />
          </div>

          {/* Slider 2: Courier SLA Penalty */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#F1F5F9' }}>Courier SLA Penalty Rate</span>
              <span style={{ fontSize: '0.85rem', fontWeight: 800, color: '#38BDF8' }}>{courierPenalty}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="25"
              step="1"
              value={courierPenalty}
              onChange={(e) => setCourierPenalty(parseFloat(e.target.value))}
              style={{ width: '100%', accentColor: '#38BDF8', cursor: 'pointer' }}
            />
          </div>

          {/* Slider 3: Marketing Spend */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#F1F5F9' }}>Marketing Budget Increase</span>
              <span style={{ fontSize: '0.85rem', fontWeight: 800, color: '#A855F7' }}>+{marketingSpend}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="80"
              step="5"
              value={marketingSpend}
              onChange={(e) => setMarketingSpend(parseFloat(e.target.value))}
              style={{ width: '100%', accentColor: '#A855F7', cursor: 'pointer' }}
            />
          </div>

          {/* Slider 4: Logistics Cost Reduction */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#F1F5F9' }}>Logistics Cost Reduction</span>
              <span style={{ fontSize: '0.85rem', fontWeight: 800, color: '#F59E0B' }}>-{costReduction}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="25"
              step="1"
              value={costReduction}
              onChange={(e) => setCostReduction(parseFloat(e.target.value))}
              style={{ width: '100%', accentColor: '#F59E0B', cursor: 'pointer' }}
            />
          </div>
        </div>

        {/* Real-Time Outcome Prediction Card */}
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>
              Real-Time Mathematical Output
            </span>
            <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#10B981', background: 'rgba(16, 185, 129, 0.12)', padding: '2px 8px', borderRadius: '4px' }}>
              StrategicScore: {strategicScore}
            </span>
          </div>

          <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '18px', borderRadius: '10px' }}>
            <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 700 }}>EXPECTED ARR RECOVERY LIFT</div>
            <div style={{ fontSize: '2.4rem', fontWeight: 900, color: '#38BDF8', marginTop: '2px' }}>
              +${expectedArr.toLocaleString()}
            </div>
            <div style={{ fontSize: '0.78rem', color: '#10B981', fontWeight: 700, marginTop: '2px' }}>
              4.8x ROI Capital Multiplier
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '14px', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.68rem', color: '#64748B', fontWeight: 700 }}>HEALTH SCORE LIFT</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#10B981', marginTop: '2px' }}>
                +{healthLift} pts
              </div>
            </div>

            <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '14px', borderRadius: '8px' }}>
              <div style={{ fontSize: '0.68rem', color: '#64748B', fontWeight: 700 }}>RISK REDUCTION</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 900, color: '#F59E0B', marginTop: '2px' }}>
                {riskReduction} pts
              </div>
            </div>
          </div>

          <button
            style={{
              marginTop: 'auto',
              padding: '12px',
              background: '#0284C7',
              border: 'none',
              borderRadius: '8px',
              color: '#FFFFFF',
              fontSize: '0.85rem',
              fontWeight: 800,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
            }}
          >
            <Play size={14} />
            <span>Save & Run 100K Monte Carlo Simulation</span>
          </button>
        </div>
      </div>
    </div>
  );
};
