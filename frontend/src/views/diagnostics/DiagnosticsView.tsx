import React, { useEffect, useState } from 'react';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { DiagnosticFinding, FindingSeverity } from '../../types';
import { LoadingSkeleton } from '../../components/feedback/LoadingSkeleton';
import { ErrorBanner } from '../../components/feedback/ErrorBanner';
import { EmptyState } from '../../components/feedback/EmptyState';
import { AlertTriangle, ShieldAlert, ChevronDown, ChevronUp } from 'lucide-react';

export const DiagnosticsView: React.FC = () => {
  const { activeDataset } = useDataset();
  const [findings, setFindings] = useState<DiagnosticFinding[]>([]);
  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL');
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDiagnostics = async (datasetId: string) => {
    try {
      setLoading(true);
      setError(null);
      const report = await DecisionApi.getIntelligenceReport(datasetId);
      setFindings(report.findings || []);
    } catch (err: any) {
      console.error('Failed to load diagnostics:', err);
      setError(err?.message || 'Could not fetch diagnostic findings for this dataset.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeDataset?.id) {
      fetchDiagnostics(activeDataset.id);
    } else {
      setLoading(false);
    }
  }, [activeDataset?.id]);

  if (!activeDataset) {
    return (
      <div className="page-container">
        <EmptyState
          title="No Active Dataset Selected"
          description="Select a dataset to inspect its diagnostic findings."
          icon={AlertTriangle}
        />
      </div>
    );
  }

  // Count by severity
  const severityCounts: Record<string, number> = {
    CRITICAL: 0,
    HIGH: 0,
    MEDIUM: 0,
    LOW: 0,
    INFO: 0,
  };
  findings.forEach((f) => {
    if (severityCounts[f.severity] !== undefined) {
      severityCounts[f.severity]++;
    }
  });

  const filteredFindings = findings.filter(
    (f) => selectedSeverity === 'ALL' || f.severity === selectedSeverity
  );

  const getSeverityBadgeClass = (sev: FindingSeverity) => {
    switch (sev) {
      case 'CRITICAL':
      case 'HIGH':
        return 'badge-danger';
      case 'MEDIUM':
        return 'badge-warning';
      case 'LOW':
        return 'badge-primary';
      default:
        return 'badge-neutral';
    }
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
          <span className="badge badge-primary">Phase 5.1–5.5 Diagnostic Core</span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Deterministic Rule Engine & Anomaly Detection
          </span>
        </div>
        <h1>Business Diagnostic Findings</h1>
        <p style={{ marginTop: '4px', fontSize: '0.9rem' }}>
          Systematic rule-based evaluation detecting revenue stagnation, margin compression, churn spikes, and operational bottlenecks.
        </p>
      </div>

      {error && <ErrorBanner message={error} onRetry={() => fetchDiagnostics(activeDataset.id)} />}

      {/* Severity Summary Bar */}
      <div
        className="card"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '16px',
          marginBottom: '20px',
          padding: '16px 20px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ShieldAlert size={18} color="var(--color-primary-light)" />
          <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>Severity Distribution:</span>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => setSelectedSeverity('ALL')}
            className={`btn btn-sm ${selectedSeverity === 'ALL' ? 'btn-primary' : 'btn-secondary'}`}
          >
            All ({findings.length})
          </button>
          <button
            onClick={() => setSelectedSeverity('CRITICAL')}
            className={`btn btn-sm ${selectedSeverity === 'CRITICAL' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ color: severityCounts.CRITICAL > 0 ? 'var(--color-danger)' : 'var(--text-muted)' }}
          >
            Critical ({severityCounts.CRITICAL})
          </button>
          <button
            onClick={() => setSelectedSeverity('HIGH')}
            className={`btn btn-sm ${selectedSeverity === 'HIGH' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ color: severityCounts.HIGH > 0 ? 'var(--color-danger)' : 'var(--text-muted)' }}
          >
            High ({severityCounts.HIGH})
          </button>
          <button
            onClick={() => setSelectedSeverity('MEDIUM')}
            className={`btn btn-sm ${selectedSeverity === 'MEDIUM' ? 'btn-primary' : 'btn-secondary'}`}
            style={{ color: severityCounts.MEDIUM > 0 ? 'var(--color-warning)' : 'var(--text-muted)' }}
          >
            Medium ({severityCounts.MEDIUM})
          </button>
        </div>
      </div>

      {/* Findings List */}
      {loading ? (
        <LoadingSkeleton count={4} height="120px" />
      ) : filteredFindings.length > 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {filteredFindings.map((f) => {
            const isExpanded = expandedId === f.id;
            return (
              <div
                key={f.id}
                className="card"
                style={{
                  borderLeft: `4px solid ${
                    f.severity === 'CRITICAL' || f.severity === 'HIGH'
                      ? 'var(--color-danger)'
                      : f.severity === 'MEDIUM'
                      ? 'var(--color-warning)'
                      : 'var(--color-primary)'
                  }`,
                }}
              >
                <div
                  onClick={() => setExpandedId(isExpanded ? null : f.id)}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    justifyContent: 'space-between',
                    cursor: 'pointer',
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                      <span className={`badge ${getSeverityBadgeClass(f.severity)}`}>
                        {f.severity}
                      </span>
                      <span className="badge badge-neutral">{f.finding_type}</span>
                      {f.confidence_score && (
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          Confidence: {(f.confidence_score * 100).toFixed(0)}%
                        </span>
                      )}
                    </div>
                    <h3 style={{ fontSize: '1.05rem', color: '#ffffff', marginBottom: '6px' }}>
                      {f.title}
                    </h3>
                    <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                      {f.description}
                    </p>
                  </div>
                  <button className="btn btn-ghost btn-sm" style={{ flexShrink: 0 }}>
                    {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                  </button>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div
                    style={{
                      marginTop: '16px',
                      paddingTop: '14px',
                      borderTop: '1px solid var(--border-subtle)',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '10px',
                    }}
                  >
                    <div>
                      <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                        Business Impact:
                      </span>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-main)', marginTop: '2px' }}>
                        {f.business_impact}
                      </p>
                    </div>

                    {f.evidence_data && Object.keys(f.evidence_data).length > 0 && (
                      <div>
                        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                          Evidence Data Snapshot:
                        </span>
                        <pre
                          style={{
                            marginTop: '4px',
                            padding: '10px',
                            backgroundColor: 'var(--bg-app)',
                            borderRadius: 'var(--radius-sm)',
                            fontSize: '0.75rem',
                            color: 'var(--text-secondary)',
                            overflowX: 'auto',
                            fontFamily: 'var(--font-mono)',
                          }}
                        >
                          {JSON.stringify(f.evidence_data, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <EmptyState
          title="No Findings in this Category"
          description="All evaluated diagnostic rules in this severity tier passed without anomalous triggers."
          icon={AlertTriangle}
        />
      )}
    </div>
  );
};
