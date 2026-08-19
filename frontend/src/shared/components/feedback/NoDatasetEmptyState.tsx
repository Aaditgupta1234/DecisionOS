import React from 'react';
import { Database, Upload, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

interface Props {
  title?: string;
  description?: string;
  actionText?: string;
  actionTo?: string;
}

export const NoDatasetEmptyState: React.FC<Props> = ({
  title = 'No Active Dataset Selected',
  description = 'Upload a CSV dataset to initiate the 8-stage DecisionOS intelligence pipeline and generate executive metrics, diagnostic findings, and actionable recommendations.',
  actionText = 'Go to Datasets & Upload CSV',
  actionTo = '/datasets',
}) => {
  return (
    <div style={{
      background: 'rgba(8, 11, 16, 0.75)',
      border: '1px solid #1A2230',
      borderRadius: '12px',
      padding: '48px 24px',
      textAlign: 'center',
      backdropFilter: 'blur(12px)',
      boxShadow: '0 15px 35px rgba(0,0,0,0.6)',
      maxWidth: '540px',
      margin: '40px auto',
    }}>
      <div style={{
        width: '56px',
        height: '56px',
        borderRadius: '50%',
        background: 'rgba(56, 189, 248, 0.1)',
        border: '1px solid rgba(56, 189, 248, 0.25)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        margin: '0 auto 16px',
        boxShadow: '0 0 20px rgba(56, 189, 248, 0.2)',
      }}>
        <Database size={24} color="#38BDF8" />
      </div>

      <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#FFFFFF', marginBottom: '8px', letterSpacing: '-0.02em' }}>
        {title}
      </h3>

      <p style={{ fontSize: '13px', color: '#94A3B8', lineHeight: 1.6, maxWidth: '440px', margin: '0 auto 24px' }}>
        {description}
      </p>

      <Link
        to={actionTo}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          background: '#1D4ED8',
          border: '1px solid #3B82F6',
          color: '#FFFFFF',
          padding: '10px 20px',
          borderRadius: '7px',
          fontSize: '13px',
          fontWeight: 700,
          textDecoration: 'none',
          boxShadow: '0 0 16px rgba(59, 130, 246, 0.3)',
        }}
      >
        <Upload size={14} />
        <span>{actionText}</span>
        <ArrowRight size={14} />
      </Link>
    </div>
  );
};
