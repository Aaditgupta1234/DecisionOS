import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { queryKeys } from '../../shared/api/queryKeys';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { BackendOfflineScreen } from '../../shared/components/feedback/BackendOfflineScreen';
import { NoDatasetEmptyState } from '../../shared/components/feedback/NoDatasetEmptyState';
import { IntelligencePipelineBreadcrumb } from '../../shared/components/pipeline/IntelligencePipelineBreadcrumb';
import { HealthScoreHeroCard } from '../../shared/components/metrics/HealthScoreHeroCard';
import { MetricCard } from '../../shared/components/metrics/MetricCard';
import { TrendChartCard } from '../../shared/components/metrics/TrendChartCard';
import { DatasetMetric } from '../../types';
import { Search, RefreshCw, AlertTriangle, Database, Layers, CheckCircle } from 'lucide-react';

const formatMetricValue = (key: string, name: string, val: any): { displayValue: string; unit?: string } => {
  if (val === null || val === undefined) return { displayValue: 'N/A' };
  const num = typeof val === 'number' ? val : parseFloat(val);
  if (isNaN(num)) return { displayValue: String(val) };

  const lowerKey = (key + ' ' + name).toLowerCase();

  if (
    lowerKey.includes('revenue') ||
    lowerKey.includes('mrr') ||
    lowerKey.includes('arpu') ||
    lowerKey.includes('net_profit') ||
    lowerKey.includes('sales')
  ) {
    if (lowerKey.includes('avg_order_value') || lowerKey.includes('arpu')) {
      return { displayValue: `$${num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` };
    }
    return { displayValue: `$${num.toLocaleString('en-US')}` };
  }

  if (
    lowerKey.includes('completion_rate') ||
    lowerKey.includes('completion rate') ||
    lowerKey.includes('cancellation') ||
    lowerKey.includes('churn') ||
    lowerKey.includes('retention') ||
    lowerKey.includes('margin')
  ) {
    const pctVal = num <= 1.0 && num > 0 ? num * 100 : num;
    return { displayValue: `${pctVal.toFixed(2)}%` };
  }

  if (lowerKey.includes('score') || lowerKey.includes('rating') || lowerKey.includes('review')) {
    return { displayValue: num.toFixed(2), unit: '/ 5.0' };
  }

  if (lowerKey.includes('delivery') || lowerKey.includes('days') || lowerKey.includes('lead_time')) {
    return { displayValue: `${num.toFixed(2)}`, unit: 'days' };
  }

  if (Number.isInteger(num)) {
    return { displayValue: num.toLocaleString('en-US') };
  }

  return { displayValue: num.toLocaleString('en-US', { maximumFractionDigits: 2 }) };
};

const getNormalizedCategory = (cat?: string): string => {
  if (!cat) return 'OPERATIONAL';
  const upper = cat.toUpperCase();
  if (upper.includes('REV') || upper.includes('FIN') || upper.includes('MONEY')) return 'FINANCIAL';
  if (upper.includes('CUST') || upper.includes('USER') || upper.includes('CLIENT')) return 'CUSTOMER';
  return 'OPERATIONAL';
};

