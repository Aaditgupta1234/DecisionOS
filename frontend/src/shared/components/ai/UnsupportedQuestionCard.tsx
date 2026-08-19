import React from 'react';
import { AlertOctagon, ShieldAlert, FileQuestion } from 'lucide-react';

interface Props {
  question?: string;
  missingDataRequirements?: string[];
}

export const UnsupportedQuestionCard: React.FC<Props> = ({
  question = 'What will revenue be in Q1 2027?',
  missingDataRequirements = [
    'Forward-Looking Revenue Forecast Model',
    'Macroeconomic Inflation & FX Horizon Telemetry',
    'Historical Multi-Year Seasonal Forecast Baseline',
  ],
}) => {
  return (
    <div style={{
      background: 'rgba(239, 68, 68, 0.05)',
      border: '1px solid rgba(239, 68, 68, 0.28)',
      borderRadius: '8px',
      padding: '16px',
      margin: '12px 0',
      color: '#FFFFFF',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <AlertOctagon size={16} color="#EF4444" />
          <span style={{ fontSize: '11.5px', fontWeight: 800, color: '#F87171', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Zero-Hallucination Guard: Insufficient Grounding Telemetry
          </span>
        </div>

        <span style={{ fontSize: '10px', fontWeight: 700, color: '#EF4444', background: 'rgba(239, 68, 68, 0.15)', padding: '2px 7px', borderRadius: '4px' }}>
          UNSUPPORTED QUERY
        </span>
      </div>

      <p style={{ fontSize: '12.5px', color: '#CBD5E1', lineHeight: 1.5, marginBottom: '12px' }}>
        DecisionOS refuses to invent or hallucinate answers without verified deterministic dataset evidence. The active dataset contains transaction history from <strong>Jan 2024 → Dec 2024</strong>, which does not contain forward-looking projections for this query.
      </p>

      <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '6px', padding: '10px 12px' }}>
        <span style={{ fontSize: '10.5px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700, display: 'block', marginBottom: '4px' }}>
          Missing Evidence Requirements to Answer:
        </span>
        <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '11.5px', color: '#94A3B8', lineHeight: 1.6 }}>
          {missingDataRequirements.map((req, idx) => (
            <li key={idx}>{req}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};
