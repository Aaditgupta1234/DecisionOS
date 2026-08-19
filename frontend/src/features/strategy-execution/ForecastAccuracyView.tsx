import React from 'react';
import { Sparkles, TrendingUp, ShieldCheck, Target, CheckCircle2 } from 'lucide-react';

export const ForecastAccuracyView: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#F59E0B', fontWeight: 800 }}>
          Continuous Digital Twin Feedback Loop
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Forecast Calibration & Accuracy Dashboard
        </h1>
      </div>

      {/* Metrics Bar */}
      <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '24px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>MEAN ACCURACY</div>
          <div style={{ fontSize: '2rem', fontWeight: 900, color: '#10B981', marginTop: '2px' }}>95.2%</div>
        </div>
        <div>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>MAPE (ERROR RATE)</div>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#38BDF8', marginTop: '2px' }}>4.8%</div>
        </div>
        <div>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>FORECAST BIAS</div>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#F59E0B', marginTop: '2px' }}>-1.2% (Conservative)</div>
        </div>
        <div>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>CALIBRATION STATE</div>
          <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#10B981', marginTop: '2px' }}>STABLE</div>
        </div>
      </div>
    </div>
  );
};
