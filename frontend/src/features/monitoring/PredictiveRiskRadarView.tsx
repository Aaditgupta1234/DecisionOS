import React from 'react';
import { Sparkles, TrendingDown, ShieldAlert, ArrowLeft, CheckCircle2, Play } from 'lucide-react';
import { Link } from 'react-router-dom';

export const PredictiveRiskRadarView: React.FC = () => {
  const predictedRisks = [
    {
      kpi: 'Customer Retention Rate',
      current: '84.2%',
      projected30d: '78.9% (-5.3% Decline)',
      projectedLoss: '-$148,000 ARR',
      confidence: '91.0%',
      hedge: 'Enforce courier SLA billing penalties and deploy $25.8K delay tokens to Southeastern accounts.',
      leadTimeAccuracy: '93% (24-day lead)',
    },
    {
      kpi: 'Regional Freight Unit Cost',
      current: '$14.20/unit',
      projected30d: '$16.80/unit (+18.3% Surge)',
      projectedLoss: '-$64,000 ARR',
      confidence: '88.5%',
      hedge: 'Consolidate parcel freight loads into northern regional distribution hubs.',
      leadTimeAccuracy: '90% (18-day lead)',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      <div>
        <Link
          to="/monitoring-center"
          style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: '#64748B', fontSize: '0.8rem', fontWeight: 700, textDecoration: 'none', marginBottom: '8px' }}
        >
          <ArrowLeft size={14} />
          <span>Back to Monitoring Command Center</span>
        </Link>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#F59E0B', fontWeight: 800 }}>
          Horizon Drift & Projected Reality
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Predictive Risk Radar (30–90 Day Horizon)
        </h1>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {predictedRisks.map((risk, idx) => (
          <div
            key={idx}
            style={{
              background: '#090D14',
              border: '1px solid #1E293B',
              borderRadius: '14px',
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              gap: '14px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <ShieldAlert size={18} color="#EF4444" />
                <span style={{ fontSize: '1.1rem', fontWeight: 900, color: '#FFFFFF' }}>{risk.kpi}</span>
              </div>
              <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#F59E0B', background: 'rgba(245, 158, 11, 0.15)', padding: '3px 10px', borderRadius: '12px' }}>
                Predictive Accuracy: {risk.leadTimeAccuracy}
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '14px', borderRadius: '8px' }}>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>CURRENT VALUE</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#94A3B8', marginTop: '2px' }}>{risk.current}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>PROJECTED 30-DAY VALUE</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 900, color: '#EF4444', marginTop: '2px' }}>{risk.projected30d}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>PROJECTED ARR RISK</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 900, color: '#EF4444', marginTop: '2px' }}>{risk.projectedLoss}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>CERTAINTY SCORE</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#38BDF8', marginTop: '2px' }}>{risk.confidence}</div>
              </div>
            </div>

            <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: '12px 16px', borderRadius: '8px', fontSize: '0.82rem', color: '#F1F5F9' }}>
              <strong style={{ color: '#10B981' }}>Proactive Autonomous Hedging Recommendation: </strong>
              {risk.hedge}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
