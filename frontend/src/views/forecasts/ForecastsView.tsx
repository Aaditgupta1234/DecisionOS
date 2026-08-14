import React, { useEffect, useState } from 'react';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { Forecast, ForecastHorizon, ForecastPoint } from '../../types';
import { ConfidenceBandChart } from '../../components/charts/ConfidenceBandChart';
import { LoadingSkeleton } from '../../components/feedback/LoadingSkeleton';
import { ErrorBanner } from '../../components/feedback/ErrorBanner';
import { EmptyState } from '../../components/feedback/EmptyState';
import { InsufficientDataAlert } from '../../components/feedback/InsufficientDataAlert';
import { TrendingUp, RefreshCw, AlertCircle, CheckCircle, Shield } from 'lucide-react';

export const ForecastsView: React.FC = () => {
  const { activeDataset } = useDataset();
  const [forecasts, setForecasts] = useState<Forecast[]>([]);
  const [activeForecast, setActiveForecast] = useState<Forecast | null>(null);
  const [targetMetric, setTargetMetric] = useState<string>('total_revenue');
  const [horizon, setHorizon] = useState<ForecastHorizon>('90_DAYS');
  const [confidence, setConfidence] = useState<number>(0.80);
  const [loading, setLoading] = useState<boolean>(true);
  const [isForecasting, setIsForecasting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [insufficientDataMsg, setInsufficientDataMsg] = useState<string | null>(null);

  const fetchForecasts = async (datasetId: string) => {
    try {
      setLoading(true);
      setError(null);
      setInsufficientDataMsg(null);
      const res = await DecisionApi.listForecasts(datasetId);
      const list = res.forecasts || [];
      setForecasts(list);
      if (list.length > 0) {
        setActiveForecast(list[0]);
      } else {
        setActiveForecast(null);
      }
    } catch (err: any) {
      console.error('Failed to load forecasts:', err);
      setError(err?.message || 'Could not fetch forecasts.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunForecast = async () => {
    if (!activeDataset) return;
    try {
      setIsForecasting(true);
      setError(null);
      setInsufficientDataMsg(null);
      const generated = await DecisionApi.createForecast(activeDataset.id, {
        metric_key: targetMetric,
        horizon,
        confidence_level: confidence,
      });
      setActiveForecast(generated);
      setForecasts([generated, ...forecasts]);
    } catch (err: any) {
      console.error('Forecast execution failed:', err);
      if (err.status === 422 || err.message?.includes('observations')) {
        setInsufficientDataMsg(err.message || 'Insufficient historical observations for this frequency/horizon.');
      } else {
        setError(err?.message || 'Failed to generate forecast projection.');
      }
    } finally {
      setIsForecasting(false);
    }
  };

  useEffect(() => {
    if (activeDataset?.id) {
      fetchForecasts(activeDataset.id);
    } else {
      setLoading(false);
    }
  }, [activeDataset?.id]);

  if (!activeDataset) {
    return (
      <div className="page-container">
        <EmptyState
          title="No Active Dataset Selected"
          description="Select a dataset to run statistical time-series forecasts."
          icon={TrendingUp}
        />
      </div>
    );
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <span className="badge badge-primary">Phase 6.4 Forecasting Engine</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Deterministic Backtested Time Series
            </span>
          </div>
          <h1>Statistical Time-Series Forecasting</h1>
          <p style={{ marginTop: '4px', fontSize: '0.9rem' }}>
            Historical holdout backtesting and point projections with statistical prediction intervals.
          </p>
        </div>
      </div>

      {error && <ErrorBanner message={error} />}

      {insufficientDataMsg && (
        <InsufficientDataAlert
          title="Analytical Limitation: Insufficient Historical Observations"
          message={insufficientDataMsg}
          requirementDetails="Forecasting requires minimum continuity: Daily (>=30 observations), Weekly (>=12 observations), Monthly (>=6 observations)."
        />
      )}

      {/* Control Panel Card */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', alignItems: 'flex-end' }}>
          <div>
            <label className="label">Target KPI Metric</label>
            <select
              value={targetMetric}
              onChange={(e) => setTargetMetric(e.target.value)}
              className="select"
            >
              <option value="total_revenue">Total Revenue</option>
              <option value="total_orders">Total Orders</option>
              <option value="unique_customers">Unique Customers</option>
              <option value="average_revenue">Average Revenue</option>
              <option value="completion_rate">Completion Rate</option>
            </select>
          </div>

          <div>
            <label className="label">Forecast Horizon</label>
            <select
              value={horizon}
              onChange={(e) => setHorizon(e.target.value as ForecastHorizon)}
              className="select"
            >
              <option value="30_DAYS">30 Days</option>
              <option value="90_DAYS">90 Days (Quarterly)</option>
              <option value="180_DAYS">180 Days (Half-Year)</option>
              <option value="365_DAYS">365 Days (Annual)</option>
            </select>
          </div>

          <div>
            <label className="label">Confidence Level ({Math.round(confidence * 100)}%)</label>
            <select
              value={confidence}
              onChange={(e) => setConfidence(parseFloat(e.target.value))}
              className="select"
            >
              <option value={0.80}>80% Prediction Interval</option>
              <option value={0.90}>90% Prediction Interval</option>
              <option value={0.95}>95% Prediction Interval</option>
            </select>
          </div>

          <div>
            <button
              onClick={handleRunForecast}
              disabled={isForecasting}
              className="btn btn-primary"
              style={{ width: '100%', height: '38px' }}
            >
              <TrendingUp size={16} />
              <span>{isForecasting ? 'Calculating...' : 'Generate Forecast'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Forecast Display */}
      {loading ? (
        <LoadingSkeleton count={3} height="160px" />
      ) : activeForecast ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Chart & Telemetry Card */}
          <div className="card-elevated">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                  <span className="badge badge-primary">{activeForecast.metric_key}</span>
                  <span className="badge badge-neutral">Horizon: {activeForecast.horizon}</span>
                  <span className="badge badge-neutral">Freq: {activeForecast.frequency}</span>
                  <span
                    className={`badge ${
                      activeForecast.trend === 'INCREASING'
                        ? 'badge-success'
                        : activeForecast.trend === 'DECREASING'
                        ? 'badge-danger'
                        : 'badge-primary'
                    }`}
                  >
                    Trend: {activeForecast.trend}
                  </span>
                </div>
                <h3 style={{ fontSize: '1.2rem', color: '#ffffff' }}>
                  Forward Trajectory & Prediction Bands
                </h3>
              </div>

              {/* Model Telemetry */}
              <div style={{ textAlign: 'right', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                <div>Selected Model: <strong style={{ color: 'var(--color-primary-light)' }}>{activeForecast.model_name}</strong></div>
                <div>Validation RMSE: <strong style={{ color: 'var(--text-main)' }}>{activeForecast.model_metrics.rmse}</strong></div>
              </div>
            </div>

            {/* SVG Prediction Interval Chart */}
            <div style={{ backgroundColor: 'var(--bg-app)', padding: '16px', borderRadius: 'var(--radius-md)' }}>
              <ConfidenceBandChart
                points={activeForecast.forecast_points}
                metricKey={activeForecast.metric_key}
                height={260}
              />
            </div>

            {/* Projection Points Table */}
            <div style={{ marginTop: '20px', overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-default)', textAlign: 'left', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '8px 12px' }}>PERIOD</th>
                    <th style={{ padding: '8px 12px' }}>LOWER BOUND ({Math.round(activeForecast.confidence_level * 100)}%)</th>
                    <th style={{ padding: '8px 12px' }}>PROJECTED VALUE</th>
                    <th style={{ padding: '8px 12px' }}>UPPER BOUND ({Math.round(activeForecast.confidence_level * 100)}%)</th>
                  </tr>
                </thead>
                <tbody>
                  {activeForecast.forecast_points.map((p, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                      <td style={{ padding: '10px 12px', fontWeight: 600, color: 'var(--text-main)' }}>{p.period}</td>
                      <td style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>{p.lower_bound?.toLocaleString()}</td>
                      <td style={{ padding: '10px 12px', fontWeight: 700, color: 'var(--color-primary-light)' }}>
                        {p.predicted_value.toLocaleString()}
                      </td>
                      <td style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>{p.upper_bound?.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Limitations & Volatility Warnings */}
          {activeForecast.limitations && activeForecast.limitations.length > 0 && (
            <div className="card" style={{ borderLeft: '4px solid var(--color-warning)' }}>
              <h4 style={{ color: 'var(--color-warning)', marginBottom: '8px' }}>
                Analytical Limitations & Volatility Notes
              </h4>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {activeForecast.limitations.map((lim, idx) => (
                  <li key={idx} style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    • {lim}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : (
        <EmptyState
          title="No Forecast Generated Yet"
          description="Select a metric and horizon above to calculate statistical predictions and confidence intervals."
          icon={TrendingUp}
        />
      )}
    </div>
  );
};