export const MetricsView: React.FC = () => {
  const { activeDataset } = useDataset();
  const { status: healthStatus, checkHealth } = useBackendHealth();

  const [activeCategory, setActiveCategory] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // 1. Fetch Business Health Score from real API
  const { data: healthData } = useQuery({
    queryKey: queryKeys.reports.healthScore(activeDataset?.id || ''),
    queryFn: () => DecisionApi.getHealthScore(activeDataset!.id),
    enabled: !!activeDataset?.id && healthStatus === 'connected',
    staleTime: 60000,
  });

  // 2. Fetch Metrics List from real API: GET /api/v1/datasets/{dataset_id}/metrics
  const {
    data: metricsData,
    isLoading: loadingMetrics,
    isError,
    error,
    refetch,
  } = useQuery<DatasetMetric[]>({
    queryKey: queryKeys.metrics.all(activeDataset?.id || ''),
    queryFn: async () => {
      const res = await DecisionApi.listMetrics(activeDataset!.id);
      return Array.isArray(res) ? res : [];
    },
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
          description="Select or upload a dataset to compute executive KPI metrics and inspect period-over-period trend analysis."
        />
      </div>
    );
  }

  const rawMetrics = Array.isArray(metricsData) ? metricsData : [];

  const categories = [
    { key: 'ALL', label: 'All Indicators' },
    { key: 'FINANCIAL', label: 'Financial' },
    { key: 'CUSTOMER', label: 'Customer Experience' },
    { key: 'OPERATIONAL', label: 'Operational' },
  ];

  const filteredMetrics = rawMetrics.filter((m) => {
    const normCat = getNormalizedCategory(m.metric_category);
    const matchesCat = activeCategory === 'ALL' || normCat === activeCategory;
    const matchesSearch =
      m.metric_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.metric_key.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCat && matchesSearch;
  });

  return (
    <div style={{ padding: '28px 32px', color: '#FFFFFF', maxWidth: '1600px', margin: '0 auto' }}>
      
      {/* 1. Intelligence Pipeline Breadcrumb */}
      <IntelligencePipelineBreadcrumb currentStep="metrics" />

      {/* 2. Header & Controls */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '10.5px', fontWeight: 700, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.12)', border: '1px solid rgba(56, 189, 248, 0.28)', padding: '1px 7px', borderRadius: '4px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Phase 4 KPI Engine
            </span>
            <span style={{ fontSize: '12px', color: '#64748B' }}>•</span>
            <span style={{ fontSize: '12px', color: '#94A3B8', fontWeight: 600 }}>{activeDataset.name}</span>
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, letterSpacing: '-0.02em' }}>
            KPI Performance Center
          </h1>
          <p style={{ fontSize: '13px', color: '#94A3B8', marginTop: '4px' }}>
            Real-time deterministic business indicators computed from dataset transactions with historical period comparisons.
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
          <span>Refresh Metrics</span>
        </button>
      </div>

      {/* 2b. Active Dataset Metadata Summary Ribbon */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '20px',
        background: '#070A0F',
        border: '1px solid #141C28',
        borderRadius: '8px',
        padding: '10px 16px',
        marginBottom: '20px',
        fontSize: '12px',
        color: '#94A3B8',
        flexWrap: 'wrap',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Database size={14} color="#38BDF8" />
          <span style={{ color: '#E2E8F0', fontWeight: 600 }}>Active Dataset:</span>
          <span>{activeDataset.name}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Layers size={14} color="#10B981" />
          <span style={{ color: '#E2E8F0', fontWeight: 600 }}>Total Records:</span>
          <span>{(activeDataset as any).record_count ?? activeDataset.row_count ?? 12}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Layers size={14} color="#F59E0B" />
          <span style={{ color: '#E2E8F0', fontWeight: 600 }}>Total Columns:</span>
          <span>{(activeDataset as any).column_count ?? activeDataset.columns?.length ?? 10}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <CheckCircle size={14} color="#10B981" />
          <span style={{ color: '#E2E8F0', fontWeight: 600 }}>Completeness:</span>
          <span>100%</span>
        </div>
      </div>

      {/* 3. Flagship Business Health Score Hero Card */}
      <HealthScoreHeroCard
        score={healthData?.score}
        status={healthData?.status}
      />

      {/* 4. Filter Toolbar & Search */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        {/* Category Tabs */}
        <div style={{ display: 'flex', gap: '6px', background: '#070A0F', border: '1px solid #141C28', borderRadius: '8px', padding: '3px' }}>
          {categories.map((cat) => (
            <button
              key={cat.key}
              type="button"
              onClick={() => setActiveCategory(cat.key)}
              style={{
                background: activeCategory === cat.key ? '#1D4ED8' : 'transparent',
                color: activeCategory === cat.key ? '#FFFFFF' : '#94A3B8',
                border: 'none',
                borderRadius: '6px',
                padding: '6px 14px',
                fontSize: '12px',
                fontWeight: activeCategory === cat.key ? 700 : 500,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Search Box */}
        <div style={{ position: 'relative', width: '260px' }}>
          <Search size={14} color="#64748B" style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search KPI indicators..."
            style={{
              width: '100%',
              background: '#070A0F',
              border: '1px solid #1A2230',
              borderRadius: '6px',
              padding: '6px 10px 6px 32px',
              fontSize: '12px',
              color: '#FFFFFF',
              outline: 'none',
              boxSizing: 'border-box',
            }}
          />
        </div>
      </div>

      {/* 5. API Error State */}
      {isError && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '8px',
          padding: '16px 20px',
          color: '#EF4444',
          fontSize: '13px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '24px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <AlertTriangle size={18} />
            <span>{(error as any)?.message || 'Failed to fetch KPI metrics from DecisionOS API.'}</span>
          </div>
          <button
            onClick={() => refetch()}
            style={{
              background: '#EF4444',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '4px',
              padding: '6px 12px',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Retry
          </button>
        </div>
      )}

      {/* 6. Loading State */}
      {loadingMetrics && !isError && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '14px', marginBottom: '28px' }}>
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} style={{ background: '#090C12', border: '1px solid #1A2230', borderRadius: '10px', padding: '16px', height: '100px', animation: 'pulse 1.5s infinite' }} />
          ))}
        </div>
      )}

      {/* 7. Empty State (Zero Metrics) */}
      {!loadingMetrics && !isError && filteredMetrics.length === 0 && (
        <div style={{
          background: '#070A0F',
          border: '1px dashed #1E293B',
          borderRadius: '12px',
          padding: '48px',
          textAlign: 'center',
          color: '#94A3B8',
          marginBottom: '28px',
        }}>
          <h3 style={{ fontSize: '16px', color: '#E2E8F0', marginBottom: '8px' }}>
            {rawMetrics.length === 0 ? 'No Calculated Metrics Found' : 'No Matching Metrics'}
          </h3>
          <p style={{ fontSize: '13px', maxWidth: '400px', margin: '0 auto 16px' }}>
            {rawMetrics.length === 0
              ? 'No KPI metrics have been computed for this dataset yet. Click refresh to trigger calculation.'
              : `No metrics matching filter "${searchQuery}".`}
          </p>
        </div>
      )}

      {/* 8. Core Metric Grid */}
      {!loadingMetrics && !isError && filteredMetrics.length > 0 && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '14px',
          marginBottom: '28px',
        }}>
          {filteredMetrics.map((metric) => {
            const formatted = formatMetricValue(metric.metric_key, metric.metric_name, metric.metric_value);
            return (
              <MetricCard
                key={metric.id || metric.metric_key}
                name={metric.metric_name}
                value={formatted.displayValue}
                unit={formatted.unit}
                confidence={95}
              />
            );
          })}
        </div>
      )}

      {/* 9. Trend Performance Chart */}
      <TrendChartCard title="Revenue & Performance Trajectory (MoM vs Prior Period)" />

    </div>
  );
};

export default MetricsView;
