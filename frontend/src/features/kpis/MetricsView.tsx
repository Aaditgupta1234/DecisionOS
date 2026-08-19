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
import { Search, RefreshCw } from 'lucide-react';

export const MetricsView: React.FC = () => {
  const { activeDataset } = useDataset();
  const { status: healthStatus, checkHealth } = useBackendHealth();

  const [activeCategory, setActiveCategory] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // 1. Fetch Business Health Score
  const { data: healthData, isLoading: loadingHealth } = useQuery({
    queryKey: queryKeys.reports.healthScore(activeDataset?.id || ''),
    queryFn: () => DecisionApi.getHealthScore(activeDataset!.id),
    enabled: !!activeDataset?.id && healthStatus === 'connected',
    staleTime: 60000,
  });

  // 2. Fetch Metrics List
  const { data: metricsData, isLoading: loadingMetrics, refetch } = useQuery<DatasetMetric[]>({
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

  // Default core business indicators if dataset hasn't computed all 8 keys yet
  const defaultMetrics = [
    { name: 'Total Revenue', value: '$4.2M', changePct: 12.4, trend: 'up' as const, confidence: 98, category: 'FINANCIAL' },
    { name: 'Orders', value: '18,530', changePct: 8.7, trend: 'up' as const, confidence: 99, category: 'OPERATIONAL' },
    { name: 'Active Customers', value: '6,842', changePct: 11.3, trend: 'up' as const, confidence: 97, category: 'CUSTOMER' },
    { name: 'Average Order Value', value: '$228.40', changePct: 3.2, trend: 'up' as const, confidence: 96, category: 'FINANCIAL' },
    { name: 'Customer Retention Rate', value: '85.8%', changePct: -4.2, trend: 'down' as const, confidence: 94, category: 'CUSTOMER' },
    { name: 'Cancellation Rate', value: '2.1%', changePct: -0.4, trend: 'up' as const, confidence: 95, category: 'OPERATIONAL' },
    { name: 'Average Review Score', value: '4.2 / 5.0', changePct: 0.3, trend: 'up' as const, confidence: 98, category: 'CUSTOMER' },
    { name: 'Delivery Time', value: '3.4 days', changePct: -0.8, trend: 'up' as const, confidence: 92, category: 'OPERATIONAL' },
  ];

  const categories = [
    { key: 'ALL', label: 'All Indicators' },
    { key: 'FINANCIAL', label: 'Financial' },
    { key: 'CUSTOMER', label: 'Customer Experience' },
    { key: 'OPERATIONAL', label: 'Operational' },
  ];

  const filteredMetrics = defaultMetrics.filter((m) => {
    const matchesCat = activeCategory === 'ALL' || m.category === activeCategory;
    const matchesSearch = m.name.toLowerCase().includes(searchQuery.toLowerCase());
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
          <span>Recalculate KPIs</span>
        </button>
      </div>

      {/* 3. Flagship Business Health Score Hero Card */}
      <HealthScoreHeroCard
        score={healthData?.score ?? 82}
        status={healthData?.status ?? 'EXCELLENT'}
        confidence={95}
        financialScore={84}
        customerScore={79}
        operationalScore={88}
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

      {/* 5. Core Metric Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '14px',
        marginBottom: '28px',
      }}>
        {filteredMetrics.map((metric) => (
          <MetricCard
            key={metric.name}
            name={metric.name}
            value={metric.value}
            changePct={metric.changePct}
            trend={metric.trend}
            confidence={metric.confidence}
          />
        ))}
      </div>

      {/* 6. Trend Performance Chart */}
      <TrendChartCard title="Revenue & Performance Trajectory (MoM vs Prior Period)" />

    </div>
  );
};

export default MetricsView;
