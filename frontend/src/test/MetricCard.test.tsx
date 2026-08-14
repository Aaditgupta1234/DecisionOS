import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { MetricCard } from '../components/metrics/MetricCard';
import { DatasetMetric } from '../types';

describe('MetricCard Component', () => {
  it('formats currency metrics with dollar sign', () => {
    const metric: DatasetMetric = {
      id: 'm1',
      metric_key: 'total_revenue',
      metric_name: 'Total Revenue',
      metric_category: 'REVENUE',
      metric_value: 1250000,
      calculated_at: '2026-08-14T00:00:00Z',
      trend_direction: 'UP',
    };

    render(<MetricCard metric={metric} />);
    expect(screen.getByText('Total Revenue')).toBeInTheDocument();
    expect(screen.getByText('REVENUE')).toBeInTheDocument();
    expect(screen.getByText('$1,250,000')).toBeInTheDocument();
  });

  it('formats rate metrics with percentage symbol', () => {
    const metric: DatasetMetric = {
      id: 'm2',
      metric_key: 'customer_churn_rate',
      metric_name: 'Customer Churn Rate',
      metric_category: 'CUSTOMER',
      metric_value: 4.8,
      calculated_at: '2026-08-14T00:00:00Z',
      trend_direction: 'DOWN',
    };

    render(<MetricCard metric={metric} />);
    expect(screen.getByText('Customer Churn Rate')).toBeInTheDocument();
    expect(screen.getByText('4.8%')).toBeInTheDocument();
  });
});
