import React, { useState } from 'react';
import { useDataset } from '../../context/DatasetContext';
import { useAuth } from '../../features/auth/AuthContext';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { useTenantStore } from '../../store/useTenantStore';
import { Database, Upload, RefreshCw, ChevronDown, Bell, Search, Sparkles, Building2, Globe } from 'lucide-react';
import { DecisionApi } from '../../api';
import { TimeTravelControls } from '../../features/shared/TimeTravelControls';

import { Link } from 'react-router-dom';

interface TopNavProps {
  onOpenSearch?: () => void;
  onOpenNotifications?: () => void;
  onOpenOnboarding?: () => void;
}

export const TopNav: React.FC<TopNavProps> = ({
  onOpenSearch,
  onOpenNotifications,
  onOpenOnboarding,
}) => {
  const { datasets, activeDataset, setActiveDataset, refreshDatasets } = useDataset();
  const { user, logout } = useAuth();
  const { status: healthStatus, latencyMs } = useBackendHealth();
  const { activeOrg, activeWorkspace, organizations, workspaces, setActiveOrg, setActiveWorkspace } = useTenantStore();

  const [isOrgDropdownOpen, setIsOrgDropdownOpen] = useState(false);
  const [isDatasetDropdownOpen, setIsDatasetDropdownOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setIsUploading(true);
      const newDataset = await DecisionApi.uploadDataset(file);
      await refreshDatasets();
      if (newDataset) {
        setActiveDataset(newDataset);
      }
    } catch (err: any) {
      console.error('Upload failed:', err);
    } finally {
      setIsUploading(false);
      e.target.value = '';
    }
  };

  return (
    <header
      style={{
        height: 'var(--header-height)',
        backgroundColor: 'rgba(6, 8, 13, 0.95)',
        backdropFilter: 'blur(16px)',
        borderBottom: '1px solid #161A22',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 12px',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        gap: '8px',
        boxSizing: 'border-box',
        width: '100%',
      }}
    >
      {/* Left: Organization & Workspace Switcher + Time Travel */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexShrink: 1, minWidth: 0 }}>
        {/* Back to Marketing Home Link */}
        <Link
          to="/"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '3px',
            padding: '3px 6px',
            background: '#080A0F',
            border: '1px solid #161A22',
            borderRadius: '5px',
            color: '#94A3B8',
            fontSize: '0.68rem',
            fontWeight: 700,
            textDecoration: 'none',
            whiteSpace: 'nowrap',
            flexShrink: 0,
            transition: 'all 0.15s ease',
          }}
        >
          <span>← Overview</span>
        </Link>

        {/* Org Switcher */}
        <div style={{ position: 'relative', flexShrink: 0 }}>
          <button
            onClick={() => setIsOrgDropdownOpen(!isOrgDropdownOpen)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: '3px 6px',
              background: '#080A0F',
              border: '1px solid #161A22',
              borderRadius: '5px',
              color: '#FFFFFF',
              fontSize: '0.70rem',
              fontWeight: 700,
              cursor: 'pointer',
              whiteSpace: 'nowrap',
            }}
          >
            <Building2 size={11} color="#38BDF8" />
            <span style={{ maxWidth: '80px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {activeOrg.name}
            </span>
            <ChevronDown size={10} color="#64748B" />
          </button>

          {isOrgDropdownOpen && (
            <div
              style={{
                position: 'absolute',
                top: '100%',
                left: 0,
                marginTop: '6px',
                width: '260px',
                background: '#080A0F',
                border: '1px solid #161A22',
                borderRadius: '8px',
                padding: '6px',
                zIndex: 100,
                boxShadow: '0 20px 40px rgba(0,0,0,0.85)',
              }}
            >
              <div style={{ fontSize: '0.68rem', color: '#64748B', padding: '6px 8px', fontWeight: 800 }}>
                SELECT TENANT ORGANIZATION
              </div>
              {organizations.map((org) => (
                <div
                  key={org.id}
                  onClick={() => {
                    setActiveOrg(org);
                    setIsOrgDropdownOpen(false);
                  }}
                  style={{
                    padding: '8px 10px',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '0.78rem',
                    color: activeOrg.id === org.id ? '#38BDF8' : '#F1F5F9',
                    background: activeOrg.id === org.id ? 'rgba(56, 189, 248, 0.1)' : 'transparent',
                    fontWeight: 700,
                  }}
                >
                  {org.name}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Universal Dataset Context Switcher */}
        <div style={{ position: 'relative', flexShrink: 0 }}>
          <button
            onClick={() => setIsDatasetDropdownOpen(!isDatasetDropdownOpen)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: '3px 6px',
              background: '#080A0F',
              border: '1px solid #161A22',
              borderRadius: '5px',
              color: '#FFFFFF',
              fontSize: '0.70rem',
              fontWeight: 700,
              cursor: 'pointer',
              whiteSpace: 'nowrap',
            }}
          >
            <Database size={11} color="#10B981" />
            <span style={{ maxWidth: '75px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {activeDataset?.name || 'SaaS Telemetry'}
            </span>
            <ChevronDown size={10} color="#64748B" />
          </button>

          {isDatasetDropdownOpen && (
            <div
              style={{
                position: 'absolute',
                top: '100%',
                left: 0,
                marginTop: '6px',
                width: '280px',
                background: '#080A0F',
                border: '1px solid #161A22',
                borderRadius: '8px',
                padding: '6px',
                zIndex: 100,
                boxShadow: '0 20px 40px rgba(0,0,0,0.85)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '6px 8px' }}>
                <span style={{ fontSize: '0.68rem', color: '#64748B', fontWeight: 800 }}>ACTIVE TELEMETRY DATASET</span>
                <Link
                  to="/enterprise-data"
                  onClick={() => setIsDatasetDropdownOpen(false)}
                  style={{ fontSize: '0.68rem', color: '#38BDF8', fontWeight: 700, textDecoration: 'none' }}
                >
                  + Open Data Hub
                </Link>
              </div>
              {datasets.length === 0 ? (
                <div style={{ padding: '8px 10px', fontSize: '0.76rem', color: '#94A3B8' }}>
                  <span>Default benchmark active.</span>{' '}
                  <Link
                    to="/enterprise-data"
                    onClick={() => setIsDatasetDropdownOpen(false)}
                    style={{ color: '#38BDF8', fontWeight: 700 }}
                  >
                    Upload CSV
                  </Link>
                </div>
              ) : (
                datasets.map((ds) => (
                  <div
                    key={ds.id}
                    onClick={() => {
                      setActiveDataset(ds);
                      setIsDatasetDropdownOpen(false);
                    }}
                    style={{
                      padding: '8px 10px',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '0.78rem',
                      color: activeDataset?.id === ds.id ? '#10B981' : '#F1F5F9',
                      background: activeDataset?.id === ds.id ? 'rgba(16, 185, 129, 0.1)' : 'transparent',
                      fontWeight: 700,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                    }}
                  >
                    <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{ds.name}</span>
                    {activeDataset?.id === ds.id && <span style={{ fontSize: '0.65rem', color: '#10B981' }}>ACTIVE</span>}
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        {/* Time Travel Controls */}
        <TimeTravelControls />
      </div>

      {/* Right Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexShrink: 0 }}>
        {/* Onboarding Wizard Trigger */}
        <button
          onClick={onOpenOnboarding}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            padding: '3px 7px',
            background: 'rgba(168, 85, 247, 0.1)',
            border: '1px solid rgba(168, 85, 247, 0.3)',
            borderRadius: '5px',
            color: '#C084FC',
            fontSize: '0.68rem',
            fontWeight: 700,
            cursor: 'pointer',
            whiteSpace: 'nowrap',
            flexShrink: 0,
          }}
        >
          <Sparkles size={11} />
          <span>Setup Wizard</span>
        </button>

        {/* Notifications Drawer Trigger */}
        <button
          onClick={onOpenNotifications}
          style={{
            background: '#080A0F',
            border: '1px solid #161A22',
            borderRadius: '5px',
            padding: '4px 6px',
            color: '#F59E0B',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative',
            flexShrink: 0,
          }}
          title="Audit & System Notifications"
        >
          <Bell size={12} />
          <div
            style={{
              position: 'absolute',
              top: '3px',
              right: '3px',
              width: '5px',
              height: '5px',
              borderRadius: '50%',
              background: '#EF4444',
            }}
          />
        </button>

        {/* User / Profile Menu */}
        <div style={{ position: 'relative', flexShrink: 0 }}>
          <button
            onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              padding: '2px 6px',
              background: '#080A0F',
              border: '1px solid #161A22',
              borderRadius: '5px',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
              flexShrink: 0,
            }}
          >
            <div
              style={{
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #1D4ED8, #0284C7)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#FFFFFF',
                fontSize: '9.5px',
                fontWeight: 800,
                flexShrink: 0,
              }}
            >
              {user?.full_name ? user.full_name.charAt(0).toUpperCase() : user?.email ? user.email.charAt(0).toUpperCase() : 'E'}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', textAlign: 'left', minWidth: 0 }}>
              <span style={{ fontSize: '0.70rem', fontWeight: 700, color: '#FFFFFF', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '85px' }}>
                {user?.full_name || (user?.email ? user.email.split('@')[0] : 'Executive Admin')}
              </span>
              <span style={{ fontSize: '0.56rem', color: '#64748B', lineHeight: 1 }}>
                {user?.role || 'admin'}
              </span>
            </div>
            <ChevronDown size={9} color="#64748B" />
          </button>

          {isUserMenuOpen && (
            <div
              style={{
                position: 'absolute',
                top: '100%',
                right: 0,
                marginTop: '8px',
                width: '200px',
                background: '#080A0F',
                border: '1px solid #14171E',
                borderRadius: '8px',
                padding: '6px',
                zIndex: 100,
                boxShadow: '0 20px 40px rgba(0,0,0,0.9)',
              }}
            >
              <div style={{ padding: '8px 10px', borderBottom: '1px solid #141A24' }}>
                <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#FFFFFF' }}>
                  {user?.full_name || 'Executive User'}
                </div>
                <div style={{ fontSize: '0.68rem', color: '#64748B', marginTop: '2px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {user?.email || 'executive@decisionos.ai'}
                </div>
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
                  gap: '6px',
                  padding: '8px 10px',
                  background: 'transparent',
                  border: 'none',
                  color: '#EF4444',
                  fontSize: '0.76rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  borderRadius: '4px',
                  textAlign: 'left',
                  marginTop: '4px',
                }}
              >
                Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
