import React, { useState } from 'react';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { Upload, Database, Check, Play, FileText } from 'lucide-react';
import { ErrorBanner } from '../../components/feedback/ErrorBanner';

export const DatasetsView: React.FC = () => {
  const { datasets, activeDataset, setActiveDataset, refreshDatasets } = useDataset();
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [isProcessing, setIsProcessing] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setIsUploading(true);
      setError(null);
      setSuccessMsg(null);
      const newDataset = await DecisionApi.uploadDataset(file);
      await refreshDatasets();
      if (newDataset) {
        setActiveDataset(newDataset);
        setSuccessMsg(`Dataset "${newDataset.name}" uploaded successfully!`);
      }
    } catch (err: any) {
      console.error('Upload failed:', err);
      setError(err?.message || 'Failed to upload CSV dataset.');
    } finally {
      setIsUploading(false);
      e.target.value = '';
    }
  };

  const handleRunPipeline = async (datasetId: string) => {
    try {
      setIsProcessing(datasetId);
      setError(null);
      setSuccessMsg(null);
      await DecisionApi.generateIntelligence(datasetId);
      setSuccessMsg('Pipeline executed successfully! Intelligence artifacts updated.');
    } catch (err: any) {
      console.error('Pipeline execution failed:', err);
      setError(err?.message || 'Failed to run intelligence pipeline.');
    } finally {
      setIsProcessing(null);
    }
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <span className="badge badge-primary">Phase 3 Dataset Management</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Schema Inference & Pipeline Ingestion
            </span>
          </div>
          <h1>Dataset Management</h1>
          <p style={{ marginTop: '4px', fontSize: '0.9rem' }}>
            Manage uploaded CSV datasets, switch active analytical context, and trigger intelligence synthesis.
          </p>
        </div>

        <label className="btn btn-primary" style={{ cursor: isUploading ? 'not-allowed' : 'pointer' }}>
          <Upload size={16} />
          <span>{isUploading ? 'Uploading...' : 'Upload New CSV'}</span>
          <input
            type="file"
            accept=".csv"
            onChange={handleFileUpload}
            disabled={isUploading}
            style={{ display: 'none' }}
          />
        </label>
      </div>

      {error && <ErrorBanner message={error} />}

      {successMsg && (
        <div
          style={{
            padding: '12px 16px',
            backgroundColor: 'var(--color-success-subtle)',
            border: '1px solid var(--color-success-border)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--color-success)',
            marginBottom: '20px',
            fontSize: '0.875rem',
            fontWeight: 500,
          }}
        >
          ✓ {successMsg}
        </div>
      )}

      {/* Datasets Table */}
      <div className="card-elevated" style={{ padding: 0, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
          <thead>
            <tr style={{ backgroundColor: 'var(--bg-app)', borderBottom: '1px solid var(--border-default)', textAlign: 'left', color: 'var(--text-muted)' }}>
              <th style={{ padding: '14px 20px' }}>DATASET NAME</th>
              <th style={{ padding: '14px 20px' }}>FILE</th>
              <th style={{ padding: '14px 20px' }}>STATUS</th>
              <th style={{ padding: '14px 20px' }}>CREATED AT</th>
              <th style={{ padding: '14px 20px', textAlign: 'right' }}>ACTIONS</th>
            </tr>
          </thead>
          <tbody>
            {datasets.map((ds) => {
              const isActive = activeDataset?.id === ds.id;
              return (
                <tr
                  key={ds.id}
                  style={{
                    borderBottom: '1px solid var(--border-subtle)',
                    backgroundColor: isActive ? 'var(--color-primary-subtle)' : 'transparent',
                  }}
                >
                  <td style={{ padding: '14px 20px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <Database size={18} color={isActive ? 'var(--color-primary-light)' : 'var(--text-muted)'} />
                      <div>
                        <div style={{ fontWeight: 600, color: isActive ? '#ffffff' : 'var(--text-main)' }}>
                          {ds.name}
                        </div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>ID: {ds.id}</div>
                      </div>
                    </div>
                  </td>

                  <td style={{ padding: '14px 20px', color: 'var(--text-secondary)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <FileText size={14} />
                      <span>{ds.original_filename}</span>
                    </div>
                  </td>

                  <td style={{ padding: '14px 20px' }}>
                    <span className="badge badge-success">{ds.status}</span>
                  </td>

                  <td style={{ padding: '14px 20px', color: 'var(--text-muted)' }}>
                    {new Date(ds.created_at).toLocaleDateString()}
                  </td>

                  <td style={{ padding: '14px 20px', textAlign: 'right' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '8px' }}>
                      {!isActive && (
                        <button
                          onClick={() => setActiveDataset(ds)}
                          className="btn btn-secondary btn-sm"
                        >
                          Set Active
                        </button>
                      )}

                      <button
                        onClick={() => handleRunPipeline(ds.id)}
                        disabled={isProcessing === ds.id}
                        className="btn btn-primary btn-sm"
                        title="Run deterministic pipeline & calculate intelligence"
                      >
                        <Play size={12} />
                        <span>{isProcessing === ds.id ? 'Processing...' : 'Run Pipeline'}</span>
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
