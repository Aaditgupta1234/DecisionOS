import React from 'react';
import { Target, CheckCircle2, TrendingUp, AlertCircle, BarChart3, ShieldCheck } from 'lucide-react';

export const ScenarioAccuracyTrackerView: React.FC = () => {
  const accuracyReports = [
    {
      id: 'ACC-01',
      scenarioName: 'Scenario A: Retention First & Courier SLA',
      type: 'RETENTION_FIRST',
      predictedArr: '+$124,000',
      actualArr: '+$118,000',
      variance: '4.8%',
      accuracy: '95.2%',
      healthLift: '+10.5 pts (Pred: +11.0)',
      rank: '#1 Most Reliable',
      status: 'CALIBRATED',
    },
    {
      id: 'ACC-02',
      scenarioName: 'Scenario C: Warehouse Load Consolidation',
      type: 'EFFICIENCY_BOOST',
      predictedArr: '+$72,000',
      actualArr: '+$68,500',
      variance: '4.9%',
      accuracy: '95.1%',
      healthLift: '+5.0 pts (Pred: +5.2)',
      rank: '#2 Most Reliable',
      status: 'CALIBRATED',
    },
    {
      id: 'ACC-03',
      scenarioName: 'Scenario B: Growth & Acquisition Burst',
      type: 'GROWTH_OPTIMIZATION',
      predictedArr: '+$98,000',
      actualArr: '+$89,000',
      variance: '9.2%',
      accuracy: '90.8%',
      healthLift: '+6.8 pts (Pred: +7.5)',
      rank: '#3 Most Reliable',
      status: 'CALIBRATING',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#F59E0B', fontWeight: 800 }}>
          Self-Learning Empirical Calibration Layer
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Scenario Accuracy & Model Calibration
        </h1>
      </div>

      {/* Accuracy Summary Bar */}
      <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>AVERAGE DIGITAL TWIN ACCURACY</div>
          <div style={{ fontSize: '2rem', fontWeight: 900, color: '#10B981', marginTop: '2px' }}>95.2%</div>
        </div>
        <div>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>PREDICTION VARIANCE ENVELOPE</div>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#38BDF8', marginTop: '2px' }}>±4.8% Mean Delta</div>
        </div>
        <div>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>CALIBRATION CYCLES</div>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#A855F7', marginTop: '2px' }}>42 Verified Runs</div>
        </div>
      </div>

      {/* Accuracy Records List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {accuracyReports.map((item) => (
          <div
            key={item.id}
            style={{
              background: '#090D14',
              border: '1px solid #1E293B',
              borderRadius: '12px',
              padding: '20px',
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '0.72rem', fontWeight: 800, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.12)', padding: '2px 8px', borderRadius: '4px' }}>
                  {item.rank}
                </span>
                <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>{item.scenarioName}</span>
              </div>
              <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#10B981', background: 'rgba(16, 185, 129, 0.15)', padding: '3px 10px', borderRadius: '12px' }}>
                ✓ {item.accuracy} Accuracy
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '10px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '12px', borderRadius: '8px' }}>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>PREDICTED ARR</div>
                <div style={{ fontSize: '1rem', fontWeight: 800, color: '#94A3B8', marginTop: '2px' }}>{item.predictedArr}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>ACTUAL REALIZED ARR</div>
                <div style={{ fontSize: '1rem', fontWeight: 800, color: '#10B981', marginTop: '2px' }}>{item.actualArr}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>VARIANCE</div>
                <div style={{ fontSize: '1rem', fontWeight: 800, color: '#38BDF8', marginTop: '2px' }}>{item.variance}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>HEALTH REALIZATION</div>
                <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#F1F5F9', marginTop: '2px' }}>{item.healthLift}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
