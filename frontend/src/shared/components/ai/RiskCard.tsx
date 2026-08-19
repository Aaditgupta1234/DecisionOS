import React from 'react';
import { AlertTriangle, ShieldAlert, ArrowRight, GitMerge } from 'lucide-react';
import { Link } from 'react-router-dom';

interface Props {
  title: string;
  financialExposure: string;
  confidence?: number;
  affectedKpi: string;
  rootCauseTitle: string;
  rootCauseId?: string;
}

export const RiskCard: React.FC<Props> = ({
  title,
  financialExposure,
  confidence = 94,
  affectedKpi,
  rootCauseTitle,
  rootCauseId = 'rc_1',
}) => {
  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '10px',
      padding: '16px 18px',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
    }}>
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <AlertTriangle size={14} color="#EF4444" />
            <span style={{ fontSize: '10.5px', fontWeight: 800, color: '#F87171', textTransform: 'uppercase' }}>
              Identified Risk Vector
            </span>
          </div>

          <span style={{ fontSize: '10.5px', color: '#64748B', fontWeight: 600 }}>
            {confidence}% Confidence
          </span>
        </div>

        <h4 style={{ fontSize: '14px', fontWeight: 800, color: '#FFFFFF', margin: '0 0 6px' }}>
          {title}
        </h4>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11.5px', color: '#94A3B8', marginBottom: '12px' }}>
          <GitMerge size={12} color="#F59E0B" />
          <span>Root Cause: <strong style={{ color: '#E2E8F0' }}>{rootCauseTitle}</strong></span>
        </div>
      </div>

      <div style={{ borderTop: '1px solid #141C28', paddingTop: '10px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <span style={{ fontSize: '10px', color: '#64748B', display: 'block', textTransform: 'uppercase' }}>Financial Exposure</span>
          <span style={{ fontSize: '14px', fontWeight: 800, color: '#EF4444' }}>{financialExposure}</span>
        </div>

        <Link
          to={`/root-causes?rootCauseId=${rootCauseId}`}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            background: '#111622',
            border: '1px solid #1F2738',
            color: '#38BDF8',
            padding: '5px 10px',
            borderRadius: '5px',
            fontSize: '11px',
            fontWeight: 700,
            textDecoration: 'none',
          }}
        >
          <span>Trace DAG</span>
          <ArrowRight size={11} />
        </Link>
      </div>
    </div>
  );
};
