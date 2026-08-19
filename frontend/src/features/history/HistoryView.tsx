import React from 'react';
import { History, CheckCircle2, ArrowRight, Database, FileSpreadsheet } from 'lucide-react';
import { Link } from 'react-router-dom';

interface AnalysisRun {
  runId: string;
  datasetName: string;
  completedAt: string;
  healthScore: number;
  findingsCount: number;
  recommendationsCount: number;
  status: string;
}

export const HistoryView: React.FC = () => {
  const historyRuns: AnalysisRun[] = [
    {
      runId: 'RUN-2026-0818-01',
      datasetName: 'Olist Ecommerce Dataset (2023–2024)',
      completedAt: 'Aug 18, 2026 • 14:32 UTC',
      healthScore: 82,
      findingsCount: 17,
      recommendationsCount: 6,
      status: 'Completed',
    },
    {
      runId: 'RUN-2026-0815-04',
      datasetName: 'Logistics Courier Performance Batch',
      completedAt: 'Aug 15, 2026 • 09:15 UTC',
      healthScore: 76,
      findingsCount: 22,
      recommendationsCount: 8,
      status: 'Completed',
    },
    {
      runId: 'RUN-2026-0810-02',
      datasetName: 'Customer Retention & Churn Sample',
      completedAt: 'Aug 10, 2026 • 18:40 UTC',
      healthScore: 88,
      findingsCount: 9,
      recommendationsCount: 4,
      status: 'Completed',
    },
  ];

  return (
    <div style={{ padding: '28px 32px', color: '#FFFFFF', maxWidth: '1400px', margin: '0 auto' }}>
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <span style={{ fontSize: '10.5px', fontWeight: 700, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.12)', border: '1px solid rgba(56, 189, 248, 0.28)', padding: '1px 7px', borderRadius: '4px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Audit Registry
          </span>
        </div>
        <h1 style={{ fontSize: '24px', fontWeight: 800, letterSpacing: '-0.02em' }}>
          Analysis Run History
        </h1>
        <p style={{ fontSize: '13px', color: '#94A3B8', marginTop: '4px' }}>
          Historical record of all deterministic intelligence executions across active and archived datasets.
        </p>
      </div>

      <div style={{ background: '#090C12', border: '1px solid #1A2230', borderRadius: '12px', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #141A24', color: '#64748B', textAlign: 'left', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              <th style={{ padding: '14px 20px' }}>Run Identifier</th>
              <th style={{ padding: '14px 16px' }}>Dataset</th>
              <th style={{ padding: '14px 16px' }}>Execution Time</th>
              <th style={{ padding: '14px 16px' }}>Health Score</th>
              <th style={{ padding: '14px 16px' }}>Findings</th>
              <th style={{ padding: '14px 16px' }}>Actions</th>
              <th style={{ padding: '14px 20px', textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {historyRuns.map((run) => (
              <tr key={run.runId} style={{ borderBottom: '1px solid #111620' }}>
                <td style={{ padding: '14px 20px', fontWeight: 700, color: '#38BDF8', fontFamily: 'monospace' }}>
                  {run.runId}
                </td>
                <td style={{ padding: '14px 16px', color: '#FFFFFF', fontWeight: 600 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <FileSpreadsheet size={15} color="#64748B" />
                    <span>{run.datasetName}</span>
                  </div>
                </td>
                <td style={{ padding: '14px 16px', color: '#64748B', fontSize: '12px' }}>
                  {run.completedAt}
                </td>
                <td style={{ padding: '14px 16px' }}>
                  <span style={{ fontSize: '11.5px', fontWeight: 700, color: '#10B981', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.25)', padding: '2px 8px', borderRadius: '4px' }}>
                    {run.healthScore}/100
                  </span>
                </td>
                <td style={{ padding: '14px 16px', color: '#94A3B8' }}>
                  {run.findingsCount} findings
                </td>
                <td style={{ padding: '14px 16px', color: '#94A3B8' }}>
                  {run.recommendationsCount} initiatives
                </td>
                <td style={{ padding: '14px 20px', textAlign: 'right' }}>
                  <Link
                    to="/dashboard"
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                      background: '#111622',
                      border: '1px solid #1F2738',
                      color: '#CBD5E1',
                      padding: '5px 12px',
                      borderRadius: '5px',
                      fontSize: '11.5px',
                      fontWeight: 600,
                      textDecoration: 'none',
                    }}
                  >
                    <span>View Output</span>
                    <ArrowRight size={12} />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default HistoryView;
