import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ConfidenceBandChart } from '../components/charts/ConfidenceBandChart';
import { ForecastPoint } from '../types';

describe('ConfidenceBandChart Component', () => {
  it('renders period labels and handles empty data gracefully', () => {
    const points: ForecastPoint[] = [
      { period: '2026-09', predicted_value: 12000, lower_bound: 11000, upper_bound: 13000 },
      { period: '2026-10', predicted_value: 12500, lower_bound: 11200, upper_bound: 13800 },
      { period: '2026-11', predicted_value: 13000, lower_bound: 11500, upper_bound: 14500 },
    ];

    render(<ConfidenceBandChart points={points} metricKey="total_revenue" />);
    expect(screen.getByText('2026-09')).toBeInTheDocument();
    expect(screen.getByText('2026-10')).toBeInTheDocument();
    expect(screen.getByText('2026-11')).toBeInTheDocument();
  });

  it('renders fallback when points array is empty', () => {
    render(<ConfidenceBandChart points={[]} metricKey="total_revenue" />);
    expect(screen.getByText('No projection points available')).toBeInTheDocument();
  });
});
