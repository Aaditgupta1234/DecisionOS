import React, { useEffect, useState } from 'react';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { DatasetMetric } from '../../types';
import { MetricCard } from '../../components/metrics/MetricCard';
import { LoadingSkeleton } from '../../components/feedback/LoadingSkeleton';
import { ErrorBanner } from '../../components/feedback/ErrorBanner';
import { EmptyState } from '../../components/feedback/EmptyState';
import { Activity, Search } from 'lucide-react';

export const MetricsView: React.FC = () => {
  const { activeDataset } = useDataset();
  const [metrics, setMetrics] = useState<DatasetMetric[]>([]);
  const [activeCategory, setActiveCategory] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = async (datasetId: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await DecisionApi.listMetrics(datasetId);
      setMetrics(Array.isArray(data) ? data : []);
    } catch (err: any) {
      console.error('Failed to load metrics:', err);
      setError(err?.message || 'Could not fetch KPI metrics for this dataset.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeDataset?.id) {
      fetchMetrics(activeDataset.id);
    } else {
      setLoading(false);
    }
  }, [activeDataset?.id]);

  if (!activeDataset) {
    return (
      <div className="page-container">
        <EmptyState
          title="No Active Dataset Selected"
          description="Please select a dataset to view its computed KPI metrics."
          icon={Activity}
        />
      </div>
    );
  }

  // Categories list
  const categories = ['ALL', ...Array.from(new Set(metrics.map((m) => m.metric_category).filter(Boolean)))];

  const filteredMetrics = metrics.filter((m) => {
    const matchesCat = activeCategory === 'ALL' || m.metric_category === activeCategory;
    const matchesSearch =
      m.metric_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.metric_key.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCat && matchesSearch;
  });

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
          <span className="badge badge-primary">Phase 4 KPI Engine</span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Deterministic Calculation & Registry
          </span>
        </div>
        <h1>KPI Metrics Explorer</h1>
        <p style={{ marginTop: '4px', fontSize: '0.9rem' }}>
          Real-time deterministic business indicators calculated from dataset transactions.
        </p>
      </div>

      {error && <ErrorBanner message={error} onRetry={() => fetchMetrics(activeDataset.id)} />}

      {/* Filter & Search Bar */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '16px',
          marginBottom: '20px',
        }}
      >
        {/* Category Tabs */}
        <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '4px' }}>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className="btn btn-sm"
              style={{
                backgroundColor: activeCategory === cat ? 'var(--color-primary)' : 'var(--bg-surface-elevated)',
                color: activeCategory === cat ? '#ffffff' : 'var(--text-secondary)',
                border: '1px solid var(--border-default)',
                fontWeight: activeCategory === cat ? 600 : 400,
              }}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div style={{ position: 'relative', width: '240px' }}>
          <Search
            size={16}
            color="var(--text-muted)"
            style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }}
          />
          <input
            type="text"
            placeholder="Search metrics..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input"
            style={{ paddingLeft: '32px' }}
          />
        </div>
      </div>

      {/* Metrics Grid */}
      {loading ? (
        <LoadingSkeleton count={6} height="110px" />
      ) : filteredMetrics.length > 0 ? (
        <div className="grid-3">
          {filteredMetrics.map((m) => (
            <MetricCard key={m.id || m.metric_key} metric={m} />
          ))}
        </div>
      ) : (
        <EmptyState
          title="No Metrics Found"
          description={
            searchQuery
              ? `No metrics matching "${searchQuery}".`
              : 'No KPI metrics have been calculated for this dataset yet.'
          }
          icon={Activity}
        />
      )}
    </div>
  );
};
