import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { DatasetMetric } from '../../types';

interface MetricCardProps {
  metric: DatasetMetric;
}

export const MetricCard: React.FC<MetricCardProps> = ({ metric }) => {
  const formatValue = (key: string, val: number, unit?: string) => {
    if (unit) return `${val.toLocaleString()} ${unit}`;

    if (key.includes('revenue') || key.includes('cost') || key.includes('price')) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        maximumFractionDigits: val >= 1000 ? 0 : 2,
      }).format(val);
    }

    if (key.includes('rate') || key.includes('percentage') || key.includes('margin')) {
      return `${val.toFixed(1)}%`;
    }

    if (key.includes('score')) {
      return val.toFixed(2);
    }

    return Number.isInteger(val) ? val.toLocaleString() : val.toFixed(2);
  };

  const getTrendIcon = (dir?: string) => {
    if (dir === 'UP') return <TrendingUp size={16} color="var(--color-success)" />;
    if (dir === 'DOWN') return <TrendingDown size={16} color="var(--color-danger)" />;
    return <Minus size={16} color="var(--text-muted)" />;
  };

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            {metric.metric_category || 'General'}
          </span>
          <span className="badge badge-neutral" style={{ fontSize: '0.65rem' }}>
            {metric.metric_key}
          </span>
        </div>
        <h4 style={{ fontSize: '0.95rem', color: 'var(--text-main)', marginBottom: '12px' }}>
          {metric.metric_name}
        </h4>
      </div>

      <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
        <div style={{ fontSize: '1.65rem', fontWeight: 700, color: '#ffffff', letterSpacing: '-0.02em' }}>
          {formatValue(metric.metric_key, metric.metric_value, metric.unit)}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          {getTrendIcon(metric.trend_direction)}
        </div>
      </div>
    </div>
  );
};
