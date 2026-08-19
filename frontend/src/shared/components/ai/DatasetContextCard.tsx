import React from 'react';
import { Database, FileSpreadsheet, Activity, AlertTriangle, GitMerge, CheckCircle2, Calendar } from 'lucide-react';

interface Props {
  datasetName?: string;
  rowCount?: string;
  timePeriod?: string;
  metricCount?: number;
  findingCount?: number;
  rootCauseCount?: number;
  recommendationCount?: number;
  lastAnalysis?: string;
}

export const DatasetContextCard: React.FC<Props> = ({
  datasetName = 'Olist Ecommerce Dataset (2023–2024)',
  rowCount = '100,000 orders',
  timePeriod = 'Jan 2024 → Dec 2024',
  metricCount = 8,
  findingCount = 17,
  rootCauseCount = 6,
  recommendationCount = 6,
  lastAnalysis = '18 Aug 2026 • Verified',
}) => {
  return (
    <div style={{
      background: 'linear-gradient(135deg, #090E17 0%, #06090F 100%)',
      border: '1px solid #1A2536',
      borderRadius: '10px',
      padding: '14px 18px',
      marginBottom: '20px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      flexWrap: 'wrap',
      gap: '12px',
    }}>
      {/* Left: Active Dataset Badge */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '8px',
          background: 'rgba(56, 189, 248, 0.12)',
          border: '1px solid rgba(56, 189, 248, 0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <Database size={16} color="#38BDF8" />
        </div>

        <div>
          <div style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
            Active Intelligence Context
          </div>
          <div style={{ fontSize: '13px', fontWeight: 800, color: '#FFFFFF' }}>
            {datasetName}
          </div>
        </div>
      </div>

      {/* Center: Metadata Badges */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px', fontSize: '11.5px', color: '#94A3B8' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <FileSpreadsheet size={13} color="#64748B" />
          <span>{rowCount}</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Calendar size={13} color="#64748B" />
          <span>{timePeriod}</span>
        </div>
      </div>

      {/* Right: Grounded Telemetry Counts */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ fontSize: '10.5px', fontWeight: 700, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.08)', padding: '3px 7px', borderRadius: '4px', border: '1px solid rgba(56, 189, 248, 0.2)' }}>
          {metricCount} KPIs
        </span>
        <span style={{ fontSize: '10.5px', fontWeight: 700, color: '#EF4444', background: 'rgba(239, 68, 68, 0.08)', padding: '3px 7px', borderRadius: '4px', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
          {findingCount} Findings
        </span>
        <span style={{ fontSize: '10.5px', fontWeight: 700, color: '#F59E0B', background: 'rgba(245, 158, 11, 0.08)', padding: '3px 7px', borderRadius: '4px', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
          {rootCauseCount} Root Causes
        </span>
        <span style={{ fontSize: '10.5px', fontWeight: 700, color: '#10B981', background: 'rgba(16, 185, 129, 0.08)', padding: '3px 7px', borderRadius: '4px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
          {recommendationCount} Actions
        </span>
      </div>
    </div>
  );
};
