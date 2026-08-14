import React, { useEffect, useState } from 'react';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { RootCause } from '../../types';
import { LoadingSkeleton } from '../../components/feedback/LoadingSkeleton';
import { ErrorBanner } from '../../components/feedback/ErrorBanner';
import { EmptyState } from '../../components/feedback/EmptyState';
import { GitMerge, Sparkles, Layers } from 'lucide-react';

export const RootCausesView: React.FC = () => {
  const { activeDataset } = useDataset();
  const [rootCauses, setRootCauses] = useState<RootCause[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRootCauses = async (datasetId: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await DecisionApi.listRootCauses(datasetId);
      setRootCauses(Array.isArray(data) ? data : []);
    } catch (err: any) {
      console.error('Failed to load root causes:', err);
      setError(err?.message || 'Could not fetch root cause analyses for this dataset.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeDataset?.id) {
      fetchRootCauses(activeDataset.id);
    } else {
      setLoading(false);
    }
  }, [activeDataset?.id]);

  if (!activeDataset) {
    return (
      <div className="page-container">
        <EmptyState
          title="No Active Dataset Selected"
          description="Select a dataset to view its root cause discovery."
          icon={GitMerge}
        />
      </div>
    );
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
          <span className="badge badge-primary">Phase 5.6 Root Cause Discovery</span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Causal DAG & Driver Synthesis
          </span>
        </div>
        <h1>Root Cause Analysis</h1>
        <p style={{ marginTop: '4px', fontSize: '0.9rem' }}>
          Deterministic causal reasoning tracing symptom findings back to their systemic business drivers.
        </p>
      </div>

      {/* Phase 7.1 Interactive Graph Preview Banner */}
      <div
        className="card"
        style={{
          marginBottom: '20px',
          background: 'linear-gradient(135deg, rgba(15, 21, 35, 0.8) 0%, rgba(30, 41, 59, 0.4) 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '14px 20px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Layers size={18} color="var(--color-primary-light)" />
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            <strong>Phase 7.0 Causal List Preview</strong> — Full Interactive Node-Link Graph visualization will be delivered in Phase 7.1.
          </span>
        </div>
        <span className="badge badge-neutral">Phase 7.1 Architecture Ready</span>
      </div>

      {error && <ErrorBanner message={error} onRetry={() => fetchRootCauses(activeDataset.id)} />}

      {/* Root Causes List */}
      {loading ? (
        <LoadingSkeleton count={3} height="130px" />
      ) : rootCauses.length > 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {rootCauses.map((rc, idx) => (
            <div key={rc.id} className="card-elevated" style={{ position: 'relative' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '10px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                    <span className="badge badge-warning">Causal Driver #{idx + 1}</span>
                    <span className="badge badge-neutral">{rc.category}</span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      Key: {rc.root_cause_key}
                    </span>
                  </div>
                  <h3 style={{ fontSize: '1.15rem', color: '#ffffff', marginBottom: '8px' }}>
                    {rc.title}
                  </h3>
                </div>

                {/* Probability & Confidence Chips */}
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Probability Score:{' '}
                    <strong style={{ color: 'var(--color-primary-light)' }}>
                      {(rc.probability_score * 100).toFixed(0)}%
                    </strong>
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Confidence:{' '}
                    <strong style={{ color: 'var(--color-success)' }}>
                      {(rc.confidence_score * 100).toFixed(0)}%
                    </strong>
                  </div>
                </div>
              </div>

              {rc.supporting_evidence && (
                <div
                  style={{
                    backgroundColor: 'var(--bg-app)',
                    padding: '12px 14px',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.85rem',
                    color: 'var(--text-secondary)',
                    lineHeight: 1.5,
                    marginBottom: '12px',
                  }}
                >
                  <strong style={{ color: 'var(--text-muted)' }}>Evidence & Explanation: </strong>
                  {rc.supporting_evidence}
                </div>
              )}

              {rc.affected_finding_ids && rc.affected_finding_ids.length > 0 && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.75rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Linked Finding Symptoms:</span>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                    {rc.affected_finding_ids.map((fid) => (
                      <span key={fid} className="badge badge-neutral" style={{ fontSize: '0.65rem' }}>
                        {fid}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <EmptyState
          title="No Root Causes Identified"
          description="Diagnostic findings on this dataset did not meet the causal threshold for systemic root causes."
          icon={GitMerge}
        />
      )}
    </div>
  );
};
