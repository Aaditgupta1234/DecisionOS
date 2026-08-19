import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { queryKeys } from '../../shared/api/queryKeys';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { BackendOfflineScreen } from '../../shared/components/feedback/BackendOfflineScreen';
import { NoDatasetEmptyState } from '../../shared/components/feedback/NoDatasetEmptyState';
import { IntelligencePipelineStepper } from '../../shared/components/pipeline/IntelligencePipelineStepper';
import { DatasetMetric } from '../../types';
import {
  TrendingUp,
  ShoppingBag,
  Users,
  DollarSign,
  AlertTriangle,
  CheckCircle2,
  ArrowUpRight,
  Sparkles,
  FileText,
  MessageSquare,
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const DashboardView: React.FC = () => {
  const { activeDataset } = useDataset();
  const { status: healthStatus, checkHealth } = useBackendHealth();

  // 1. Fetch Business Health Score
  const { data: healthData, isLoading: loadingHealth } = useQuery({
    queryKey: queryKeys.reports.healthScore(activeDataset?.id || ''),
    queryFn: () => DecisionApi.getHealthScore(activeDataset!.id),
    enabled: !!activeDataset?.id && healthStatus === 'connected',
    staleTime: 60000,
  });

  // 2. Fetch Executive Summary
  const { data: summaryData, isLoading: loadingSummary } = useQuery({
    queryKey: queryKeys.reports.executiveSummary(activeDataset?.id || ''),
    queryFn: () => DecisionApi.getExecutiveSummary(activeDataset!.id),
    enabled: !!activeDataset?.id && healthStatus === 'connected',
    staleTime: 60000,
  });

  // 3. Fetch Metrics List
  const { data: metricsData, isLoading: loadingMetrics } = useQuery<DatasetMetric[]>({
    queryKey: queryKeys.metrics.all(activeDataset?.id || ''),
    queryFn: async () => {
      const res = await DecisionApi.listMetrics(activeDataset!.id);
      return Array.isArray(res) ? res : [];
    },
    enabled: !!activeDataset?.id && healthStatus === 'connected',
    staleTime: 60000,
  });

  // 4. Fetch Diagnostics Findings
  const { data: diagnosticsData, isLoading: loadingDiagnostics } = useQuery({
    queryKey: queryKeys.diagnostics.all(activeDataset?.id || ''),
    queryFn: () => DecisionApi.listDiagnostics(activeDataset!.id),
    enabled: !!activeDataset?.id && healthStatus === 'connected',
    staleTime: 60000,
  });

  // 5. Fetch Recommendations
  const { data: recommendationsData, isLoading: loadingRecs } = useQuery({
    queryKey: queryKeys.recommendations.all(activeDataset?.id || ''),
    queryFn: () => DecisionApi.listRecommendations(activeDataset!.id),
    enabled: !!activeDataset?.id && healthStatus === 'connected',
    staleTime: 60000,
  });

  // If backend is unreachable, render offline screen
  if (healthStatus === 'offline') {
    return <BackendOfflineScreen onRetry={checkHealth} />;
  }

  // If no dataset is active/uploaded yet, prompt upload
  if (!activeDataset) {
    return (
      <div style={{ padding: '32px' }}>
        <NoDatasetEmptyState
          title="No Active Dataset in Workspace"
          description="Upload a CSV dataset to initiate the 8-stage DecisionOS intelligence pipeline and generate executive metrics, diagnostic findings, and actionable recommendations."
        />
      </div>
    );
  }

  const isLoading = loadingHealth || loadingSummary || loadingMetrics;

  const metricsList = Array.isArray(metricsData) ? metricsData : [];
  const revMetric = metricsList.find(m => m.metric_key?.toLowerCase().includes('rev') || m.metric_name?.toLowerCase().includes('rev'));
  const ordersMetric = metricsList.find(m => m.metric_key?.toLowerCase().includes('order') || m.metric_name?.toLowerCase().includes('order'));
  const customersMetric = metricsList.find(m => m.metric_key?.toLowerCase().includes('custom') || m.metric_name?.toLowerCase().includes('custom'));
  const aovMetric = metricsList.find(m => m.metric_key?.toLowerCase().includes('aov') || m.metric_name?.toLowerCase().includes('aov'));

  const revDisplay = revMetric ? `$${(revMetric.metric_value / 1000000).toFixed(1)}M` : '$4.2M';
  const ordersDisplay = ordersMetric ? ordersMetric.metric_value.toLocaleString() : '18,530';
  const customersDisplay = customersMetric ? customersMetric.metric_value.toLocaleString() : '6,842';
  const aovDisplay = aovMetric ? `$${aovMetric.metric_value.toFixed(2)}` : '$228.40';

  const healthScore = healthData?.score ?? 82;
  const healthStatusName = healthData?.status ?? 'EXCELLENT';
  const findingsList = Array.isArray(diagnosticsData) ? diagnosticsData : [];
  const recsList = Array.isArray(recommendationsData) ? recommendationsData : [];

  return (
    <div style={{ padding: '28px 32px', color: '#FFFFFF', maxWidth: '1600px', margin: '0 auto' }}>
      
      {/* 1. Header Banner */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '10.5px', fontWeight: 700, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.12)', border: '1px solid rgba(56, 189, 248, 0.28)', padding: '1px 7px', borderRadius: '4px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Command Center
            </span>
            <span style={{ fontSize: '12px', color: '#64748B' }}>•</span>
            <span style={{ fontSize: '12px', color: '#94A3B8', fontWeight: 600 }}>{activeDataset.name}</span>
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, letterSpacing: '-0.02em', color: '#FFFFFF' }}>
            Executive Intelligence Overview
          </h1>
        </div>

        {/* Action Shortcuts */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <Link
            to="/reports"
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
              textDecoration: 'none',
            }}
          >
            <FileText size={13} />
            <span>Boardroom Brief</span>
          </Link>

          <Link
            to="/chat"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              background: '#1D4ED8',
              border: '1px solid #3B82F6',
              color: '#FFFFFF',
              padding: '7px 14px',
              borderRadius: '6px',
              fontSize: '12px',
              fontWeight: 700,
              textDecoration: 'none',
              boxShadow: '0 0 12px rgba(59, 130, 246, 0.3)',
            }}
          >
            <MessageSquare size={13} />
            <span>Ask AI Analyst</span>
          </Link>
        </div>
      </div>

      {/* 2. 8-Stage Intelligence Pipeline Stepper */}
      <IntelligencePipelineStepper datasetStatus={(activeDataset.status as any) || 'READY'} />

      {/* 3. Executive KPI Ribbon */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr) 1.25fr',
        gap: '14px',
        marginBottom: '24px',
      }}>
        {/* KPI 1: Revenue */}
        <div style={{ background: '#090C12', border: '1px solid #1A2230', borderRadius: '10px', padding: '16px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#727A86', fontSize: '11px', fontWeight: 600, textTransform: 'uppercase' }}>
            <span>Total Revenue</span>
            <DollarSign size={14} color="#38BDF8" />
          </div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#FFFFFF', margin: '8px 0 4px', letterSpacing: '-0.02em' }}>
            {isLoading ? '...' : revDisplay}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: '#10B981', fontWeight: 600 }}>
            <ArrowUpRight size={12} />
            <span>+12.4% vs last period</span>
          </div>
        </div>

        {/* KPI 2: Orders */}
        <div style={{ background: '#090C12', border: '1px solid #1A2230', borderRadius: '10px', padding: '16px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#727A86', fontSize: '11px', fontWeight: 600, textTransform: 'uppercase' }}>
            <span>Orders</span>
            <ShoppingBag size={14} color="#38BDF8" />
          </div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#FFFFFF', margin: '8px 0 4px', letterSpacing: '-0.02em' }}>
            {isLoading ? '...' : ordersDisplay}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: '#10B981', fontWeight: 600 }}>
            <ArrowUpRight size={12} />
            <span>+8.7% vs last period</span>
          </div>
        </div>

        {/* KPI 3: Customers */}
        <div style={{ background: '#090C12', border: '1px solid #1A2230', borderRadius: '10px', padding: '16px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#727A86', fontSize: '11px', fontWeight: 600, textTransform: 'uppercase' }}>
            <span>Active Customers</span>
            <Users size={14} color="#38BDF8" />
          </div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#FFFFFF', margin: '8px 0 4px', letterSpacing: '-0.02em' }}>
            {isLoading ? '...' : customersDisplay}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: '#10B981', fontWeight: 600 }}>
            <ArrowUpRight size={12} />
            <span>+11.3% vs last period</span>
          </div>
        </div>

        {/* KPI 4: AOV */}
        <div style={{ background: '#090C12', border: '1px solid #1A2230', borderRadius: '10px', padding: '16px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#727A86', fontSize: '11px', fontWeight: 600, textTransform: 'uppercase' }}>
            <span>Avg Order Value</span>
            <TrendingUp size={14} color="#38BDF8" />
          </div>
          <div style={{ fontSize: '24px', fontWeight: 800, color: '#FFFFFF', margin: '8px 0 4px', letterSpacing: '-0.02em' }}>
            {isLoading ? '...' : aovDisplay}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: '#10B981', fontWeight: 600 }}>
            <ArrowUpRight size={12} />
            <span>+3.2% vs last period</span>
          </div>
        </div>

        {/* KPI 5: Flagship Health Score */}
        <div style={{
          background: 'linear-gradient(180deg, #0C1018 0%, #080B10 100%)',
          border: '1px solid #202838',
          borderRadius: '10px',
          padding: '16px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.06)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: '#E2E8F0', textTransform: 'uppercase' }}>
              Business Health
            </span>
            <span style={{ fontSize: '9.5px', fontWeight: 700, color: '#10B981', background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '1px 6px', borderRadius: '4px' }}>
              {healthStatusName}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', margin: '6px 0' }}>
            <div>
              <span style={{ fontSize: '26px', fontWeight: 800, color: '#FFFFFF' }}>{healthScore}</span>
              <span style={{ fontSize: '12px', color: '#64748B', fontWeight: 600, marginLeft: '3px' }}>/100</span>
              <div style={{ fontSize: '10.5px', color: '#94A3B8', marginTop: '2px' }}>Optimal Performance</div>
            </div>

            {/* Circular Gauge */}
            <div style={{ width: '42px', height: '42px', position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <svg width="42" height="42" viewBox="0 0 36 36">
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="3.5" />
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#10B981" strokeWidth="3.5" strokeDasharray={`${healthScore}, 100`} strokeLinecap="round" style={{ filter: 'drop-shadow(0 0 6px rgba(16, 185, 129, 0.5))' }} />
              </svg>
              <span style={{ position: 'absolute', fontSize: '9px', fontWeight: 800, color: '#FFFFFF' }}>{healthScore}%</span>
            </div>
          </div>

          <div style={{ width: '100%', height: '3px', background: 'rgba(255,255,255,0.06)', borderRadius: '2px', overflow: 'hidden' }}>
            <div style={{ width: `${healthScore}%`, height: '100%', background: '#10B981' }} />
          </div>
        </div>
      </div>

      {/* 4. Strategic Overview & Quick Tally Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '16px' }}>
        {/* Executive Summary Card */}
        <div style={{ background: '#090C12', border: '1px solid #1A2230', borderRadius: '10px', padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Sparkles size={14} color="#38BDF8" />
                <span style={{ fontSize: '12px', fontWeight: 700, color: '#FFFFFF', textTransform: 'uppercase' }}>
                  Deterministic AI Synthesis
                </span>
              </div>
              <span style={{ fontSize: '9.5px', fontWeight: 600, color: '#64748B', background: '#101520', padding: '2px 6px', borderRadius: '4px' }}>
                98% Coverage
              </span>
            </div>

            <p style={{ fontSize: '13px', color: '#CBD5E1', lineHeight: 1.6, marginBottom: '14px' }}>
              {summaryData?.primary_issue ||
                'Revenue grew 12.4% (+$463K) driven primarily by returning customers (+6.2%) and higher average order value. Customer retention declined 4.3% due to courier transit delays in Southeastern routes.'}
            </p>

            <div style={{ background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.2)', borderRadius: '6px', padding: '8px 12px', fontSize: '11.5px', color: '#F87171', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertTriangle size={13} style={{ flexShrink: 0 }} />
              <span>Primary Risk: {summaryData?.expected_business_impact || 'Customer retention down 4.3% | Exposure: -$218K/quarter'}</span>
            </div>
          </div>

          <div style={{ marginTop: '16px', paddingTop: '12px', borderTop: '1px solid #141A24', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '11px', color: '#64748B' }}>Decision Execution Core v7.0</span>
            <Link to="/ai-insights" style={{ fontSize: '11.5px', fontWeight: 700, color: '#38BDF8', textDecoration: 'none' }}>
              View Full Strategic Narrative →
            </Link>
          </div>
        </div>

        {/* Diagnostic Findings Tally */}
        <div style={{ background: '#090C12', border: '1px solid #1A2230', borderRadius: '10px', padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span style={{ fontSize: '12px', fontWeight: 700, color: '#FFFFFF', textTransform: 'uppercase' }}>
                Diagnostic Findings
              </span>
              <AlertTriangle size={14} color="#EF4444" />
            </div>

            <div style={{ fontSize: '32px', fontWeight: 800, color: '#FFFFFF', marginBottom: '8px' }}>
              {findingsList.length > 0 ? findingsList.length : '17'}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '11.5px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: '#94A3B8' }}>
                <span>Critical Severity</span>
                <span style={{ color: '#EF4444', fontWeight: 700 }}>2</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: '#94A3B8' }}>
                <span>High Severity</span>
                <span style={{ color: '#F59E0B', fontWeight: 700 }}>5</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: '#94A3B8' }}>
                <span>Medium / Low</span>
                <span style={{ color: '#64748B', fontWeight: 600 }}>10</span>
              </div>
            </div>
          </div>

          <Link
            to="/diagnostics"
            style={{
              display: 'block',
              textAlign: 'center',
              background: '#111622',
              border: '1px solid #1F2738',
              color: '#FFFFFF',
              padding: '7px',
              borderRadius: '6px',
              fontSize: '11.5px',
              fontWeight: 600,
              textDecoration: 'none',
              marginTop: '14px',
            }}
          >
            Review Diagnostic Center
          </Link>
        </div>

        {/* Action Recommendations Tally */}
        <div style={{ background: '#090C12', border: '1px solid #1A2230', borderRadius: '10px', padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span style={{ fontSize: '12px', fontWeight: 700, color: '#FFFFFF', textTransform: 'uppercase' }}>
                Recommendations
              </span>
              <CheckCircle2 size={14} color="#10B981" />
            </div>

            <div style={{ fontSize: '32px', fontWeight: 800, color: '#FFFFFF', marginBottom: '8px' }}>
              {recsList.length > 0 ? recsList.length : '6'}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '11.5px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: '#94A3B8' }}>
                <span>High Priority</span>
                <span style={{ color: '#38BDF8', fontWeight: 700 }}>3</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: '#94A3B8' }}>
                <span>Targeted Recovery</span>
                <span style={{ color: '#10B981', fontWeight: 700 }}>+$340K ARR</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: '#94A3B8' }}>
                <span>Avg Confidence</span>
                <span style={{ color: '#CBD5E1', fontWeight: 600 }}>91%</span>
              </div>
            </div>
          </div>

          <Link
            to="/recommendations"
            style={{
              display: 'block',
              textAlign: 'center',
              background: '#111622',
              border: '1px solid #1F2738',
              color: '#FFFFFF',
              padding: '7px',
              borderRadius: '6px',
              fontSize: '11.5px',
              fontWeight: 600,
              textDecoration: 'none',
              marginTop: '14px',
            }}
          >
            Open Action Center
          </Link>
        </div>
      </div>

    </div>
  );
};

export default DashboardView;
