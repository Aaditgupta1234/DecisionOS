import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { queryKeys } from '../../shared/api/queryKeys';
import { Dataset } from '../../types';
import {
  Upload,
  Database,
  Trash2,
  CheckCircle2,
  Clock,
  AlertCircle,
  FileSpreadsheet,
  ArrowRight,
  RefreshCw,
  Eye,
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

export const DatasetsView: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { activeDataset, setActiveDataset, refreshDatasets } = useDataset();

  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Fetch datasets with React Query
  const { data: datasets = [], isLoading, refetch } = useQuery<Dataset[]>({
    queryKey: queryKeys.datasets.all(),
    queryFn: async () => {
      const res = await DecisionApi.listDatasets();
      return Array.isArray(res) ? res : [];
    },
  });

  const handleUploadFile = async (file: File) => {
    if (!file.name.endsWith('.csv')) {
      setErrorMsg('Please select a valid .csv file.');
      return;
    }

    try {
      setUploading(true);
      setErrorMsg(null);
      setUploadProgress(25);

      const interval = setInterval(() => {
        setUploadProgress(prev => (prev < 90 ? prev + 15 : prev));
      }, 150);

      const created = await DecisionApi.uploadDataset(file);
      clearInterval(interval);
      setUploadProgress(100);

      await queryClient.invalidateQueries({ queryKey: queryKeys.datasets.all() });
      await refreshDatasets();

      if (created) {
        setActiveDataset(created);
        // Direct to Schema Mapping Review
        navigate(`/datasets/${created.id}/mapping`);
      }
    } catch (err: any) {
      console.error('Upload error:', err);
      setErrorMsg(err?.message || 'Failed to upload CSV dataset.');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleUploadFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <div style={{ padding: '28px 32px', color: '#FFFFFF', maxWidth: '1400px', margin: '0 auto' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '10.5px', fontWeight: 700, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.12)', border: '1px solid rgba(56, 189, 248, 0.28)', padding: '1px 7px', borderRadius: '4px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Data Gateway
            </span>
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, letterSpacing: '-0.02em' }}>
            Dataset Management & Ingestion
          </h1>
          <p style={{ fontSize: '13px', color: '#94A3B8', marginTop: '4px' }}>
            Upload and inspect structured transactional datasets to fuel the DecisionOS intelligence core.
          </p>
        </div>

        <button
          onClick={() => refetch()}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: '#0F172A',
            border: '1px solid #1E293B',
            color: '#CBD5E1',
            padding: '7px 14px',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          <RefreshCw size={13} />
          <span>Refresh List</span>
        </button>
      </div>

      {/* Error Alert */}
      {errorMsg && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.12)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '8px',
          padding: '10px 16px',
          marginBottom: '20px',
          color: '#F87171',
          fontSize: '12.5px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
        }}>
          <AlertCircle size={15} />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* CSV Drag & Drop Upload Zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
        style={{
          background: dragActive ? 'rgba(56, 189, 248, 0.06)' : '#080B10',
          border: `2px dashed ${dragActive ? '#38BDF8' : '#1E293B'}`,
          borderRadius: '12px',
          padding: '36px 24px',
          textAlign: 'center',
          marginBottom: '32px',
          transition: 'all 0.15s ease',
          position: 'relative',
        }}
      >
        <div style={{
          width: '52px',
          height: '52px',
          borderRadius: '50%',
          background: 'rgba(56, 189, 248, 0.1)',
          border: '1px solid rgba(56, 189, 248, 0.25)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 16px',
        }}>
          <Upload size={24} color="#38BDF8" />
        </div>

        <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '6px' }}>
          Drag & Drop your CSV Dataset here
        </h3>
        <p style={{ fontSize: '12.5px', color: '#64748B', maxWidth: '420px', margin: '0 auto 16px' }}>
          Supports comma-separated E-Commerce, Retail, SaaS, or Logistics transactional data with headers.
        </p>

        <label
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            background: '#1D4ED8',
            border: '1px solid #3B82F6',
            color: '#FFFFFF',
            padding: '8px 20px',
            borderRadius: '6px',
            fontSize: '12.5px',
            fontWeight: 700,
            cursor: uploading ? 'not-allowed' : 'pointer',
          }}
        >
          <span>{uploading ? `Uploading (${uploadProgress}%)...` : 'Browse Local CSV'}</span>
          <input
            type="file"
            accept=".csv"
            disabled={uploading}
            onChange={(e) => {
              if (e.target.files?.[0]) handleUploadFile(e.target.files[0]);
            }}
            style={{ display: 'none' }}
          />
        </label>

        {uploading && (
          <div style={{ maxWidth: '300px', margin: '16px auto 0' }}>
            <div style={{ width: '100%', height: '4px', background: '#1E293B', borderRadius: '2px', overflow: 'hidden' }}>
              <div style={{ width: `${uploadProgress}%`, height: '100%', background: '#38BDF8', transition: 'width 0.2s ease' }} />
            </div>
          </div>
        )}
      </div>

      {/* Dataset Registry Table */}
      <div style={{ background: '#090C12', border: '1px solid #1A2230', borderRadius: '12px', overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #141A24', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Database size={16} color="#38BDF8" />
            <span style={{ fontSize: '13px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Registered Datasets ({datasets.length})
            </span>
          </div>
        </div>

        {isLoading ? (
          <div style={{ padding: '32px', textAlign: 'center', color: '#64748B', fontSize: '13px' }}>
            Loading dataset registry from backend...
          </div>
        ) : datasets.length === 0 ? (
          <div style={{ padding: '48px 24px', textAlign: 'center', color: '#94A3B8' }}>
            <FileSpreadsheet size={32} color="#334155" style={{ margin: '0 auto 12px' }} />
            <div style={{ fontSize: '14px', fontWeight: 600, color: '#CBD5E1', marginBottom: '4px' }}>No Datasets Uploaded</div>
            <div style={{ fontSize: '12px', color: '#64748B' }}>Upload a CSV above to begin analysis.</div>
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #141A24', color: '#64748B', textAlign: 'left', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                <th style={{ padding: '12px 20px' }}>Dataset Name</th>
                <th style={{ padding: '12px 16px' }}>Status</th>
                <th style={{ padding: '12px 16px' }}>Rows</th>
                <th style={{ padding: '12px 16px' }}>Uploaded</th>
                <th style={{ padding: '12px 20px', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {datasets.map((ds) => {
                const isActive = activeDataset?.id === ds.id;
                const isReady = ds.status === 'READY';

                return (
                  <tr
                    key={ds.id}
                    style={{
                      borderBottom: '1px solid #111620',
                      background: isActive ? 'rgba(56, 189, 248, 0.03)' : 'transparent',
                    }}
                  >
                    <td style={{ padding: '14px 20px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <div style={{
                          width: '32px',
                          height: '32px',
                          borderRadius: '6px',
                          background: isActive ? 'rgba(56, 189, 248, 0.15)' : '#111622',
                          border: `1px solid ${isActive ? 'rgba(56, 189, 248, 0.35)' : '#1E2738'}`,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: isActive ? '#38BDF8' : '#94A3B8',
                        }}>
                          <FileSpreadsheet size={16} />
                        </div>
                        <div>
                          <div style={{ fontWeight: 700, color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <span>{ds.name}</span>
                            {isActive && (
                              <span style={{ fontSize: '9px', fontWeight: 700, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.15)', padding: '1px 5px', borderRadius: '3px' }}>
                                Active
                              </span>
                            )}
                          </div>
                          <div style={{ fontSize: '11px', color: '#64748B' }}>{ds.original_filename || ds.id}</div>
                        </div>
                      </div>
                    </td>

                    <td style={{ padding: '14px 16px' }}>
                      <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '5px',
                        fontSize: '11px',
                        fontWeight: 700,
                        color: isReady ? '#10B981' : ds.status === 'FAILED' ? '#EF4444' : '#F59E0B',
                        background: isReady ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                        padding: '2px 8px',
                        borderRadius: '4px',
                      }}>
                        {isReady ? <CheckCircle2 size={12} /> : <Clock size={12} />}
                        <span>{ds.status || 'READY'}</span>
                      </span>
                    </td>

                    <td style={{ padding: '14px 16px', color: '#94A3B8', fontWeight: 600 }}>
                      {ds.row_count ? ds.row_count.toLocaleString() : '—'}
                    </td>

                    <td style={{ padding: '14px 16px', color: '#64748B', fontSize: '12px' }}>
                      {ds.created_at ? new Date(ds.created_at).toLocaleDateString() : 'Just now'}
                    </td>

                    <td style={{ padding: '14px 20px', textAlign: 'right' }}>
                      <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                        {!isActive && (
                          <button
                            onClick={() => setActiveDataset(ds)}
                            style={{
                              background: '#111622',
                              border: '1px solid #1F2738',
                              color: '#CBD5E1',
                              padding: '5px 10px',
                              borderRadius: '5px',
                              fontSize: '11.5px',
                              fontWeight: 600,
                              cursor: 'pointer',
                            }}
                          >
                            Set Active
                          </button>
                        )}

                        <Link
                          to={`/datasets/${ds.id}/mapping`}
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '4px',
                            background: '#1D4ED8',
                            border: '1px solid #3B82F6',
                            color: '#FFFFFF',
                            padding: '5px 10px',
                            borderRadius: '5px',
                            fontSize: '11.5px',
                            fontWeight: 700,
                            textDecoration: 'none',
                          }}
                        >
                          <Eye size={12} />
                          <span>Review Schema</span>
                        </Link>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default DatasetsView;
