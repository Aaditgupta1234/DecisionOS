import React, { useState } from 'react';
import { useDataset } from '../../context/DatasetContext';
import { Database, Upload, RefreshCw, ChevronDown, Check, AlertCircle } from 'lucide-react';
import { DecisionApi } from '../../api';

export const TopNav: React.FC = () => {
  const { datasets, activeDataset, setActiveDataset, refreshDatasets } = useDataset();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setIsUploading(true);
      setUploadError(null);
      const newDataset = await DecisionApi.uploadDataset(file);
      await refreshDatasets();
      if (newDataset) {
        setActiveDataset(newDataset);
      }
    } catch (err: any) {
      console.error('Upload failed:', err);
      setUploadError(err?.message || 'Failed to upload CSV file.');
    } finally {
      setIsUploading(false);
      e.target.value = '';
    }
  };

  return (
    <header
      style={{
        height: 'var(--header-height)',
        backgroundColor: 'var(--bg-app)',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 32px',
        position: 'sticky',
        top: 0,
        zIndex: 50,
      }}
    >
      {/* Left: Active Dataset Selector */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', position: 'relative' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Database size={16} color="var(--text-muted)" />
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Active Dataset:
          </span>
        </div>

        {datasets.length > 0 ? (
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="btn btn-secondary"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '6px 14px',
                fontSize: '0.875rem',
                fontWeight: 600,
              }}
            >
              <span style={{ color: 'var(--color-primary-light)' }}>
                {activeDataset ? activeDataset.name : 'Select Dataset'}
              </span>
              <ChevronDown size={14} />
            </button>

            {isDropdownOpen && (
              <div
                style={{
                  position: 'absolute',
                  top: '100%',
                  left: 0,
                  marginTop: '6px',
                  width: '280px',
                  backgroundColor: 'var(--bg-surface-elevated)',
                  border: '1px solid var(--border-default)',
                  borderRadius: 'var(--radius-md)',
                  boxShadow: 'var(--shadow-lg)',
                  padding: '6px',
                  zIndex: 100,
                }}
              >
                <div style={{ maxHeight: '240px', overflowY: 'auto' }}>
                  {datasets.map((ds) => {
                    const isSelected = activeDataset?.id === ds.id;
                    return (
                      <div
                        key={ds.id}
                        onClick={() => {
                          setActiveDataset(ds);
                          setIsDropdownOpen(false);
                        }}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '8px 12px',
                          borderRadius: 'var(--radius-sm)',
                          cursor: 'pointer',
                          backgroundColor: isSelected ? 'var(--color-primary-subtle)' : 'transparent',
                          color: isSelected ? 'var(--color-primary-light)' : 'var(--text-main)',
                          fontSize: '0.875rem',
                        }}
                      >
                        <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          <div style={{ fontWeight: isSelected ? 600 : 400 }}>{ds.name}</div>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                            {ds.original_filename}
                          </div>
                        </div>
                        {isSelected && <Check size={16} color="var(--color-primary-light)" />}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        ) : (
          <span style={{ fontSize: '0.85rem', color: 'var(--color-warning)' }}>No datasets uploaded yet</span>
        )}

        {uploadError && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--color-danger)', fontSize: '0.8rem' }}>
            <AlertCircle size={14} />
            <span>{uploadError}</span>
          </div>
        )}
      </div>

      {/* Right Actions: Upload & Refresh */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <label
          className="btn btn-secondary btn-sm"
          style={{ cursor: isUploading ? 'not-allowed' : 'pointer' }}
        >
          <Upload size={14} />
          <span>{isUploading ? 'Uploading...' : 'Upload CSV'}</span>
          <input
            type="file"
            accept=".csv"
            onChange={handleFileUpload}
            disabled={isUploading}
            style={{ display: 'none' }}
          />
        </label>

        <button
          onClick={() => refreshDatasets()}
          className="btn btn-ghost btn-sm"
          title="Refresh Datasets"
        >
          <RefreshCw size={14} />
        </button>
      </div>
    </header>
  );
};
