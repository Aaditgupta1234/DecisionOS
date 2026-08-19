import React, { useState } from 'react';
import { useDataset } from '../../context/DatasetContext';
import { useAuth } from '../../features/auth/AuthContext';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { Database, Upload, RefreshCw, ChevronDown, Check, AlertCircle, LogOut, User, Activity, Plus, Search } from 'lucide-react';
import { DecisionApi } from '../../api';
import { Link } from 'react-router-dom';
import { ExecutiveNotificationPopover } from '../workspace/ExecutiveNotificationPopover';
import { GlobalSearchModal } from '../workspace/GlobalSearchModal';

export const TopNav: React.FC = () => {
  const { datasets, activeDataset, setActiveDataset, refreshDatasets } = useDataset();
  const { user, logout } = useAuth();
  const { status: healthStatus, latencyMs } = useBackendHealth();

  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
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
        padding: '0 24px',
        position: 'sticky',
        top: 0,
        zIndex: 50,
      }}
    >
      {/* Left: Global Dataset-Centric Selector */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', position: 'relative' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Database size={15} color="#94A3B8" />
          <span style={{ fontSize: '0.78rem', color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
            Current Dataset:
          </span>
        </div>

        {datasets.length > 0 ? (
          <div style={{ position: 'relative' }}>
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '6px 14px',
                fontSize: '0.85rem',
                fontWeight: 700,
                background: 'rgba(15, 23, 42, 0.8)',
                border: '1px solid #1E293B',
                borderRadius: '6px',
                color: '#FFFFFF',
                cursor: 'pointer',
              }}
            >
              <span style={{ color: '#38BDF8' }}>
                {activeDataset ? activeDataset.name : 'Select Dataset'}
              </span>
              <ChevronDown size={14} color="#94A3B8" />
            </button>

            {isDropdownOpen && (
              <div
                style={{
                  position: 'absolute',
                  top: '100%',
                  left: 0,
                  marginTop: '6px',
                  width: '300px',
                  backgroundColor: '#090D14',
                  border: '1px solid #1E293B',
                  borderRadius: '8px',
                  boxShadow: '0 20px 40px rgba(0,0,0,0.85)',
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
                          borderRadius: '6px',
                          cursor: 'pointer',
                          backgroundColor: isSelected ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
                          color: isSelected ? '#38BDF8' : '#F1F5F9',
                          fontSize: '0.82rem',
                          marginBottom: '2px',
                        }}
                      >
                        <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          <div style={{ fontWeight: isSelected ? 700 : 500 }}>{ds.name}</div>
                          <div style={{ fontSize: '0.7rem', color: '#64748B' }}>
                            {ds.row_count ? `${ds.row_count.toLocaleString()} rows` : ds.original_filename || 'Uploaded CSV'}
                          </div>
                        </div>
                        {isSelected && <Check size={14} color="#38BDF8" />}
                      </div>
                    );
                  })}
                </div>

                <div style={{ borderTop: '1px solid #141A24', marginTop: '6px', paddingTop: '6px' }}>
                  <Link
                    to="/datasets"
                    onClick={() => setIsDropdownOpen(false)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      padding: '6px 10px',
                      fontSize: '11.5px',
                      color: '#94A3B8',
                      textDecoration: 'none',
                      borderRadius: '4px',
                    }}
                  >
                    <Plus size={13} color="#38BDF8" />
                    <span>Upload or Manage Datasets...</span>
                  </Link>
                </div>
              </div>
            )}
          </div>
        ) : (
          <Link
            to="/datasets"
            style={{
              fontSize: '0.8rem',
              color: '#F59E0B',
              textDecoration: 'none',
              background: 'rgba(245, 158, 11, 0.1)',
              padding: '4px 10px',
              borderRadius: '5px',
              border: '1px solid rgba(245, 158, 11, 0.25)',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '5px',
            }}
          >
            <span>No datasets active</span>
            <span style={{ color: '#38BDF8', fontWeight: 600 }}>— Upload CSV</span>
          </Link>
        )}

        {uploadError && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#EF4444', fontSize: '0.8rem' }}>
            <AlertCircle size={14} />
            <span>{uploadError}</span>
          </div>
        )}
      </div>

      {/* Right Controls: Universal Search, Notifications, Backend Status, Upload, Refresh, User Profile */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {/* Cmd+K Universal Search Button */}
        <button
          onClick={() => setIsSearchOpen(true)}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            background: 'rgba(15, 23, 42, 0.8)',
            border: '1px solid #1E293B',
            borderRadius: '6px',
            padding: '5px 10px',
            color: '#94A3B8',
            fontSize: '12px',
            cursor: 'pointer',
          }}
          title="Universal Search (Cmd+K)"
        >
          <Search size={13} color="#38BDF8" />
          <span>Search...</span>
          <kbd style={{ background: '#1E293B', color: '#64748B', padding: '1px 5px', borderRadius: '3px', fontSize: '9px', fontWeight: 800 }}>⌘K</kbd>
        </button>

        {/* Actionable Notification Popover */}
        <ExecutiveNotificationPopover />

        {/* Global Search Modal */}
        <GlobalSearchModal isOpen={isSearchOpen} onClose={() => setIsSearchOpen(false)} />
        {/* Backend Heartbeat Pill */}
        <div
          title={healthStatus === 'connected' ? `FastAPI Gateway Connected (${latencyMs || '<10'}ms)` : 'Backend Gateway Offline on port 8000'}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: healthStatus === 'connected' ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)',
            border: `1px solid ${healthStatus === 'connected' ? 'rgba(16, 185, 129, 0.25)' : 'rgba(239, 68, 68, 0.3)'}`,
            padding: '4px 10px',
            borderRadius: '20px',
            fontSize: '11px',
            fontWeight: 600,
            color: healthStatus === 'connected' ? '#10B981' : '#EF4444',
          }}
        >
          <Activity size={12} />
          <span>{healthStatus === 'connected' ? 'Connected' : 'Offline'}</span>
        </div>

        {/* Upload Quick Button */}
        <label
          className="btn btn-secondary btn-sm"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: '#0F172A',
            border: '1px solid #1E293B',
            color: '#FFFFFF',
            padding: '5px 12px',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: 600,
            cursor: isUploading ? 'not-allowed' : 'pointer',
          }}
        >
          <Upload size={13} />
          <span>{isUploading ? 'Uploading...' : 'Upload CSV'}</span>
          <input
            type="file"
            accept=".csv"
            onChange={handleFileUpload}
            disabled={isUploading}
            style={{ display: 'none' }}
          />
        </label>

        {/* Refresh Cache */}
        <button
          onClick={() => refreshDatasets()}
          style={{
            background: 'transparent',
            border: '1px solid #1E293B',
            color: '#94A3B8',
            borderRadius: '6px',
            padding: '6px 8px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          title="Refresh Active Data"
        >
          <RefreshCw size={13} />
        </button>

        {/* User Profile & Logout */}
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              padding: '4px',
            }}
          >
            <div style={{
              width: '28px',
              height: '28px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #1D4ED8, #0284C7)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#FFFFFF',
              fontSize: '12px',
              fontWeight: 700,
            }}>
              {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'E'}
            </div>
            <div style={{ textAlign: 'left', display: 'flex', flexDirection: 'column' }}>
              <span style={{ fontSize: '12px', fontWeight: 700, color: '#FFFFFF', lineHeight: 1.1 }}>
                {user?.full_name || 'Executive'}
              </span>
              <span style={{ fontSize: '10px', color: '#64748B' }}>
                {user?.role || 'Admin'}
              </span>
            </div>
            <ChevronDown size={12} color="#64748B" />
          </button>

          {isUserMenuOpen && (
            <div style={{
              position: 'absolute',
              top: '100%',
              right: 0,
              marginTop: '8px',
              width: '200px',
              background: '#090D14',
              border: '1px solid #1E293B',
              borderRadius: '8px',
              boxShadow: '0 20px 40px rgba(0,0,0,0.9)',
              padding: '6px',
              zIndex: 100,
            }}>
              <div style={{ padding: '8px 10px', borderBottom: '1px solid #141A24', fontSize: '11px', color: '#64748B' }}>
                Signed in as <span style={{ color: '#F1F5F9', fontWeight: 600 }}>{user?.email || 'executive@decisionos.ai'}</span>
              </div>
              <button
                onClick={() => {
                  logout();
                  setIsUserMenuOpen(false);
                }}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 10px',
                  background: 'transparent',
                  border: 'none',
                  color: '#EF4444',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  borderRadius: '4px',
                  textAlign: 'left',
                }}
              >
                <LogOut size={13} />
                <span>Sign Out</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
