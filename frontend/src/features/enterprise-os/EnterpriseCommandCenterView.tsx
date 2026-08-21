import React, { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Activity,
  Award,
  ShieldCheck,
  TrendingUp,
  Sparkles,
  Layers,
  BarChart3,
  CheckCircle2,
  DollarSign,
  Database,
  Upload,
  AlertTriangle,
  Zap,
  ArrowRight,
  RefreshCw,
  GitMerge
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { queryKeys } from '../../shared/api/queryKeys';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { BackendOfflineScreen } from '../../shared/components/feedback/BackendOfflineScreen';
import { NoDatasetEmptyState } from '../../shared/components/feedback/NoDatasetEmptyState';
import { ActivityFeed } from '../shared/ActivityFeed';
import { BusinessHealthResponse, IntelligenceReportResponse } from '../../types';

export const EnterpriseCommandCenterView: React.FC = () => {
  const { datasets, activeDataset, setActiveDataset, refreshDatasets } = useDataset();
  const queryClient = useQueryClient();
  const { status: healthStatus, checkHealth } = useBackendHealth();
  const [quickNotice, setQuickNotice] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // In-place CSV Dataset Upload Handler
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setIsUploading(true);
      setUploadError(null);
      setQuickNotice(`Uploading & parsing "${file.name}"... Initializing 8-stage intelligence pipeline.`);
      
      const newDataset = await DecisionApi.uploadDataset(file);
      if (newDataset) {
        setActiveDataset(newDataset);
        await refreshDatasets();
        await queryClient.invalidateQueries();
        await queryClient.refetchQueries({ queryKey: queryKeys.reports.executive(newDataset.id) });
        await queryClient.refetchQueries({ queryKey: queryKeys.reports.healthScore(newDataset.id) });
        setQuickNotice(`Dataset "${newDataset.name}" uploaded and active! Real intelligence pipeline computed.`);
        setTimeout(() => setQuickNotice(null), 5000);
      }
    } catch (err: any) {
      console.error('Upload failed:', err);
      setUploadError(err?.message || 'Failed to upload CSV dataset.');
      setQuickNotice(null);
    } finally {
      setIsUploading(false);
      e.target.value = '';
    }
  };

  // 1. Fetch Real Intelligence Report (contains executive summary, artifact counts, metrics, findings, recommendations)
  const {
    data: reportData,
    isLoading: isReportLoading,
    isError: isReportError,
    error: reportError,
    refetch: refetchReport,
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
    refetch: refetchHealth,
  } = useQuery<BusinessHealthResponse>({
    queryKey: queryKeys.reports.healthScore(activeDataset?.id || ''),
    queryFn: () => DecisionApi.getHealthScore(activeDataset!.id),
    enabled: !!activeDataset?.id && healthStatus === 'connected',
    staleTime: 0,
  });

  // Canonical Unified Intelligence payload is the Single Source of Truth
  const rawHealthScore = reportData?.executive_summary?.business_health_score ?? healthData?.score;
  const healthScore = rawHealthScore !== undefined && rawHealthScore !== null ? Math.round(rawHealthScore) : '--';
  const healthStatusStr = reportData?.executive_summary?.business_health_status ?? healthData?.status ?? 'NEUTRAL';

  const metricCount = reportData?.artifact_counts?.metrics ?? reportData?.metrics?.length ?? 0;
  const findingCount = reportData?.artifact_counts?.findings ?? reportData?.findings?.length ?? 0;
  const rootCauseCount = reportData?.artifact_counts?.root_causes ?? reportData?.root_causes?.length ?? 0;
  const recommendationCount = reportData?.artifact_counts?.recommendations ?? reportData?.recommendations?.length ?? 0;

  const primaryIssue = reportData?.executive_summary?.primary_issue || 'No Critical Issues Identified';
  const topRecommendation = reportData?.executive_summary?.top_recommendation || 'No Immediate Corrective Actions Prescribed';
  const primaryBusinessImpact = reportData?.findings?.[0]?.business_impact || (reportData?.executive_summary?.key_risks?.[0] ?? 'Operational telemetry within normal limits');
  const topBenefitImpact = (reportData?.recommendations?.[0] as any)?.expected_benefits?.primary_kpi_impact || 'Operational Stabilization';
  const financialImpact = reportData?.executive_summary?.expected_business_impact || '--';

  const recordCount = activeDataset ? ((activeDataset as any).record_count ?? activeDataset.row_count ?? '--') : '--';
  const columnCount = activeDataset ? ((activeDataset as any).column_count ?? activeDataset.columns?.length ?? '--') : '--';

  // Runtime Integrity Guard: declared unconditionally at top level
  React.useEffect(() => {
    if (typeof rawHealthScore === 'number' && rawHealthScore <= 60 && recommendationCount === 0) {
      console.warn(
        '[INTELLIGENCE_INTEGRITY] Critical logic contradiction: Health score <= 60 with 0 recommendations.',
        { rawHealthScore, recommendationCount, findingCount }
      );
    }
    if (healthStatusStr === 'CRITICAL' && financialImpact.toLowerCase().includes('stable')) {
      console.warn(
        '[INTELLIGENCE_INTEGRITY] Narrative contradiction: CRITICAL status narrative contains "stable".',
        { healthStatusStr, financialImpact }
      );
    }
  }, [rawHealthScore, recommendationCount, findingCount, healthStatusStr, financialImpact]);

  if (healthStatus === 'offline') {
    return <BackendOfflineScreen onRetry={checkHealth} />;
  }

  if (!activeDataset) {
    return (
      <div style={{ padding: '32px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <NoDatasetEmptyState
          title="No Active Dataset Selected"
          description="Select or upload an enterprise CSV dataset directly on this page to view autonomous decision intelligence, health score, and executive telemetry."
          actionText="Or Select Existing Dataset"
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
            padding: '10px 22px',
            borderRadius: '8px',
            fontSize: '13px',
            fontWeight: 800,
            cursor: isUploading ? 'not-allowed' : 'pointer',
            boxShadow: '0 0 20px rgba(255,255,255,0.2)',
          }}
        >
          {isUploading ? <RefreshCw size={14} className="animate-spin" /> : <Upload size={14} />}
          <span>{isUploading ? 'Ingesting Dataset...' : 'Upload CSV Dataset Directly'}</span>
          <input
            type="file"
            accept=".csv"
            style={{ display: 'none' }}
            onChange={handleFileUpload}
            disabled={isUploading}
          />
        </label>
      </div>
    );
  }

  const handleLoadDemoDataset = async () => {
    if (datasets.length > 0) {
      setActiveDataset(datasets[0]);
      setQuickNotice(`Loaded active dataset context: "${datasets[0].name}". Real intelligence pipeline engaged.`);
      await queryClient.invalidateQueries();
      setTimeout(() => setQuickNotice(null), 4000);
    }
  };

  const handleRefreshAll = async () => {
    setQuickNotice('Refreshing live intelligence telemetry...');
    await queryClient.invalidateQueries();
    if (activeDataset?.id) {
      await queryClient.refetchQueries({ queryKey: queryKeys.reports.executive(activeDataset.id) });
      await queryClient.refetchQueries({ queryKey: queryKeys.reports.healthScore(activeDataset.id) });
    }
    setTimeout(() => setQuickNotice(null), 3000);
  };

  const getHealthStatusColor = (status: string) => {
    switch (String(status).toUpperCase()) {
      case 'EXCELLENT':
        return { text: '#10B981', bg: 'rgba(16, 185, 129, 0.12)', border: 'rgba(16, 185, 129, 0.28)' };
      case 'HEALTHY':
        return { text: '#38BDF8', bg: 'rgba(56, 189, 248, 0.12)', border: 'rgba(56, 189, 248, 0.28)' };
      case 'WATCH_LIST':
        return { text: '#F59E0B', bg: 'rgba(245, 158, 11, 0.12)', border: 'rgba(245, 158, 11, 0.28)' };
      case 'AT_RISK':
        return { text: '#FB923C', bg: 'rgba(251, 146, 60, 0.12)', border: 'rgba(251, 146, 60, 0.28)' };
      case 'CRITICAL':
        return { text: '#EF4444', bg: 'rgba(239, 68, 68, 0.12)', border: 'rgba(239, 68, 68, 0.28)' };
      default:
        return { text: '#94A3B8', bg: 'rgba(148, 163, 184, 0.12)', border: 'rgba(148, 163, 184, 0.28)' };
    }
  };

  const statusColors = getHealthStatusColor(healthStatusStr);
  const isLoading = isReportLoading || isHealthLoading;
  const isError = isReportError || isHealthError;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', paddingBottom: '32px' }}>
      
      {/* 1. Header with Primary CTA Buttons */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '5px',
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              color: '#C5CCD6',
              borderRadius: '9999px',
              padding: '2px 10px',
              fontSize: '10px',
              fontWeight: 700,
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              marginBottom: '4px',
            }}
          >
            <Sparkles size={11} color="#10B981" />
            <span>EXECUTIVE INTELLIGENCE OPERATING SYSTEM (LIVE BACKEND API)</span>
          </div>
          <h1 style={{ fontSize: '1.4rem', fontWeight: 900, color: '#FFFFFF', margin: '0', letterSpacing: '-0.025em', lineHeight: 1.15 }}>
            Enterprise Decision Intelligence Command Center
          </h1>
          <p style={{ color: '#8E99A8', fontSize: '0.78rem', margin: '2px 0 0 0' }}>
            Autonomous business diagnosis, algorithmic root causes, prioritized initiatives, and deterministic health scoring.
          </p>
        </div>

        {/* Primary Action Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <button
            onClick={handleRefreshAll}
            style={{
              padding: '6px 12px',
              background: '#0D0F14',
              border: '1px solid #1E232B',
              borderRadius: '6px',
              color: '#CBD5E1',
              fontSize: '0.75rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
            }}
          >
            <RefreshCw size={12} />
            <span>Refresh Intelligence</span>
          </button>

          <button
            onClick={handleLoadDemoDataset}
            style={{
              padding: '6px 12px',
              background: '#0D0F14',
              border: '1px solid #1E232B',
              borderRadius: '6px',
              color: '#FFFFFF',
              fontSize: '0.75rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
            }}
          >
            <Sparkles size={12} color="#CBD5E1" />
            <span>Select Active Dataset</span>
          </button>

          <label
            style={{
              padding: '6px 14px',
              background: '#FFFFFF',
              border: '1px solid #FFFFFF',
              borderRadius: '6px',
              color: '#000000',
              fontSize: '0.75rem',
              fontWeight: 700,
              cursor: isUploading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              opacity: isUploading ? 0.7 : 1,
              transition: 'all 0.15s ease',
            }}
          >
            {isUploading ? <RefreshCw size={12} className="animate-spin" /> : <Upload size={12} />}
            <span>{isUploading ? 'Ingesting Dataset...' : 'Upload Enterprise Dataset'}</span>
            <input
              type="file"
              accept=".csv"
              style={{ display: 'none' }}
              onChange={handleFileUpload}
              disabled={isUploading}
            />
          </label>
        </div>
      </div>

      {/* Upload Error Banner */}
      {uploadError && (
        <div style={{ padding: '8px 12px', background: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.35)', borderRadius: '8px', color: '#EF4444', fontSize: '0.78rem', fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '6px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <AlertTriangle size={14} />
            <span>Upload Failed: {uploadError}</span>
          </div>
          <button
            onClick={() => setUploadError(null)}
            style={{ background: 'transparent', border: 'none', color: '#EF4444', cursor: 'pointer', fontSize: '0.75rem', fontWeight: 800 }}
          >
            ✕
          </button>
        </div>
      )}

      {/* Quick Notice Banner */}
      {quickNotice && (
        <div style={{ padding: '8px 12px', background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.35)', borderRadius: '8px', color: '#10B981', fontSize: '0.78rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
          <CheckCircle2 size={14} />
          <span>{quickNotice}</span>
        </div>
      )}

      {/* API Error State */}
      {isError && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '8px',
          padding: '12px 16px',
          color: '#EF4444',
          fontSize: '0.8rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertTriangle size={16} />
            <span>{(reportError as any)?.message || 'Failed to fetch Unified Intelligence telemetry from backend API.'}</span>
          </div>
          <button
            onClick={handleRefreshAll}
            style={{
              background: '#EF4444',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '4px',
              padding: '4px 10px',
              fontSize: '0.72rem',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            Retry API Request
          </button>
        </div>
      )}

      {/* 2. Boardroom 'What Changed?' Intelligence Diff Banner */}
      {!isLoading && !isError && (
        <div style={{ background: '#080A0E', border: '1px solid #161A22', borderRadius: '10px', padding: '10px 14px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '7px' }}>
            <Sparkles size={13} color="#38BDF8" />
            <span style={{ fontSize: '0.76rem', color: '#CBD5E1', fontWeight: 600 }}>
              Active Dataset: <strong style={{ color: '#FFFFFF' }}>{activeDataset.name}</strong> • Primary Issue: <strong style={{ color: '#F87171' }}>{primaryIssue}</strong> • Top Action: <strong style={{ color: '#10B981' }}>{topRecommendation}</strong>
            </span>
          </div>
          <span style={{ fontSize: '0.64rem', fontWeight: 700, padding: '2px 7px', borderRadius: '4px', background: statusColors.bg, color: statusColors.text, border: `1px solid ${statusColors.border}`, letterSpacing: '0.04em' }}>
            HEALTH STATUS: {healthStatusStr}
          </span>
        </div>
      )}

      {/* Loading Skeletons */}
      {isLoading && !isError && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: '10px' }}>
          {[1, 2, 3, 4].map((i) => (
            <div key={i} style={{ background: '#080A0E', border: '1px solid #161A22', borderRadius: '10px', height: '110px', animation: 'pulse 1.5s infinite' }} />
          ))}
        </div>
      )}

      {/* 3. Data-Aware Homepage Cards Row (4 Columns Single Row) */}
      {!isLoading && !isError && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: '10px' }}>
          
          {/* Card 1: Datasets Ingestion Status */}
          <div
            style={{
              background: '#080A0E',
              border: '1px solid #161A22',
              borderRadius: '10px',
              padding: '12px 14px',
              position: 'relative',
              boxShadow: '0 4px 14px rgba(0,0,0,0.4)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              gap: '6px',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.66rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                  ACTIVE DATASET
                </span>
                <Database size={13} color="#38BDF8" />
              </div>
              <div style={{ fontSize: '1.2rem', fontWeight: 900, color: '#FFFFFF', letterSpacing: '-0.02em', marginTop: '2px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {activeDataset.name}
              </div>
              <div style={{ fontSize: '0.70rem', color: '#8E99A8', marginTop: '1px' }}>
                <span style={{ color: '#10B981', fontWeight: 700 }}>{recordCount} Records</span> • <span>{columnCount} Columns</span>
              </div>
            </div>
            <Link
              to="/enterprise-data"
              style={{
                fontSize: '0.72rem',
                fontWeight: 700,
                color: '#E2E8F0',
                textDecoration: 'none',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                paddingTop: '6px',
                borderTop: '1px solid #14171E',
              }}
            >
              <span>Manage Datasets ({datasets.length})</span>
              <ArrowRight size={11} />
            </Link>
          </div>

          {/* Card 2: Business Health Score */}
          <div
            style={{
              background: '#080A0E',
              border: '1px solid #161A22',
              borderRadius: '10px',
              padding: '12px 14px',
              position: 'relative',
              boxShadow: '0 4px 14px rgba(0,0,0,0.4)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              gap: '6px',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.66rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                  BUSINESS HEALTH SCORE
                </span>
                <Activity size={13} color={statusColors.text} />
              </div>
              <div style={{ fontSize: '1.45rem', fontWeight: 900, color: '#FFFFFF', letterSpacing: '-0.02em', marginTop: '2px' }}>
                {healthScore} <span style={{ fontSize: '0.82rem', color: '#64748B' }}>/ 100</span>
              </div>
              <div style={{ fontSize: '0.70rem', color: '#8E99A8', marginTop: '1px' }}>
                <span style={{ color: statusColors.text, fontWeight: 700 }}>{healthStatusStr}</span> • Evaluated Deterministically
              </div>
            </div>
            <Link
              to="/kpis"
              style={{
                fontSize: '0.72rem',
                fontWeight: 700,
                color: '#E2E8F0',
                textDecoration: 'none',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                paddingTop: '6px',
                borderTop: '1px solid #14171E',
              }}
            >
              <span>View {metricCount} Calculated KPIs</span>
              <ArrowRight size={11} />
            </Link>
          </div>

          {/* Card 3: Diagnostic Findings & Root Causes */}
          <div
            style={{
              background: '#080A0E',
              border: '1px solid #161A22',
              borderRadius: '10px',
              padding: '12px 14px',
              position: 'relative',
              boxShadow: '0 4px 14px rgba(0,0,0,0.4)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              gap: '6px',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.66rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                  DIAGNOSTICS & ROOT CAUSES
                </span>
                <AlertTriangle size={13} color="#F59E0B" />
              </div>
              <div style={{ fontSize: '1.45rem', fontWeight: 900, color: '#F59E0B', letterSpacing: '-0.02em', marginTop: '2px' }}>
                {findingCount} Findings
              </div>
              <div style={{ fontSize: '0.70rem', color: '#8E99A8', marginTop: '1px' }}>
                {rootCauseCount} Causal Edges Isolated
              </div>
            </div>
            <Link
              to="/diagnostics"
              style={{
                fontSize: '0.72rem',
                fontWeight: 700,
                color: '#E2E8F0',
                textDecoration: 'none',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                paddingTop: '6px',
                borderTop: '1px solid #14171E',
              }}
            >
              <span>Inspect Findings & Root Causes</span>
              <ArrowRight size={11} />
            </Link>
          </div>

          {/* Card 4: Prescribed Recommendations */}
          <div
            style={{
              background: '#080A0E',
              border: '1px solid #161A22',
              borderRadius: '10px',
              padding: '12px 14px',
              position: 'relative',
              boxShadow: '0 4px 14px rgba(0,0,0,0.4)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              gap: '6px',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.66rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                  PRESCRIBED ACTIONS
                </span>
                <Zap size={13} color="#10B981" />
              </div>
              <div style={{ fontSize: '1.45rem', fontWeight: 900, color: '#FFFFFF', letterSpacing: '-0.02em', marginTop: '2px' }}>
                {recommendationCount} {recommendationCount === 1 ? 'Action' : 'Actions'}
              </div>
              <div style={{ fontSize: '0.70rem', color: '#8E99A8', marginTop: '1px' }}>
                {recommendationCount > 0 ? (
                  <>Target: <span style={{ color: '#10B981', fontWeight: 700 }}>{topBenefitImpact}</span></>
                ) : (
                  <>Target: <span style={{ color: '#64748B', fontWeight: 700 }}>—</span></>
                )}
              </div>
            </div>
            <Link
              to="/recommendations"
              style={{
                fontSize: '0.72rem',
                fontWeight: 700,
                color: '#E2E8F0',
                textDecoration: 'none',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                paddingTop: '6px',
                borderTop: '1px solid #14171E',
              }}
            >
              <span>View Prescribed Action Roadmap</span>
              <ArrowRight size={11} />
            </Link>
          </div>

        </div>
      )}

      {/* 4. Multi-Quarter Scorecard & Telemetry Breakdown */}
      {!isLoading && !isError && (
        <div style={{ background: '#080A0E', border: '1px solid #161A22', borderRadius: '10px', padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <span style={{ fontSize: '0.94rem', fontWeight: 800, color: '#FFFFFF' }}>Unified Intelligence Executive Summary</span>
              <span style={{ fontSize: '0.72rem', color: '#64748B', display: 'block' }}>Dataset-Specific Autonomous Analysis Handoff</span>
            </div>
            <span style={{ fontSize: '0.66rem', fontWeight: 700, padding: '3px 8px', borderRadius: '4px', background: 'rgba(56, 189, 248, 0.12)', color: '#38BDF8', border: '1px solid rgba(56, 189, 248, 0.28)', letterSpacing: '0.04em' }}>
              VERIFIED PIPELINE ENGINE
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '16px' }}>
            <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '14px' }}>
              <div style={{ fontSize: '0.70rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>
                PRIMARY BUSINESS ISSUE
              </div>
              <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#F87171', marginBottom: '6px' }}>
                {primaryIssue}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#94A3B8', lineHeight: 1.5 }}>
                Business Impact: <strong style={{ color: '#F87171' }}>{primaryBusinessImpact}</strong>
              </div>
            </div>

            <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '14px' }}>
              <div style={{ fontSize: '0.70rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>
                TOP PRESCRIBED ACTION
              </div>
              <div style={{ fontSize: '0.95rem', fontWeight: 800, color: recommendationCount > 0 ? '#10B981' : '#94A3B8', marginBottom: '6px' }}>
                {recommendationCount > 0 ? topRecommendation : 'No Prescribed Actions Available'}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#CBD5E1', lineHeight: 1.5 }}>
                Strategic Guidance: {financialImpact}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 5. Live Activity Feed */}
      <ActivityFeed />

    </div>
  );
};

export default EnterpriseCommandCenterView;
