import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { TrendChartCard } from '../shared/components/metrics/TrendChartCard';

describe('TrendChartCard Component', () => {
  it('renders clean empty state when data prop is missing (undefined)', () => {
    render(<TrendChartCard title="Revenue Performance Trend" />);
    expect(screen.getByText('Revenue Performance Trend')).toBeInTheDocument();
    expect(screen.getByTestId('trend-chart-empty-state')).toBeInTheDocument();
    expect(screen.getByText('No Historical Time-Series Available')).toBeInTheDocument();
    expect(
      screen.getByText(/Period-over-period trend analysis requires multiple time-series observations/i)
    ).toBeInTheDocument();
  });

  it('renders clean empty state when data prop is an empty array', () => {
    render(<TrendChartCard title="Revenue Performance Trend" data={[]} />);
    expect(screen.getByTestId('trend-chart-empty-state')).toBeInTheDocument();
    expect(screen.getByText('No Historical Time-Series Available')).toBeInTheDocument();
  });

  it('renders chart and period toggle buttons when genuine historical data is provided', () => {
    const historicalData = [
      { period: '2026-01', value: 120000, comparisonValue: 110000 },
      { period: '2026-02', value: 135000, comparisonValue: 125000 },
      { period: '2026-03', value: 150000, comparisonValue: 140000 },
    ];

    render(<TrendChartCard title="Revenue Performance Trend" data={historicalData} />);
    expect(screen.getByText('Revenue Performance Trend')).toBeInTheDocument();
    expect(screen.queryByTestId('trend-chart-empty-state')).not.toBeInTheDocument();
    expect(screen.getByText('Month-over-Month')).toBeInTheDocument();
    expect(screen.getByText('Quarter-over-Quarter')).toBeInTheDocument();
  });
});
