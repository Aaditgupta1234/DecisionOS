import React from 'react';
import { ShieldCheck, HelpCircle } from 'lucide-react';

interface Props {
  metricCoverage?: number;
  findingCoverage?: number;
  rootCauseCertainty?: number;
  recommendationAgreement?: number;
  overallConfidence?: number;
}

export const ConfidenceBreakdownCard: React.FC<Props> = ({
  metricCoverage = 100,
  findingCoverage = 100,
  rootCauseCertainty = 89,
  recommendationAgreement = 94,
  overallConfidence = 91,
}) => {
  return (
    <div style={{
      background: '#070A0F',
      border: '1px solid #141C28',
      borderRadius: '8px',
      padding: '14px 16px',
      fontSize: '11.5px',
      color: '#CBD5E1',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px', borderBottom: '1px solid #101620', paddingBottom: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <ShieldCheck size={14} color="#10B981" />
          <span style={{ fontWeight: 800, color: '#FFFFFF', textTransform: 'uppercase', fontSize: '10.5px', letterSpacing: '0.04em' }}>
            Confidence Composition Breakdown
          </span>
        </div>
        <span style={{ fontSize: '12px', fontWeight: 800, color: '#10B981' }}>
          {overallConfidence}% Aggregate
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', fontFamily: 'monospace' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ color: '#94A3B8' }}>Metric Telemetry Coverage .............</span>
          <span style={{ color: '#FFFFFF', fontWeight: 700 }}>{metricCoverage}%</span>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ color: '#94A3B8' }}>Diagnostic Finding Coverage ...........</span>
          <span style={{ color: '#FFFFFF', fontWeight: 700 }}>{findingCoverage}%</span>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ color: '#94A3B8' }}>Root Cause DAG Certainty ..............</span>
          <span style={{ color: '#38BDF8', fontWeight: 700 }}>{rootCauseCertainty}%</span>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <span style={{ color: '#94A3B8' }}>Action Engine Agreement ...............</span>
          <span style={{ color: '#10B981', fontWeight: 700 }}>{recommendationAgreement}%</span>
        </div>
      </div>
    </div>
  );
};
