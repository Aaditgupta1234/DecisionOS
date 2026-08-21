import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
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
  const { datasets, activeDataset, setActiveDataset } = useDataset();
  const { status: healthStatus, checkHealth } = useBackendHealth();
  const [quickNotice, setQuickNotice] = useState<string | null>(null);

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
    staleTime: 60000,
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
    staleTime: 60000,
  });

  if (healthStatus === 'offline') {
    return <BackendOfflineScreen onRetry={checkHealth} />;
  }

  if (!activeDataset) {
    return (
      <div style={{ padding: '32px' }}>
        <NoDatasetEmptyState
          title="No Active Dataset Selected"
          description="Select or upload an enterprise dataset to view autonomous decision intelligence, health score, and executive telemetry."
        />
      </div>
    );
  }

  const handleLoadDemoDataset = () => {
    if (datasets.length > 0) {
      setActiveDataset(datasets[0]);
      setQuickNotice(`Loaded active dataset context: "${datasets[0].name}". Real intelligence pipeline engaged.`);
      setTimeout(() => setQuickNotice(null), 4000);
    }
  };

  const handleRefreshAll = () => {
    refetchReport();
    refetchHealth();
  };

  // Derive Real Values from Backend APIs (No Hardcoded Fallbacks)
  const rawHealthScore = healthData?.score ?? reportData?.executive_summary?.business_health_score;
  const healthScore = rawHealthScore !== undefined && rawHealthScore !== null ? Math.round(rawHealthScore) : '--';
  const healthStatusStr = healthData?.status ?? reportData?.executive_summary?.business_health_status ?? 'NEUTRAL';
  
  const metricCount = reportData?.artifact_counts?.metrics ?? reportData?.metrics?.length ?? 0;
  const findingCount = reportData?.artifact_counts?.findings ?? reportData?.findings?.length ?? 0;
  const rootCauseCount = reportData?.artifact_counts?.root_causes ?? reportData?.root_causes?.length ?? 0;
  const recommendationCount = reportData?.artifact_counts?.recommendations ?? reportData?.recommendations?.length ?? 0;

  const primaryIssue = reportData?.executive_summary?.primary_issue || 'No Critical Issues Identified';
  const topRecommendation = reportData?.executive_summary?.top_recommendation || 'No Immediate Corrective Actions Prescribed';
  const financialImpact = reportData?.executive_summary?.expected_business_impact || '--';

  const recordCount = (activeDataset as any).record_count ?? activeDataset.row_count ?? '--';
  const columnCount = (activeDataset as any).column_count ?? activeDataset.columns?.length ?? '--';

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
            Autonomous deterministic intelligence, dataset telemetry ingestion, and boardroom scenario control.
          </p>
        </div>

        {/* Primary Action Buttons */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'nowrap', flexShrink: 0 }}>
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

          <Link
            to="/enterprise-data"
            style={{
              padding: '6px 14px',
              background: '#FFFFFF',
              border: '1px solid #FFFFFF',
              borderRadius: '6px',
              color: '#000000',
              fontSize: '0.75rem',
              fontWeight: 700,
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
            }}
          >
            <Upload size={12} />
            <span>Upload Enterprise Dataset</span>
          </Link>
        </div>
      </div>

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
          <span style={{ fontSize: '0.64rem', fontWeight: 700, padding: '2px 7px', borderRadius: '4px', background: 'rgba(16, 185, 129, 0.12)', color: '#10B981', border: '1px solid rgba(16, 185, 129, 0.28)', letterSpacing: '0.04em' }}>
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
                <Activity size={13} color="#10B981" />
              </div>
              <div style={{ fontSize: '1.45rem', fontWeight: 900, color: '#FFFFFF', letterSpacing: '-0.02em', marginTop: '2px' }}>
                {healthScore} <span style={{ fontSize: '0.82rem', color: '#64748B' }}>/ 100</span>
              </div>
              <div style={{ fontSize: '0.70rem', color: '#8E99A8', marginTop: '1px' }}>
                <span style={{ color: '#10B981', fontWeight: 700 }}>{healthStatusStr}</span> • Evaluated Deterministically
              </div>
            </div>
            <Link
              to="/portfolio"
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
                {recommendationCount} Actions
              </div>
              <div style={{ fontSize: '0.70rem', color: '#8E99A8', marginTop: '1px' }}>
                Impact: <span style={{ color: '#F87171', fontWeight: 700 }}>{financialImpact}</span>
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
                Estimated Financial Impact: <strong style={{ color: '#EF4444' }}>{financialImpact}</strong>. Identified through rule-based evaluation of consecutive revenue decline periods.
              </div>
            </div>

            <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '14px' }}>
              <div style={{ fontSize: '0.70rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase', marginBottom: '4px' }}>
                TOP PRESCRIBED ACTION
              </div>
              <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#10B981', marginBottom: '6px' }}>
                {topRecommendation}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#94A3B8', lineHeight: 1.5 }}>
                Actionable intervention targeted at reversing negative revenue trajectory and reducing magnitude of contraction.
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
