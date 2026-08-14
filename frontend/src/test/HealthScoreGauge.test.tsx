import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { HealthScoreGauge } from '../components/metrics/HealthScoreGauge';

describe('HealthScoreGauge Component', () => {
  it('renders health score index and categorical status tier', () => {
    render(
      <HealthScoreGauge
        score={85}
        status="HEALTHY"
        description="Business metrics indicate strong operational stability."
      />
    );

    expect(screen.getByText('85')).toBeInTheDocument();
    expect(screen.getByText('/ 100')).toBeInTheDocument();
    expect(screen.getByText('HEALTHY')).toBeInTheDocument();
    expect(
      screen.getByText('Business metrics indicate strong operational stability.')
    ).toBeInTheDocument();
  });

  it('renders critical status badge accurately', () => {
    render(<HealthScoreGauge score={35} status="CRITICAL" />);
    expect(screen.getByText('35')).toBeInTheDocument();
    expect(screen.getByText('CRITICAL')).toBeInTheDocument();
  });
});
