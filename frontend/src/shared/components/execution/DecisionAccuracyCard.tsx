import React from 'react';
import { Target, TrendingUp, Award, ShieldCheck, CheckCircle2 } from 'lucide-react';

interface Props {
  avgPrecision?: number;
  lastRunsPrecision?: number;
  priorRunsPrecision?: number;
  learningLift?: number;
  rootCauseAccuracy?: number;
  recommendationReliability?: number;
}

export const DecisionAccuracyCard: React.FC<Props> = ({
  avgPrecision = 68.8,
  lastRunsPrecision = 72.4,
  priorRunsPrecision = 65.1,
  learningLift = 7.3,
  rootCauseAccuracy = 89,
  recommendationReliability = 94,
}) => {
  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '12px',
      padding: '20px',
      marginBottom: '24px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Target size={16} color="#38BDF8" />
          <h3 style={{ fontSize: '14.5px', fontWeight: 800, color: '#FFFFFF', margin: 0, textTransform: 'uppercase' }}>
            Decision Intelligence Precision & Engine Accuracy Trend
          </h3>
        </div>
        <span style={{ fontSize: '10.5px', color: '#10B981', fontWeight: 700, background: 'rgba(16, 185, 129, 0.1)', padding: '2px 8px', borderRadius: '4px' }}>
          +{learningLift}% Learning Gain
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '14px' }}>
        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Recovery Realization Precision</span>
          <div style={{ fontSize: '18px', fontWeight: 800, color: '#10B981', marginTop: '2px' }}>
            {avgPrecision}%
          </div>
          <span style={{ fontSize: '10.5px', color: '#94A3B8' }}>Actual vs. Predicted ARR</span>
        </div>

        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Learning Rate (Last 30 Runs)</span>
          <div style={{ fontSize: '18px', fontWeight: 800, color: '#38BDF8', marginTop: '2px' }}>
            {lastRunsPrecision}% vs {priorRunsPrecision}%
          </div>
          <span style={{ fontSize: '10.5px', color: '#10B981' }}>+{learningLift}% precision increase</span>
        </div>

        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Root Cause & Action Validity</span>
          <div style={{ fontSize: '18px', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>
            {rootCauseAccuracy}% / {recommendationReliability}%
          </div>
          <span style={{ fontSize: '10.5px', color: '#94A3B8' }}>DAG Certainty / Rec Reliability</span>
        </div>
      </div>

      <p style={{ fontSize: '11.5px', color: '#94A3B8', margin: 0, lineHeight: 1.45 }}>
        DecisionOS continuously validates deterministic prediction precision against verified outcome telemetry, improving historical accuracy by <strong>+{learningLift}%</strong> across subsequent execution runs.
      </p>
    </div>
  );
};
