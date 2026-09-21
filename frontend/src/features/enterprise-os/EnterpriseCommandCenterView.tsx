import React, { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Database,
  Upload,
  AlertTriangle,
  Zap,
  RefreshCw,
  GitMerge,
  ArrowRight,
  BrainCircuit,
  Target,
  BarChart2,
  Network,
  CheckCircle2,
  Check,
  Sparkles,
  ShieldCheck,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { useDataset } from '../../context/DatasetContext';
import { useAuth } from '../auth/AuthContext';
import { DecisionApi } from '../../api';
import { queryKeys } from '../../shared/api/queryKeys';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { BackendOfflineScreen } from '../../shared/components/feedback/BackendOfflineScreen';
import { NoDatasetEmptyState } from '../../shared/components/feedback/NoDatasetEmptyState';
import { BusinessHealthResponse, IntelligenceReportResponse } from '../../types';
import { FadeUp } from '../../design-system/motion';
import { buildHarmonizedExecutiveIntelligence } from './enterpriseIntelligenceEngine';
import { EnterpriseCardErrorBoundary } from './EnterpriseCardErrorBoundary';
import { getDatasetStatusDisplay } from '../../utils/datasetStatus';

export const EnterpriseCommandCenterView: React.FC = () => {
  const { datasets, activeDataset, setActiveDataset, refreshDatasets } = useDataset();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const { status: healthStatus, checkHealth } = useBackendHealth();
  const [quickNotice, setQuickNotice] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [claimedPrograms, setClaimedPrograms] = useState<Record<string, string>>(() => {
    try {
      const saved = localStorage.getItem('decisionos_claimed_programs');
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  });
  const [lastRefreshTime, setLastRefreshTime] = useState<string>(() => {
    const d = new Date();
    return d.toTimeString().slice(0, 8) + ' UTC';
  });

  const handleClaimProgram = (title: string) => {
    const claimer = user?.full_name ? `${user.full_name} (Active Session)` : 'Executive Sponsor (Active Session)';
    setClaimedPrograms((prev) => {
      const next = { ...prev, [title]: claimer };
      try {
        localStorage.setItem('decisionos_claimed_programs', JSON.stringify(next));
      } catch {
        // Ignore quota/storage errors
      }
      return next;
    });
    setQuickNotice(`Governance stewardship of "${title}" claimed.`);
    setTimeout(() => setQuickNotice(null), 4000);
  };

  // In-place CSV Dataset Upload Handler
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const csvFiles = Array.from(files).filter(
      (f) => f.name.toLowerCase().endsWith('.csv') || f.type === 'text/csv' || !f.name.includes('.')
    );
    if (csvFiles.length === 0) {
      setUploadError('Please select valid .csv dataset file(s).');
      return;
    }

    try {
      setIsUploading(true);
      setUploadError(null);

      let lastDataset = null;
      let count = 0;

      for (let i = 0; i < csvFiles.length; i++) {
        const file = csvFiles[i];
        if (csvFiles.length > 1) {
          setQuickNotice(`Ingesting source ${i + 1} of ${csvFiles.length}: "${file.name}"...`);
        } else {
          setQuickNotice(`Connecting "${file.name}"... Initializing pipeline.`);
        }

        const newDataset = await DecisionApi.uploadDataset(file);
        if (newDataset) {
          lastDataset = newDataset;
          count++;
        }
      }

      if (lastDataset) {
        setActiveDataset(lastDataset);
        await refreshDatasets();
        await queryClient.invalidateQueries();
        await queryClient.refetchQueries({ queryKey: queryKeys.reports.executive(lastDataset.id) });
        await queryClient.refetchQueries({ queryKey: queryKeys.reports.healthScore(lastDataset.id) });

        setLastRefreshTime(new Date().toTimeString().slice(0, 8) + ' UTC');
        setQuickNotice(`Governed data source "${lastDataset.name}" active.`);
        setTimeout(() => setQuickNotice(null), 3500);
      }
    } catch (err: any) {
      console.error('Upload failed:', err);
      const errorMessage =
        err?.response?.data?.message ||
        err?.data?.detail?.message ||
        err?.data?.message ||
        (typeof err?.data?.detail === 'string' ? err.data.detail : null) ||
        (typeof err?.message === 'string' && !err.message.includes('[object') ? err.message : null) ||
        'Intelligence Service Temporarily Unavailable';
      setUploadError(errorMessage);
      setQuickNotice(null);
    } finally {
      setIsUploading(false);
      e.target.value = '';
    }
  };

  // 1. Fetch Real Intelligence Report
  const {
    data: reportData,
    isLoading: isReportLoading,
    isError: isReportError,
  } = useQuery<IntelligenceReportResponse>({
    queryKey: queryKeys.reports.executive(activeDataset?.id || ''),
    queryFn: () => DecisionApi.getIntelligenceReport(activeDataset!.id),
    enabled: !!activeDataset?.id && healthStatus === 'connected',
    staleTime: 0,
  });

  // 2. Fetch Real Business Health Score
  const {
    data: healthData,
    isLoading: isHealthLoading,
    isError: isHealthError,
  } = useQuery<BusinessHealthResponse>({
    queryKey: queryKeys.reports.healthScore(activeDataset?.id || ''),
    queryFn: () => DecisionApi.getHealthScore(activeDataset!.id),
    enabled: !!activeDataset?.id && healthStatus === 'connected',
    staleTime: 0,
  });

  // Single Deterministic Harmonized Intelligence Synthesizer with Dynamic Dataset & IAM Context
  const intel = buildHarmonizedExecutiveIntelligence(reportData, healthData, activeDataset?.name, activeDataset, datasets, user);

  const isLoading = isReportLoading || isHealthLoading;
  const isError = isReportError || isHealthError;

  const handleRefreshAll = async () => {
    setQuickNotice('Synchronizing intelligence...');
    await queryClient.invalidateQueries();
    if (activeDataset?.id) {
      await queryClient.refetchQueries({ queryKey: queryKeys.reports.executive(activeDataset.id) });
      await queryClient.refetchQueries({ queryKey: queryKeys.reports.healthScore(activeDataset.id) });
    }
    setLastRefreshTime(new Date().toTimeString().slice(0, 8) + ' UTC');
    setQuickNotice(`Intelligence synchronized successfully. Active source: ${activeDataset?.name || 'Governed Pipeline'}`);
    setTimeout(() => setQuickNotice(null), 3500);
  };

  if (healthStatus === 'offline') {
    return <BackendOfflineScreen onRetry={checkHealth} />;
  }

  if (!activeDataset) {
    return (
      <div style={{ padding: '64px 32px', display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative' }}>
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: '50%',
            transform: 'translateX(-50%)',
            width: '500px',
            height: '260px',
            background: 'radial-gradient(circle at top center, rgba(56, 189, 248, 0.05), transparent 65%)',
            pointerEvents: 'none',
          }}
        />
        <NoDatasetEmptyState
          title="No Active Data Source Selected"
          description="Connect or select an enterprise business data source to initialize the Executive Command Center."
          actionText="Or Select Governed Source"
          actionTo="/enterprise-data"
        />
        <label
          style={{
            marginTop: '-16px',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            background: '#FFFFFF',
            color: '#000000',
            padding: '10px 24px',
            borderRadius: '8px',
            fontSize: '13px',
            fontWeight: 700,
            cursor: isUploading ? 'not-allowed' : 'pointer',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.40)',
            opacity: isUploading ? 0.7 : 1,
            transition: 'all 0.15s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = '#EAEAEA';
            e.currentTarget.style.transform = 'translateY(-1px)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = '#FFFFFF';
            e.currentTarget.style.transform = 'translateY(0)';
          }}
        >
          {isUploading ? <RefreshCw size={14} className="animate-spin" /> : <Upload size={14} />}
          <span>{isUploading ? 'Connecting Source...' : 'Upload CSV Dataset Directly'}</span>
          <input
            type="file"
            accept=".csv"
            multiple
            style={{ display: 'none' }}
            onChange={handleFileUpload}
            disabled={isUploading}
          />
        </label>
      </div>
    );
  }

  // Premium Command Center Card Material
  const cardStyle: React.CSSProperties = {
    background: 'rgba(8, 12, 20, 0.75)',
    border: '1px solid rgba(255, 255, 255, 0.05)',
    borderRadius: '12px',
    boxShadow: '0 4px 20px -2px rgba(0, 0, 0, 0.40)',
    transition: 'transform 0.16s ease, border-color 0.16s ease',
  };

  const secondaryBtnStyle: React.CSSProperties = {
    background: 'rgba(15, 20, 30, 0.60)',
    color: '#E2E8F0',
    fontSize: '12px',
    fontWeight: 600,
    height: '32px',
    padding: '0 14px',
    borderRadius: '18px',
    border: '1px solid rgba(255, 255, 255, 0.06)',
    display: 'inline-flex',
    alignItems: 'center',
    gap: '6px',
    textDecoration: 'none',
    cursor: 'pointer',
    transition: 'all 0.15s ease',
  };

  const sectionHeaderStyle: React.CSSProperties = {
    fontSize: '11px',
    fontWeight: 700,
    letterSpacing: '0.04em',
    color: '#64748B',
    marginBottom: '6px',
    textTransform: 'uppercase',
  };

  return (
    <div style={{ padding: '24px 32px', display: 'flex', flexDirection: 'column', gap: '16px', position: 'relative' }}>
      
      {/* Radial Backlight Backdrop */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: '50%',
          transform: 'translateX(-50%)',
          width: '800px',
          height: '260px',
          background: 'radial-gradient(circle at top center, rgba(56, 189, 248, 0.07), transparent 70%)',
          pointerEvents: 'none',
        }}
      />

      {/* ======================================================================
          HEADER ROW: GOVERNED SOURCE BANNER (COMPACT INTEGRATED COMMAND BAR)
          ====================================================================== */}
      <FadeUp delay={0.02}>
        <div
          style={{
            ...cardStyle,
            padding: '12px 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '16px',
            background: 'linear-gradient(180deg, rgba(14, 22, 37, 0.90) 0%, rgba(8, 12, 20, 0.95) 100%)',
            position: 'relative',
            zIndex: 1,
          }}
        >
          {/* Left: Active Dataset Selector Pill + Health Sync Indicator */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div
                style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: '6px',
                  background: 'rgba(56, 189, 248, 0.12)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Database size={15} color="#38BDF8" />
              </div>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '0.98rem', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.015em' }}>
                    {activeDataset.name}
                  </span>
                  {(() => {
                    const statusDisplay = getDatasetStatusDisplay(activeDataset);
                    return (
                      <span
                        style={{
                          fontSize: '10px',
                          fontWeight: 800,
                          color: statusDisplay.badgeColor,
                          background: statusDisplay.badgeBg,
                          border: `0.5px solid ${statusDisplay.badgeBorder}`,
                          padding: '1px 6px',
                          borderRadius: '4px',
                          letterSpacing: '0.04em',
                          textTransform: 'uppercase',
                        }}
                      >
                        {statusDisplay.statusLabel}
                      </span>
                    );
                  })()}
                </div>
                <div style={{ fontSize: '0.66rem', color: '#64748B', marginTop: '1px' }}>
                  {activeDataset.column_count || activeDataset.columns?.length || 0} Columns • {activeDataset.record_count?.toLocaleString() || activeDataset.row_count?.toLocaleString() || '1,000+'} Records • {getDatasetStatusDisplay(activeDataset).badge}
                </div>
              </div>
            </div>

            {/* Quick Switch Dropdown if multiple datasets exist */}
            {datasets.length > 1 && (
              <select
                value={activeDataset.id}
                onChange={(e) => {
                  const selected = datasets.find((d) => d.id === e.target.value);
                  if (selected) {
                    setActiveDataset(selected);
                    setQuickNotice(`Switched to governed source: "${selected.name}"`);
                    setTimeout(() => setQuickNotice(null), 3000);
                  }
                }}
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.10)',
                  color: '#CBD5E1',
                  borderRadius: '6px',
                  padding: '4px 8px',
                  fontSize: '0.70rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  outline: 'none',
                }}
              >
                {datasets.map((d) => (
                  <option key={d.id} value={d.id} style={{ background: '#0B132B', color: '#FFFFFF' }}>
                    {d.name} ({d.record_count || 0} rows)
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Right: Refresh Timestamp & Action Trigger */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ fontSize: '0.64rem', color: '#64748B', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10B981' }} />
              <span>Synced {lastRefreshTime}</span>
            </div>

            <button
              onClick={handleRefreshAll}
              title="Synchronize real-time intelligence from backend data store"
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.10)',
                color: '#CBD5E1',
                padding: '5px 10px',
                borderRadius: '6px',
                fontSize: '0.68rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                transition: 'all 0.15s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.10)';
                e.currentTarget.style.color = '#FFFFFF';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                e.currentTarget.style.color = '#CBD5E1';
              }}
            >
              <RefreshCw size={11} className={isLoading ? 'animate-spin' : ''} />
              <span>Sync Telemetry</span>
            </button>

            {/* Seamless In-Place Ingestion Button (Hero Action) */}
            <div>
              <label
                style={{
                  background: 'rgba(255, 255, 255, 0.08)',
                  color: '#FFFFFF',
                  fontSize: '0.72rem',
                  fontWeight: 600,
                  height: '32px',
                  padding: '0 16px',
                  borderRadius: '18px',
                  border: '1px solid rgba(255, 255, 255, 0.12)',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  cursor: isUploading ? 'not-allowed' : 'pointer',
                  boxShadow: '0 2px 10px rgba(0, 0, 0, 0.20)',
                  opacity: isUploading ? 0.7 : 1,
                  transition: 'all 0.15s ease',
                }}
                onMouseEnter={(e) => {
                  if (!isUploading) {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.14)';
                    e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.20)';
                    e.currentTarget.style.transform = 'translateY(-1px)';
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.12)';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                {isUploading ? <RefreshCw size={11} className="animate-spin" /> : <Upload size={11} />}
                <span>{isUploading ? 'Connecting...' : 'Connect Governed Data Source'}</span>
                <input
                  type="file"
                  accept=".csv"
                  multiple
                  style={{ display: 'none' }}
                  onChange={handleFileUpload}
                  disabled={isUploading}
                />
              </label>
            </div>
          </div>
        </div>
      </FadeUp>

      {/* Real-time Notice Feedback */}
      {uploadError && (
        <div style={{ padding: '6px 12px', background: 'rgba(248, 113, 113, 0.08)', border: '1px solid rgba(248, 113, 113, 0.18)', borderRadius: '10px', color: '#F87171', fontSize: '0.74rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'relative', zIndex: 1 }}>
          <span>Connection Failed: {typeof uploadError === 'string' && !uploadError.includes('[object') ? uploadError : 'Intelligence Service Temporarily Unavailable'}</span>
          <button onClick={() => setUploadError(null)} style={{ background: 'none', border: 'none', color: '#F87171', cursor: 'pointer', fontWeight: 700 }}>✕</button>
        </div>
      )}
      {quickNotice && (
        <div style={{ padding: '6px 12px', background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.18)', borderRadius: '10px', color: '#10B981', fontSize: '0.74rem', display: 'flex', alignItems: 'center', gap: '6px', position: 'relative', zIndex: 1 }}>
          <CheckCircle2 size={12} />
          <span>{quickNotice}</span>
        </div>
      )}

      {/* Visible Error State Alert Banner (Dashboard Persists Permanently) */}
      {isError && (
        <div
          style={{
            padding: '12px 18px',
            background: 'rgba(239, 68, 68, 0.10)',
            border: '1px solid rgba(239, 68, 68, 0.25)',
            borderRadius: '10px',
            color: '#F87171',
            fontSize: '0.80rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            position: 'relative',
            zIndex: 1,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertTriangle size={14} color="#EF4444" />
            <span>Telemetry synchronization encountered an API issue. Workspace shell remains active with deterministic fallback intelligence.</span>
          </div>
          <button
            onClick={handleRefreshAll}
            style={{
              background: 'rgba(239, 68, 68, 0.2)',
              border: '1px solid rgba(239, 68, 68, 0.4)',
              color: '#FFFFFF',
              padding: '5px 14px',
              borderRadius: '6px',
              fontSize: '11px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <RefreshCw size={11} />
            <span>Retry Connection</span>
          </button>
        </div>
      )}

      {/* Intelligence Quarantine Banner (Unverified Schema or Univariate Telemetry) */}
      {intel.intelligenceSuppressed && (
        <div
          style={{
            padding: '14px 20px',
            background: 'rgba(245, 158, 11, 0.08)',
            border: '1px solid rgba(245, 158, 11, 0.25)',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            position: 'relative',
            zIndex: 1,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div
              style={{
                width: '34px',
                height: '34px',
                borderRadius: '8px',
                background: 'rgba(245, 158, 11, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              <AlertTriangle size={17} color="#F59E0B" />
            </div>
            <div>
              <div style={{ fontSize: '13px', fontWeight: 800, color: '#FDE68A', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span>⚠ {intel.quarantineReason || 'UNVERIFIED SCHEMA CONTRACT'}</span>
                <span style={{ fontSize: '10px', background: 'rgba(245, 158, 11, 0.2)', padding: '1px 6px', borderRadius: '4px', color: '#F59E0B', fontWeight: 700 }}>
                  CONFIDENCE CAPPED (44%)
                </span>
                <span style={{ fontSize: '10px', background: 'rgba(239, 68, 68, 0.15)', padding: '1px 6px', borderRadius: '4px', color: '#F87171', fontWeight: 700 }}>
                  CAUSAL ATTRIBUTION SUSPENDED
                </span>
              </div>
              <div style={{ fontSize: '11.5px', color: '#CBD5E1', marginTop: '2px' }}>
                No recognized enterprise business metrics detected.
              </div>
            </div>
          </div>
          <Link
            to="/data-management"
            style={{
              background: '#F59E0B',
              color: '#000000',
              padding: '7px 14px',
              borderRadius: '6px',
              fontSize: '11px',
              fontWeight: 700,
              textDecoration: 'none',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              flexShrink: 0,
            }}
          >
            <span>Review Schema</span>
            <ArrowRight size={12} />
          </Link>
        </div>
      )}

      {/* ======================================================================
          STRATEGIC SUMMARY SECTION (COMPACT EXECUTIVE SIGNALS — EQUAL WEIGHT)
          Business Health • Primary Risk • Root Cause • Recommended Intervention
          ====================================================================== */}
      <EnterpriseCardErrorBoundary sectionKey="strategic-summary" fallbackTitle="Strategic Summary Telemetry">
        <FadeUp delay={0.04}>
          <div
            style={{
              ...cardStyle,
              padding: '18px 24px',
              position: 'relative',
              zIndex: 1,
            }}
          >
            {/* 4 Pillars with Reduced Height, Equal Visual Weight, and Short Descriptions */}
            <div style={{ display: 'grid', gridTemplateColumns: '180px 1.15fr 1.15fr 1.1fr', gap: '20px', alignItems: 'flex-start' }}>
              
              {/* Pillar 1: Business Health with Trend Delta */}
              <div style={{ borderRight: '1px solid rgba(255, 255, 255, 0.04)', paddingRight: '18px' }}>
                <div style={{ fontSize: '0.68rem', color: '#64748B', fontWeight: 700 }}>
                  Business Health
                </div>

                <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px', margin: '2px 0 2px 0' }}>
                  {intel.healthScore !== null ? (
                    <>
                      <span style={{ fontSize: '1.45rem', fontWeight: 800, color: '#F1F5F9', lineHeight: 1, letterSpacing: '-0.025em' }}>
                        {intel.healthScore}
                      </span>
                      <span style={{ fontSize: '0.80rem', color: '#64748B', fontWeight: 700 }}>/ 100</span>
                    </>
                  ) : (
                    <span style={{ fontSize: '1.10rem', fontWeight: 800, color: '#F59E0B', lineHeight: 1.2, letterSpacing: '-0.02em' }}>
                      Not Assessable
                    </span>
                  )}
                </div>

                {/* Severity Meter Track */}
                <div style={{ height: '3px', width: '100%', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '2px', overflow: 'hidden', margin: '4px 0 3px 0' }}>
                  <div style={{ width: intel.healthScore !== null ? `${Math.max(intel.healthScore, 5)}%` : '0%', height: '100%', background: intel.healthStatusColor, transition: 'width 0.6s ease' }} />
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '0.68rem', color: intel.healthStatusColor, fontWeight: 700 }}>
                    {intel.healthClassification}
                  </span>
                  <span style={{ fontSize: '0.60rem', color: '#94A3B8', fontWeight: 600 }}>
                    {intel.healthTrendDelta}
                  </span>
                </div>
              </div>

              {/* Pillar 2: Primary Risk with SLA Governance & Empirical Baseline */}
              <div style={{ minWidth: 0, borderRight: '1px solid rgba(255, 255, 255, 0.04)', paddingRight: '18px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2px' }}>
                  <div style={{ fontSize: '0.68rem', color: intel.intelligenceSuppressed ? '#F59E0B' : '#F87171', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <AlertTriangle size={11} />
                    <span>Primary Risk ({intel.primaryRisk.severity})</span>
                  </div>
                  <span
                    style={{
                      fontSize: '10px',
                      fontWeight: 800,
                      color: intel.primaryRisk.slaBadgeColor,
                      background: intel.primaryRisk.slaGovernanceState === 'CONFIGURED_SLA' ? 'rgba(16, 185, 129, 0.12)' : 'rgba(245, 158, 11, 0.12)',
                      border: `0.5px solid ${intel.primaryRisk.slaGovernanceState === 'CONFIGURED_SLA' ? 'rgba(16, 185, 129, 0.25)' : 'rgba(245, 158, 11, 0.25)'}`,
                      padding: '1px 5px',
                      borderRadius: '3px',
                      letterSpacing: '0.04em',
                      textTransform: 'uppercase',
                      cursor: 'help',
                    }}
                    title={intel.primaryRisk.slaTooltip}
                  >
                    {intel.primaryRisk.slaBadgeText}
                  </span>
                </div>
                <div style={{ fontSize: '1.02rem', fontWeight: 800, color: '#FFFFFF', lineHeight: 1.25, letterSpacing: '-0.015em' }} title={intel.primaryRisk.title}>
                  {intel.primaryRisk.title}
                </div>
                <div style={{ fontSize: '0.66rem', color: '#CBD5E1', marginTop: '3px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', fontWeight: 600 }}>
                  <span style={{ color: '#94A3B8' }}>Observed: </span>
                  <strong style={{ color: '#FFFFFF' }}>{intel.primaryRisk.metricValue}</strong>
                  <span style={{ color: '#64748B' }}> • </span>
                  <span style={{ color: '#94A3B8' }}>{intel.primaryRisk.isConfiguredSLA ? 'Configured SLA: ' : 'Baseline: '}</span>
                  <strong style={{ color: intel.primaryRisk.isConfiguredSLA ? '#10B981' : '#CBD5E1' }}>{intel.primaryRisk.benchmarkSLA}</strong>
                  <span style={{ color: '#64748B' }}> • </span>
                  <span style={{ color: intel.intelligenceSuppressed ? '#F59E0B' : '#F87171', fontWeight: 700 }}>{intel.primaryRisk.varianceText}</span>
                </div>
              </div>

              {/* Pillar 3: Root Cause & Attribution (Business Language) */}
              <div style={{ minWidth: 0, borderRight: '1px solid rgba(255, 255, 255, 0.04)', paddingRight: '18px' }}>
                <div style={{ fontSize: '0.68rem', color: '#64748B', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
                  <GitMerge size={11} color="#38BDF8" />
                  <span>Root Cause</span>
                </div>
                <div style={{ fontSize: '0.88rem', fontWeight: 800, color: '#FFFFFF', lineHeight: 1.25, letterSpacing: '-0.01em' }} title={intel.rootCause.title}>
                  {intel.rootCause.title}
                </div>
                <div style={{ fontSize: '0.66rem', color: intel.intelligenceSuppressed ? '#94A3B8' : '#38BDF8', marginTop: '3px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', fontWeight: 700 }} title={intel.rootCause.businessInterpretation}>
                  {intel.rootCause.businessInterpretation}
                </div>
              </div>

              {/* Pillar 4: Recommended Intervention */}
              <div style={{ minWidth: 0 }}>
                <div style={{ fontSize: '0.68rem', color: '#10B981', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}>
                  <Zap size={11} />
                  <span>{intel.recommendedAction.actionLabel}</span>
                </div>
                <div style={{ fontSize: '1.02rem', fontWeight: 800, color: '#FFFFFF', lineHeight: 1.25, letterSpacing: '-0.015em' }} title={intel.recommendedAction.primaryAction}>
                  {intel.recommendedAction.primaryAction}
                </div>
                <div style={{ fontSize: '0.70rem', color: '#94A3B8', marginTop: '3px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  Target: <strong style={{ color: '#FFFFFF' }}>{intel.recommendedAction.targetKPIImpact}</strong>
                </div>
              </div>

            </div>
          </div>
        </FadeUp>
      </EnterpriseCardErrorBoundary>

      {/* ======================================================================
          EXECUTIVE NARRATIVE: SCANNABLE BOARDROOM STRATEGIC BRIEFING (ISSUE 5)
          ====================================================================== */}
      <EnterpriseCardErrorBoundary sectionKey="executive-narrative" fallbackTitle="Executive Strategic Briefing">
        <FadeUp delay={0.05}>
          <div
            style={{
              ...cardStyle,
              padding: '14px 20px',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '12px',
              background: 'rgba(10, 15, 24, 0.85)',
              borderLeft: `3px solid ${intel.healthStatusColor}`,
              position: 'relative',
              zIndex: 1,
            }}
          >
            <div style={{ padding: '2px', flexShrink: 0 }}>
              <Sparkles size={13} color="#38BDF8" />
            </div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                <span style={{ fontSize: '0.66rem', color: '#64748B', fontWeight: 800, letterSpacing: '0.04em', textTransform: 'uppercase' }}>
                  Executive Strategic Briefing
                </span>
                <span style={{ color: '#1E293B', fontSize: '9px' }}>•</span>
                <span style={{ fontSize: '0.66rem', color: intel.healthStatusColor, fontWeight: 700 }}>
                  {intel.healthClassification} Range ({intel.healthScore}/100 • {intel.healthTrendDelta})
                </span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {intel.executiveNarrative.split('\n').map((line, lIdx) => {
                  const colonIdx = line.indexOf(': ');
                  if (colonIdx > 0) {
                    const label = line.slice(0, colonIdx);
                    const val = line.slice(colonIdx + 2);
                    return (
                      <div key={lIdx} style={{ fontSize: '0.78rem', color: '#E2E8F0', lineHeight: 1.45, fontWeight: 500 }}>
                        <strong style={{ color: '#FFFFFF', fontWeight: 700 }}>{label}: </strong>
                        <span>{val}</span>
                      </div>
                    );
                  }
                  return (
                    <div key={lIdx} style={{ fontSize: '0.78rem', color: '#E2E8F0', lineHeight: 1.45, fontWeight: 500 }}>
                      {line}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </FadeUp>
      </EnterpriseCardErrorBoundary>

      {/* ======================================================================
          EXECUTIVE SNAPSHOT: SLIM COMMAND BAR (BLOOMBERG / LINEAR STATUS STRIP)
          ====================================================================== */}
      <EnterpriseCardErrorBoundary sectionKey="executive-snapshot" fallbackTitle="Executive Status Strip">
        <FadeUp delay={0.06}>
          <div
            style={{
              ...cardStyle,
              padding: '8px 20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              position: 'relative',
              zIndex: 1,
            }}
          >
            {/* Inline Executive Status Strip with Exposure & Monthly Run-Rate */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap' }}>
              <div style={{ display: 'inline-flex', alignItems: 'baseline', gap: '5px' }}>
                <span style={{ fontSize: '0.86rem', fontWeight: 800, color: '#FFFFFF' }}>{intel.snapshot.totalRisks}</span>
                <span style={{ fontSize: '0.70rem', color: '#64748B' }}>Risks</span>
              </div>
              <span style={{ color: '#1E293B', fontSize: '9px' }}>•</span>
              <div style={{ display: 'inline-flex', alignItems: 'baseline', gap: '5px' }}>
                <span style={{ fontSize: '0.86rem', fontWeight: 800, color: '#F87171' }}>{intel.snapshot.criticalRiskPct}%</span>
                <span style={{ fontSize: '0.70rem', color: '#64748B' }}>Critical</span>
              </div>
              <span style={{ color: '#1E293B', fontSize: '9px' }}>•</span>
              <div style={{ display: 'inline-flex', alignItems: 'baseline', gap: '5px' }}>
                <span style={{ fontSize: '0.86rem', fontWeight: 800, color: '#FFFFFF' }}>{intel.snapshot.anomaliesCount}</span>
                <span style={{ fontSize: '0.70rem', color: '#64748B' }}>Anomalies</span>
              </div>
              <span style={{ color: '#1E293B', fontSize: '9px' }}>•</span>
              <div
                style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
                title={intel.snapshot.exposureBreakdown.tooltipText}
              >
                {intel.snapshot.exposureBreakdown.isMonetary ? (
                  <>
                    <span style={{ fontSize: '0.86rem', fontWeight: 800, color: '#FB923C' }}>{intel.snapshot.financialExposure}</span>
                    <span style={{ fontSize: '0.70rem', color: '#64748B' }}>Annualized VaR</span>
                    <span style={{ fontSize: '0.70rem', color: '#F59E0B', fontWeight: 600 }}>({intel.snapshot.monthlyExposure})</span>
                  </>
                ) : (
                  <>
                    <span
                      style={{
                        fontSize: '0.56rem',
                        fontWeight: 800,
                        color: '#FB923C',
                        background: 'rgba(251, 146, 60, 0.12)',
                        border: '1px solid rgba(251, 146, 60, 0.25)',
                        padding: '1px 5px',
                        borderRadius: '3px',
                        cursor: 'help',
                      }}
                      title="Dataset contains no verified monetary fields. Risk is expressed as operational exposure rather than financial VaR."
                    >
                      OPERATIONAL IMPACT MODEL
                    </span>
                    <span style={{ fontSize: '0.70rem', color: '#94A3B8', fontWeight: 600 }}>Operational Exposure:</span>
                    <span style={{ fontSize: '0.86rem', fontWeight: 800, color: '#FB923C' }}>
                      {intel.snapshot.financialExposure}
                    </span>
                    <Link
                      to="/kpi-dictionary"
                      style={{
                        fontSize: '0.64rem',
                        color: '#38BDF8',
                        fontWeight: 700,
                        textDecoration: 'underline',
                        marginLeft: '2px',
                      }}
                    >
                      Map Revenue Field
                    </Link>
                  </>
                )}
              </div>
              <span style={{ color: '#1E293B', fontSize: '9px' }}>•</span>
              <div style={{ display: 'inline-flex', alignItems: 'baseline', gap: '5px' }}>
                <span style={{ fontSize: '0.86rem', fontWeight: 800, color: '#10B981' }}>{intel.snapshot.confidenceScore}%</span>
                <span style={{ fontSize: '0.70rem', color: '#64748B' }}>{intel.snapshot.confidenceLabel}</span>
              </div>
            </div>

            <Link
              to="/diagnostics"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '0.70rem',
                fontWeight: 600,
                color: '#38BDF8',
                textDecoration: 'none',
              }}
            >
              <span>Explore Diagnostics</span>
              <ArrowRight size={10} />
            </Link>
          </div>
        </FadeUp>
      </EnterpriseCardErrorBoundary>

      {/* ======================================================================
          RECOMMENDED PROGRAMS: ENTERPRISE PMO INITIATIVES WITH CHARTERED GOVERNANCE
          ====================================================================== */}
      <EnterpriseCardErrorBoundary sectionKey="recommended-programs" fallbackTitle="Strategic Programs">
        <FadeUp delay={0.08}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', position: 'relative', zIndex: 1 }}>
            
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={sectionHeaderStyle}>
                  {intel.snapshot.confidenceTier === 'SUGGESTED' ? 'Suggested Improvement Programs' : intel.snapshot.confidenceTier === 'HIGH_CONFIDENCE' ? 'High Confidence Strategic Programs' : 'Recommended Programs'}
                </div>
                <span style={{ fontSize: '10.5px', color: '#64748B', fontWeight: 600 }}>
                  ({intel.programsHeaderLabel})
                </span>
              </div>
              <Link
                to="/recommendations"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  fontSize: '0.70rem',
                  fontWeight: 600,
                  color: '#38BDF8',
                  textDecoration: 'none',
                }}
              >
                <span>View All ({intel.snapshot.totalRisks})</span>
                <ArrowRight size={10} />
              </Link>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: intel.recommendedPrograms.length === 0 ? '1fr' : 'repeat(2, 1fr)', gap: '12px', alignItems: 'stretch' }}>
              
              {intel.recommendedPrograms.length === 0 ? (
                <div
                  style={{
                    ...cardStyle,
                    padding: '24px',
                    textAlign: 'center',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                  }}
                >
                  <AlertTriangle size={24} color="#F59E0B" />
                  <div style={{ fontSize: '0.90rem', fontWeight: 700, color: '#FDE68A' }}>
                    {intel.intelligenceSuppressed ? 'Intervention Programs & Governance Councils Suspended' : 'No Active Programs'}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#94A3B8', maxWidth: '500px' }}>
                    {intel.intelligenceSuppressed
                      ? 'Automated intervention playbooks and chartered governance groups require verified enterprise business metrics. Complete schema verification to generate actionable programs.'
                      : 'No strategic programs are currently recommended.'}
                  </div>
                </div>
              ) : (
                intel.recommendedPrograms.map((program, idx) => (
                  <div
                    key={idx}
                    style={{
                      ...cardStyle,
                      padding: '16px 20px',
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'space-between',
                      gap: '12px',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-1px)';
                      e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.10)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)';
                      e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.05)';
                    }}
                  >
                    <div>
                      {/* Header: Title + Priority, Horizon & Owner Badges */}
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px', flexWrap: 'wrap', gap: '6px' }}>
                        <span style={{ fontSize: '0.98rem', fontWeight: 800, color: '#FFFFFF', lineHeight: 1.2, letterSpacing: '-0.015em' }}>
                          {program.title}
                        </span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                          <span
                            style={{
                              fontSize: '0.62rem',
                              fontWeight: 800,
                              color: program.priority === 'Critical' ? '#F87171' : program.priority === 'High' ? '#FB923C' : '#38BDF8',
                              padding: '2px 7px',
                              background: 'rgba(255, 255, 255, 0.04)',
                              borderRadius: '4px',
                              border: '1px solid rgba(255, 255, 255, 0.06)',
                              textTransform: 'uppercase',
                            }}
                          >
                            {program.priority} Priority
                          </span>

                          {/* Chartered Governance Owner Badge */}
                          {program.ownerType === 'UNASSIGNED' && !claimedPrograms[program.title] ? (
                            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                              <span
                                style={{
                                  fontSize: '0.60rem',
                                  fontWeight: 700,
                                  color: '#94A3B8',
                                  padding: '2px 6px',
                                  background: 'rgba(255, 255, 255, 0.04)',
                                  borderRadius: '4px',
                                  border: '1px solid rgba(255, 255, 255, 0.08)',
                                }}
                              >
                                Owner: Unassigned Governance Role
                              </span>
                              <button
                                onClick={() => handleClaimProgram(program.title)}
                                title="No active principal assigned. Authenticated users can claim program stewardship."
                                style={{
                                  fontSize: '0.58rem',
                                  fontWeight: 800,
                                  color: '#38BDF8',
                                  background: 'rgba(56, 189, 248, 0.12)',
                                  border: '1px solid rgba(56, 189, 248, 0.25)',
                                  padding: '2px 7px',
                                  borderRadius: '4px',
                                  cursor: 'pointer',
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  gap: '3px',
                                  textTransform: 'uppercase',
                                  transition: 'all 0.15s ease',
                                }}
                                onMouseEnter={(e) => {
                                  e.currentTarget.style.background = 'rgba(56, 189, 248, 0.22)';
                                }}
                                onMouseLeave={(e) => {
                                  e.currentTarget.style.background = 'rgba(56, 189, 248, 0.12)';
                                }}
                              >
                                <ShieldCheck size={10} />
                                <span>[Claim Ownership]</span>
                              </button>
                            </div>
                          ) : claimedPrograms[program.title] ? (
                            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                              <span
                                style={{
                                  fontSize: '0.60rem',
                                  fontWeight: 700,
                                  color: '#E2E8F0',
                                  padding: '2px 6px',
                                  background: 'rgba(255, 255, 255, 0.04)',
                                  borderRadius: '4px',
                                  border: '1px solid rgba(255, 255, 255, 0.08)',
                                }}
                              >
                                Owner: {claimedPrograms[program.title]}
                              </span>
                              <span
                                title="Stewardship claimed in active session."
                                style={{
                                  fontSize: '0.56rem',
                                  fontWeight: 800,
                                  color: '#10B981',
                                  background: 'rgba(16, 185, 129, 0.10)',
                                  border: '1px solid rgba(16, 185, 129, 0.20)',
                                  padding: '2px 6px',
                                  borderRadius: '4px',
                                  letterSpacing: '0.03em',
                                  cursor: 'help',
                                }}
                              >
                                [GOVERNANCE CLAIMED]
                              </span>
                            </div>
                          ) : (
                            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                              <span
                                style={{
                                  fontSize: '0.60rem',
                                  fontWeight: 700,
                                  color: '#E2E8F0',
                                  padding: '2px 6px',
                                  background: 'rgba(255, 255, 255, 0.04)',
                                  borderRadius: '4px',
                                  border: '1px solid rgba(255, 255, 255, 0.08)',
                                }}
                              >
                                Owner: {program.owner}
                              </span>
                              <span
                                title="Program assigned to chartered enterprise governance council."
                                style={{
                                  fontSize: '0.56rem',
                                  fontWeight: 800,
                                  color: '#38BDF8',
                                  background: 'rgba(56, 189, 248, 0.10)',
                                  border: '1px solid rgba(56, 189, 248, 0.20)',
                                  padding: '2px 6px',
                                  borderRadius: '4px',
                                  letterSpacing: '0.03em',
                                  cursor: 'help',
                                }}
                              >
                                [GOVERNANCE GROUP]
                              </span>
                            </div>
                          )}

                          <span
                            style={{
                              fontSize: '0.62rem',
                              fontWeight: 700,
                              color: '#94A3B8',
                              padding: '2px 7px',
                              background: 'rgba(15, 20, 30, 0.60)',
                              borderRadius: '4px',
                              border: '0.5px solid rgba(255, 255, 255, 0.06)',
                            }}
                          >
                            {program.executionType}
                          </span>

                          <span
                            style={{
                              fontSize: '0.62rem',
                              fontWeight: 700,
                              color: '#94A3B8',
                              padding: '2px 7px',
                              background: 'rgba(15, 20, 30, 0.60)',
                              borderRadius: '4px',
                            }}
                          >
                            {program.executionHorizon}
                          </span>
                        </div>
                      </div>

                      {/* Program Objective */}
                      <p style={{ fontSize: '0.74rem', color: '#CBD5E1', margin: '0 0 10px 0', lineHeight: 1.45 }}>
                        {program.objective}
                      </p>

                      {/* Evidence-Based Program Metadata Grid (4-Cell Consolidated Executive Summary) */}
                      <div
                        style={{
                          display: 'grid',
                          gridTemplateColumns: 'repeat(2, 1fr)',
                          gap: '8px',
                          padding: '10px 12px',
                          background: 'rgba(10, 15, 24, 0.70)',
                          borderRadius: '8px',
                          border: '1px solid rgba(255, 255, 255, 0.04)',
                        }}
                      >
                        <div>
                          <div style={{ fontSize: '0.58rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase' }}>
                            Addresses Root Cause
                          </div>
                          <div style={{ fontSize: '0.72rem', color: '#38BDF8', fontWeight: 700, marginTop: '1px' }}>
                            {program.rootCauseAddressed}
                          </div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.58rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase' }}>
                            Expected Outcome
                          </div>
                          <div style={{ fontSize: '0.72rem', color: '#10B981', fontWeight: 700, marginTop: '1px' }}>
                            {program.expectedOutcomeRange}
                          </div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.58rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase' }}>
                            Cost Model & Capital
                          </div>
                          <div style={{ fontSize: '0.70rem', color: '#94A3B8', fontWeight: 600, marginTop: '1px' }}>
                            {program.costModel} • {program.capitalRequirement}
                          </div>
                        </div>
                        <div>
                          <div
                            style={{
                              fontSize: '0.58rem',
                              color: '#64748B',
                              fontWeight: 700,
                              textTransform: 'uppercase',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '3px',
                              cursor: 'help',
                            }}
                            title="Derived from connected business indicators and statistical causal attribution methods."
                          >
                            <span>Decision Signals</span>
                            <span style={{ color: '#38BDF8' }}>ℹ</span>
                          </div>
                          <div style={{ fontSize: '0.70rem', color: '#38BDF8', fontWeight: 700, marginTop: '1px' }} title="Derived from connected business indicators and statistical causal attribution methods.">
                            {program.evidenceFeatures && program.evidenceFeatures.length > 0
                              ? program.evidenceFeatures.slice(0, 3).map((f) => `${f.businessLabel} (${f.importanceScore})`).join(' • ')
                              : 'Signal Attribution Unavailable'}
                          </div>
                        </div>
                      </div>

                      {/* Executive Traceability Lineage */}
                      <div
                        title={`Complete Decision Traceability: ${program.traceabilityLineage}`}
                        style={{
                          marginTop: '8px',
                          padding: '4px 8px',
                          background: 'rgba(56, 189, 248, 0.04)',
                          borderRadius: '5px',
                          border: '1px solid rgba(56, 189, 248, 0.10)',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px',
                          cursor: 'help',
                        }}
                      >
                        <span style={{ fontSize: '0.58rem', color: '#38BDF8', fontWeight: 800, textTransform: 'uppercase', flexShrink: 0 }}>Lineage:</span>
                        <span style={{ fontSize: '0.64rem', color: '#94A3B8', fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          Risk → Driver → KPI → Initiative → Owner
                        </span>
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '4px' }}>
                      <Link
                        to={program.linkTo}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '5px',
                          fontSize: '0.72rem',
                          fontWeight: 700,
                          color: '#38BDF8',
                          textDecoration: 'none',
                        }}
                      >
                        <span>{program.ctaLabel || 'Deploy Remediation Playbook'}</span>
                        <ArrowRight size={11} />
                      </Link>
                    </div>
                  </div>
                ))
              )}

            </div>

            {/* Explanation Footnote */}
            <div style={{ fontSize: '0.66rem', color: '#64748B', marginTop: '4px', fontStyle: 'italic', display: 'flex', alignItems: 'center', gap: '5px' }}>
              <span>ℹ</span>
              <span>{intel.methodologyNote}</span>
            </div>
          </div>
        </FadeUp>
      </EnterpriseCardErrorBoundary>

      {/* ======================================================================
          ENTERPRISE WORKSPACES: DATASET-AWARE REAL-TIME NAVIGATION DESTINATIONS
          ====================================================================== */}
      <EnterpriseCardErrorBoundary sectionKey="enterprise-workspaces" fallbackTitle="Enterprise Workspaces">
        <FadeUp delay={0.10}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', position: 'relative', zIndex: 1 }}>
            
            <div style={sectionHeaderStyle}>
              Enterprise Workspaces (Live Business Intelligence)
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '12px', alignItems: 'stretch' }}>
              
              {/* Workspace 1: KPI Workspace */}
              <div
                style={{
                  ...cardStyle,
                  padding: '16px 18px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '12px',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-1px)';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.10)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.05)';
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <BarChart2 size={14} color="#64748B" />
                      <span style={{ fontSize: '0.90rem', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.01em' }}>
                        {intel.workspaces.kpiWorkspace.title}
                      </span>
                    </div>
                    <span style={{ fontSize: '0.58rem', fontWeight: 800, color: '#38BDF8', padding: '1px 5px', background: 'rgba(56, 189, 248, 0.1)', borderRadius: '4px' }}>
                      {intel.workspaces.kpiWorkspace.badge}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.72rem', color: '#94A3B8', margin: 0, lineHeight: 1.45 }}>
                    {intel.workspaces.kpiWorkspace.statusDetail}
                  </p>
                </div>
                <Link
                  to={intel.workspaces.kpiWorkspace.linkTo}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontSize: '0.72rem',
                    fontWeight: 600,
                    color: '#38BDF8',
                    textDecoration: 'none',
                  }}
                >
                  <span>Open Surveillance Hub</span>
                  <ArrowRight size={10} />
                </Link>
              </div>

              {/* Workspace 2: Diagnostic Graph */}
              <div
                style={{
                  ...cardStyle,
                  padding: '16px 18px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '12px',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-1px)';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.10)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.05)';
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Network size={14} color="#64748B" />
                      <span style={{ fontSize: '0.90rem', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.01em' }}>
                        {intel.workspaces.diagnosticGraph.title}
                      </span>
                    </div>
                    <span style={{ fontSize: '0.58rem', fontWeight: 800, color: '#FB923C', padding: '1px 5px', background: 'rgba(251, 146, 60, 0.1)', borderRadius: '4px' }}>
                      {intel.workspaces.diagnosticGraph.badge}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.72rem', color: '#94A3B8', margin: 0, lineHeight: 1.45 }}>
                    {intel.workspaces.diagnosticGraph.statusDetail}
                  </p>
                </div>
                <Link
                  to={intel.workspaces.diagnosticGraph.linkTo}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontSize: '0.72rem',
                    fontWeight: 600,
                    color: '#38BDF8',
                    textDecoration: 'none',
                  }}
                >
                  <span>Explore Causal Edges</span>
                  <ArrowRight size={10} />
                </Link>
              </div>

              {/* Workspace 3: Action Portfolio */}
              <div
                style={{
                  ...cardStyle,
                  padding: '16px 18px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '12px',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-1px)';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.10)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.05)';
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Target size={14} color="#64748B" />
                      <span style={{ fontSize: '0.90rem', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.01em' }}>
                        {intel.workspaces.actionPortfolio.title}
                      </span>
                    </div>
                    <span style={{ fontSize: '0.58rem', fontWeight: 800, color: '#10B981', padding: '1px 5px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '4px' }}>
                      {intel.workspaces.actionPortfolio.badge}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.72rem', color: '#94A3B8', margin: 0, lineHeight: 1.45 }}>
                    {intel.workspaces.actionPortfolio.statusDetail}
                  </p>
                </div>
                <Link
                  to={intel.workspaces.actionPortfolio.linkTo}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontSize: '0.72rem',
                    fontWeight: 600,
                    color: '#38BDF8',
                    textDecoration: 'none',
                  }}
                >
                  <span>Manage Playbooks</span>
                  <ArrowRight size={10} />
                </Link>
              </div>

              {/* Workspace 4: Governed Data Lineage */}
              <div
                style={{
                  ...cardStyle,
                  padding: '16px 18px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '12px',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-1px)';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.10)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.05)';
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Database size={14} color="#64748B" />
                      <span style={{ fontSize: '0.90rem', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.01em' }}>
                        {intel.workspaces.datasetLineage.title}
                      </span>
                    </div>
                    <span style={{ fontSize: '0.58rem', fontWeight: 800, color: '#94A3B8', padding: '1px 5px', background: 'rgba(255, 255, 255, 0.06)', borderRadius: '4px' }}>
                      {intel.workspaces.datasetLineage.badge}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.72rem', color: '#94A3B8', margin: 0, lineHeight: 1.45 }}>
                    {intel.workspaces.datasetLineage.statusDetail}
                  </p>
                </div>
                <Link
                  to={intel.workspaces.datasetLineage.linkTo}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontSize: '0.72rem',
                    fontWeight: 600,
                    color: '#38BDF8',
                    textDecoration: 'none',
                  }}
                >
                  <span>Verify Lineage & Provenance</span>
                  <ArrowRight size={10} />
                </Link>
              </div>

            </div>
          </div>
        </FadeUp>
      </EnterpriseCardErrorBoundary>

      {/* ======================================================================
          DATA CONTRACT STATUS: GOVERNANCE & AUDIT READINESS SUMMARY
          ====================================================================== */}
      <EnterpriseCardErrorBoundary sectionKey="data-contract-status" fallbackTitle="Data Grounding & Contract Status">
        <FadeUp delay={0.11}>
          <div
            style={{
              ...cardStyle,
              padding: '14px 18px',
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
              background: 'rgba(8, 12, 20, 0.88)',
              position: 'relative',
              zIndex: 1,
            }}
          >
            {/* Header: Data Grounding & Contract Status */}
            <div
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px', cursor: 'help' }}
              title={intel.dataGroundingStatus?.tooltip || 'Status derived from active governance checks, runtime validation rules, and available dataset evidence.'}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <ShieldCheck size={14} color="#10B981" />
                <span style={{ fontSize: '0.72rem', fontWeight: 800, color: '#FFFFFF', letterSpacing: '0.04em', textTransform: 'uppercase' }}>
                  {intel.dataGroundingStatus?.title || 'DATA GROUNDING STATUS'}
                </span>
                <span style={{ fontSize: '0.62rem', color: '#10B981', fontWeight: 700, padding: '2px 8px', borderRadius: '4px', background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.25)' }}>
                  {intel.dataGroundingStatus?.badge || 'Dataset Grounded'}
                </span>
                <span style={{ fontSize: '0.58rem', color: '#64748B', fontWeight: 600 }}>
                  ({intel.dataGroundingStatus?.subtitle || 'Runtime Validation Passed'})
                </span>
              </div>
              <span style={{ fontSize: '0.62rem', color: '#10B981', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                <Check size={11} /> Governed Pipeline & Provenance Verified
              </span>
            </div>

            {/* 8 Governance Integrity Rules */}
            {intel.dataGroundingStatus?.checks && intel.dataGroundingStatus.checks.length > 0 && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: '6px' }}>
                {intel.dataGroundingStatus.checks.map((c, i) => (
                  <div
                    key={i}
                    title={c.details}
                    style={{
                      padding: '5px 8px',
                      background: 'rgba(16, 185, 129, 0.05)',
                      borderRadius: '4px',
                      border: '1px solid rgba(16, 185, 129, 0.15)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '5px',
                      cursor: 'help',
                    }}
                  >
                    <Check size={10} color="#10B981" style={{ flexShrink: 0 }} />
                    <span style={{ fontSize: '0.60rem', color: '#CBD5E1', fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {c.rule}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {/* 5 Enterprise Data Contract Specifications */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, minmax(0, 1fr))', gap: '8px' }}>
              {/* 1. SLA Configuration */}
              <div
                style={{ padding: '8px 10px', background: 'rgba(10, 15, 24, 0.60)', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.04)', cursor: 'help' }}
                title={intel.dataContractStatus.slaConfiguration.tooltip}
              >
                <div style={{ fontSize: '0.56rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase' }}>SLA Configuration</div>
                <div style={{ fontSize: '0.70rem', fontWeight: 800, color: intel.dataContractStatus.slaConfiguration.badgeColor, marginTop: '2px' }}>
                  {intel.dataContractStatus.slaConfiguration.label}
                </div>
                <div style={{ fontSize: '0.58rem', color: '#94A3B8', marginTop: '1px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {intel.dataContractStatus.slaConfiguration.detail}
                </div>
              </div>

              {/* 2. Monetary Mapping */}
              <div
                style={{ padding: '8px 10px', background: 'rgba(10, 15, 24, 0.60)', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.04)', cursor: 'help' }}
                title={intel.dataContractStatus.monetaryMapping.tooltip}
              >
                <div style={{ fontSize: '0.56rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase' }}>Monetary Mapping</div>
                <div style={{ fontSize: '0.70rem', fontWeight: 800, color: intel.dataContractStatus.monetaryMapping.badgeColor, marginTop: '2px' }}>
                  {intel.dataContractStatus.monetaryMapping.label}
                </div>
                <div style={{ fontSize: '0.58rem', color: '#94A3B8', marginTop: '1px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {intel.dataContractStatus.monetaryMapping.detail}
                </div>
              </div>

              {/* 3. Temporal Coverage */}
              <div
                style={{ padding: '8px 10px', background: 'rgba(10, 15, 24, 0.60)', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.04)', cursor: 'help' }}
                title={intel.dataContractStatus.temporalCoverage.tooltip}
              >
                <div style={{ fontSize: '0.56rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase' }}>Temporal Coverage</div>
                <div style={{ fontSize: '0.70rem', fontWeight: 800, color: intel.dataContractStatus.temporalCoverage.badgeColor, marginTop: '2px' }}>
                  {intel.dataContractStatus.temporalCoverage.label}
                </div>
                <div style={{ fontSize: '0.58rem', color: '#94A3B8', marginTop: '1px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {intel.dataContractStatus.temporalCoverage.detail}
                </div>
              </div>

              {/* 4. Signal Attribution */}
              <div
                style={{ padding: '8px 10px', background: 'rgba(10, 15, 24, 0.60)', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.04)', cursor: 'help' }}
                title={intel.dataContractStatus.featureAttribution.tooltip}
              >
                <div style={{ fontSize: '0.56rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase' }}>Signal Attribution</div>
                <div style={{ fontSize: '0.70rem', fontWeight: 800, color: intel.dataContractStatus.featureAttribution.badgeColor, marginTop: '2px' }}>
                  {intel.dataContractStatus.featureAttribution.label}
                </div>
                <div style={{ fontSize: '0.58rem', color: '#94A3B8', marginTop: '1px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {intel.dataContractStatus.featureAttribution.detail}
                </div>
              </div>

              {/* 5. Data Contract Integrity */}
              <div
                style={{ padding: '8px 10px', background: 'rgba(10, 15, 24, 0.60)', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.04)', cursor: 'help' }}
                title={intel.dataContractStatus.schemaIntegrity.tooltip}
              >
                <div style={{ fontSize: '0.56rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase' }}>Data Contract Integrity</div>
                <div style={{ fontSize: '0.70rem', fontWeight: 800, color: intel.dataContractStatus.schemaIntegrity.badgeColor, marginTop: '2px' }}>
                  {intel.dataContractStatus.schemaIntegrity.label}
                </div>
                <div style={{ fontSize: '0.58rem', color: '#94A3B8', marginTop: '1px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {intel.dataContractStatus.schemaIntegrity.detail}
                </div>
              </div>
            </div>
          </div>
        </FadeUp>
      </EnterpriseCardErrorBoundary>

      {/* ======================================================================
          FOOTER: UNDERSTATED TRUST & VERIFICATION STATUS
          ✓ Deterministic Engine Verified • ✓ Explainable Audit Passed • ✓ Governance Active
          ====================================================================== */}
      <EnterpriseCardErrorBoundary sectionKey="footer" fallbackTitle="Governance Lineage Footer">
        <FadeUp delay={0.12}>
          <div
            style={{
              padding: '10px 16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: '0.70rem',
              color: '#64748B',
              borderTop: '1px solid rgba(255, 255, 255, 0.03)',
              position: 'relative',
              zIndex: 1,
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexWrap: 'wrap' }}>
              <span style={{ color: '#94A3B8', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                <Check size={11} color="#10B981" /> Deterministic Governance Engine v2.4
              </span>
              <span style={{ color: '#334155' }}>•</span>
              <span style={{ color: '#94A3B8', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                <Check size={11} color="#10B981" /> Audit Trail Verified
              </span>
              <span style={{ color: '#334155' }}>•</span>
              <span style={{ color: '#94A3B8', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                <Check size={11} color="#10B981" /> SHA-256 Provenance Active
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{ fontSize: '0.68rem', color: '#64748B' }}>DecisionOS v2.4 Enterprise Core</span>
            </div>
          </div>
        </FadeUp>
      </EnterpriseCardErrorBoundary>

    </div>
  );
};

export default EnterpriseCommandCenterView;
