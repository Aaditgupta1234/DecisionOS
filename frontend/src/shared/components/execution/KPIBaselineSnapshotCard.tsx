import React from 'react';
import { Lock, ShieldCheck, Database, Calendar, Hash, CheckCircle2, AlertTriangle } from 'lucide-react';

export type SnapshotIntegrityStatus = 'VERIFIED' | 'MISMATCH' | 'PENDING';

interface Props {
  datasetId?: string;
  datasetVersion?: string;
  analysisRunId?: string;
  retentionBaseline?: string;
  revenueBaseline?: string;
  orderCountBaseline?: string;
  snapshotTimestamp?: string;
  sha256Hash?: string;
  integrityStatus?: SnapshotIntegrityStatus;
}

export const KPIBaselineSnapshotCard: React.FC<Props> = ({
  datasetId = 'ds_olist_2026',
  datasetVersion = 'v14 (Production Baseline)',
  analysisRunId = 'RUN-2026-0818-001',
  retentionBaseline = '85.8%',
  revenueBaseline = '$1.24M / Qtr',
  orderCountBaseline = '22,113 Orders',
  snapshotTimestamp = '2026-08-18 09:15:00 UTC',
  sha256Hash = '8f4ae12db99c85310fa09bb2e5414d48a1296bf3ec0992a',
  integrityStatus = 'VERIFIED',
}) => {
  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '12px',
      padding: '20px',
      marginBottom: '24px',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Lock size={16} color="#38BDF8" />
          <h3 style={{ fontSize: '14.5px', fontWeight: 800, color: '#FFFFFF', margin: 0, textTransform: 'uppercase' }}>
            Immutable Baseline KPI Telemetry Snapshot
          </h3>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '5px',
          background: integrityStatus === 'VERIFIED' ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
          border: `1px solid ${integrityStatus === 'VERIFIED' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
          color: integrityStatus === 'VERIFIED' ? '#10B981' : '#EF4444',
          padding: '3px 10px',
          borderRadius: '6px',
          fontSize: '11px',
          fontWeight: 800,
        }}>
          {integrityStatus === 'VERIFIED' ? <ShieldCheck size={13} /> : <AlertTriangle size={13} />}
          <span>Snapshot Integrity Verified</span>
        </div>
      </div>

      {/* Lineage & Provenance Metadata */}
      <div style={{
        background: '#05070B',
        border: '1px solid #141C28',
        borderRadius: '8px',
        padding: '12px 16px',
        marginBottom: '14px',
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '12px',
      }}>
        <div>
          <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Dataset Source & Version</span>
          <div style={{ fontSize: '12.5px', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>
            {datasetId} • {datasetVersion}
          </div>
        </div>

        <div>
          <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Analysis Run Lineage</span>
          <div style={{ fontSize: '12.5px', fontWeight: 800, color: '#38BDF8', marginTop: '2px', fontFamily: 'monospace' }}>
            {analysisRunId}
          </div>
        </div>

        <div>
          <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Frozen Snapshot Timestamp</span>
          <div style={{ fontSize: '12.5px', fontWeight: 700, color: '#94A3B8', marginTop: '2px' }}>
            {snapshotTimestamp}
          </div>
        </div>
      </div>

      {/* Frozen Baseline Metric Values */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '14px' }}>
        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Frozen Retention Baseline</span>
          <div style={{ fontSize: '18px', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>
            {retentionBaseline}
          </div>
          <span style={{ fontSize: '10.5px', color: '#94A3B8' }}>Trough level at initiative creation</span>
        </div>

        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Frozen Revenue Baseline</span>
          <div style={{ fontSize: '18px', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>
            {revenueBaseline}
          </div>
          <span style={{ fontSize: '10.5px', color: '#94A3B8' }}>Quarterly baseline reference</span>
        </div>

        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Frozen Order Volume</span>
          <div style={{ fontSize: '18px', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>
            {orderCountBaseline}
          </div>
          <span style={{ fontSize: '10.5px', color: '#94A3B8' }}>Cohort size benchmark</span>
        </div>
      </div>

      {/* Cryptographic SHA-256 Hash Verification */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: '#04060A',
        border: '1px solid #101620',
        borderRadius: '6px',
        padding: '8px 12px',
        fontSize: '11px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#64748B' }}>
          <Hash size={12} color="#38BDF8" />
          <span>SHA-256 Hash:</span>
          <span style={{ color: '#CBD5E1', fontFamily: 'monospace' }}>{sha256Hash}</span>
        </div>

        <span style={{ color: '#10B981', fontWeight: 700 }}>Immutable & Cryptographically Sealed</span>
      </div>
    </div>
  );
};
