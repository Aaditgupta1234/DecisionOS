import React, { useEffect, useState } from 'react';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { Scenario, ScenarioAdjustmentType, ScenarioAssumption } from '../../types';
import { LoadingSkeleton } from '../../components/feedback/LoadingSkeleton';
import { ErrorBanner } from '../../components/feedback/ErrorBanner';
import { EmptyState } from '../../components/feedback/EmptyState';
import { Sliders, Plus, Trash2, ArrowRight, ShieldCheck, CheckCircle2 } from 'lucide-react';

export const ScenariosView: React.FC = () => {
  const { activeDataset } = useDataset();
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // New Scenario Form State
  const [showModal, setShowModal] = useState<boolean>(false);
  const [scenarioName, setScenarioName] = useState<string>('Optimized Growth Plan');
  const [scenarioDesc, setScenarioDesc] = useState<string>('Simulating 15% revenue expansion with 5% churn reduction');
  const [assumptions, setAssumptions] = useState<ScenarioAssumption[]>([
    { metric_key: 'total_revenue', adjustment_type: 'RELATIVE_PERCENT', adjustment_value: 15.0 },
    { metric_key: 'customer_churn_rate', adjustment_type: 'RELATIVE_PERCENT', adjustment_value: -5.0 },
  ]);

  const fetchScenarios = async (datasetId: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await DecisionApi.listScenarios(datasetId);
      setScenarios(Array.isArray(data) ? data : []);
    } catch (err: any) {
      console.error('Failed to load scenarios:', err);
      setError(err?.message || 'Could not fetch scenario simulations.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateScenario = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeDataset) return;

    try {
      setIsSimulating(true);
      setError(null);
      const created = await DecisionApi.createScenario(activeDataset.id, {
        name: scenarioName,
        description: scenarioDesc,
        assumptions,
      });
      setScenarios([created, ...scenarios]);
      setShowModal(false);
    } catch (err: any) {
      console.error('Scenario simulation failed:', err);
      setError(err?.message || 'Failed to execute scenario simulation.');
    } finally {
      setIsSimulating(false);
    }
  };

  const addAssumption = () => {
    setAssumptions([
      ...assumptions,
      { metric_key: 'total_revenue', adjustment_type: 'RELATIVE_PERCENT', adjustment_value: 10.0 },
    ]);
  };

  const removeAssumption = (idx: number) => {
    setAssumptions(assumptions.filter((_, i) => i !== idx));
  };

  const updateAssumption = (idx: number, field: keyof ScenarioAssumption, val: any) => {
    const next = [...assumptions];
    next[idx] = { ...next[idx], [field]: val };
    setAssumptions(next);
  };

  useEffect(() => {
    if (activeDataset?.id) {
      fetchScenarios(activeDataset.id);
    } else {
      setLoading(false);
    }
  }, [activeDataset?.id]);

  if (!activeDataset) {
    return (
      <div className="page-container">
        <EmptyState
          title="No Active Dataset Selected"
          description="Select a dataset to run deterministic What-If scenario simulations."
          icon={Sliders}
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
            <span className="badge badge-primary">Phase 6.3 Scenario Engine</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Deterministic Numerical Projections (No LLM)
            </span>
          </div>
          <h1>What-If Scenario Simulation Studio</h1>
          <p style={{ marginTop: '4px', fontSize: '0.9rem' }}>
            Model the systemic ripple effects of business decisions on diagnostic findings and health score without mutating historical actuals.
          </p>
        </div>

        <button onClick={() => setShowModal(true)} className="btn btn-primary">
          <Plus size={16} />
          <span>New Simulation</span>
        </button>
      </div>

      {error && <ErrorBanner message={error} onRetry={() => fetchScenarios(activeDataset.id)} />}

      {/* Scenarios List */}
      {loading ? (
        <LoadingSkeleton count={3} height="160px" />
      ) : scenarios.length > 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {scenarios.map((sc) => (
            <div key={sc.id} className="card-elevated">
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '14px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                    <span className="badge badge-primary">Scenario v{sc.scenario_version}</span>
                    <span className="badge badge-neutral">{sc.status}</span>
                  </div>
                  <h3 style={{ fontSize: '1.2rem', color: '#ffffff', marginBottom: '4px' }}>{sc.name}</h3>
                  {sc.description && (
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{sc.description}</p>
                  )}
                </div>

                {/* Health Comparison Chip */}
                <div
                  style={{
                    backgroundColor: 'var(--bg-app)',
                    border: '1px solid var(--border-default)',
                    padding: '10px 18px',
                    borderRadius: 'var(--radius-md)',
                    textAlign: 'right',
                  }}
                >
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    PROJECTED HEALTH SCORE
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--color-success)' }}>
                    {sc.projected_health_score}{' '}
                    <span style={{ fontSize: '0.8rem', fontWeight: 500, color: 'var(--text-secondary)' }}>
                      ({sc.projected_health_status})
                    </span>
                  </div>
                </div>
              </div>

              {/* Assumptions & Projections Grid */}
              <div className="grid-2" style={{ marginTop: '16px' }}>
                {/* Assumptions Card */}
                <div style={{ backgroundColor: 'var(--bg-app)', padding: '14px', borderRadius: 'var(--radius-sm)' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    User Assumptions Applied:
                  </span>
                  <div style={{ marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    {(sc.assumptions || []).map((a, idx) => (
                      <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                        <span style={{ color: 'var(--text-main)' }}>{a.metric_key}</span>
                        <span className="badge badge-primary">
                          {a.adjustment_value > 0 ? `+${a.adjustment_value}` : a.adjustment_value}
                          {a.adjustment_type === 'RELATIVE_PERCENT' ? '%' : ' pts'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Projected Metric Deltas */}
                <div style={{ backgroundColor: 'var(--bg-app)', padding: '14px', borderRadius: 'var(--radius-sm)' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    Projected KPI Outcomes:
                  </span>
                  <div style={{ marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    {Object.entries(sc.projected_metrics || {}).slice(0, 3).map(([k, v]: [string, any]) => (
                      <div key={k} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                        <span style={{ color: 'var(--text-secondary)' }}>{k}</span>
                        <span style={{ fontWeight: 600, color: '#ffffff' }}>
                          {typeof v === 'number' ? v.toLocaleString() : JSON.stringify(v)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState
          title="No Scenarios Simulated Yet"
          description="Create your first What-If scenario to model revenue, price, or churn shifts."
          icon={Sliders}
          actionText="Create Simulation"
          onAction={() => setShowModal(true)}
        />
      )}

      {/* Create Simulation Modal */}
      {showModal && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 200,
          }}
        >
          <div
            className="card-elevated"
            style={{ width: '560px', maxWidth: '90vw', maxHeight: '90vh', overflowY: 'auto' }}
          >
            <h2 style={{ marginBottom: '16px' }}>New What-If Simulation</h2>

            <form onSubmit={handleCreateScenario}>
              <div style={{ marginBottom: '14px' }}>
                <label className="label">Scenario Name</label>
                <input
                  type="text"
                  required
                  value={scenarioName}
                  onChange={(e) => setScenarioName(e.target.value)}
                  className="input"
                />
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label className="label">Description / Strategic Context</label>
                <input
                  type="text"
                  value={scenarioDesc}
                  onChange={(e) => setScenarioDesc(e.target.value)}
                  className="input"
                />
              </div>

              <div style={{ marginBottom: '18px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <label className="label" style={{ marginBottom: 0 }}>Model Assumptions</label>
                  <button type="button" onClick={addAssumption} className="btn btn-ghost btn-sm" style={{ color: 'var(--color-primary-light)' }}>
                    <Plus size={14} /> Add Assumption
                  </button>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {assumptions.map((a, idx) => (
                    <div key={idx} style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                      <select
                        value={a.metric_key}
                        onChange={(e) => updateAssumption(idx, 'metric_key', e.target.value)}
                        className="select"
                        style={{ flex: 2 }}
                      >
                        <option value="total_revenue">Total Revenue</option>
                        <option value="customer_churn_rate">Customer Churn Rate</option>
                        <option value="completion_rate">Completion Rate</option>
                        <option value="average_review_score">Review Score</option>
                      </select>

                      <select
                        value={a.adjustment_type}
                        onChange={(e) => updateAssumption(idx, 'adjustment_type', e.target.value as ScenarioAdjustmentType)}
                        className="select"
                        style={{ flex: 2 }}
                      >
                        <option value="RELATIVE_PERCENT">Relative %</option>
                        <option value="PERCENTAGE_POINTS">Percentage Pts</option>
                        <option value="ABSOLUTE_VALUE">Absolute Value</option>
                      </select>

                      <input
                        type="number"
                        step="any"
                        value={a.adjustment_value}
                        onChange={(e) => updateAssumption(idx, 'adjustment_value', parseFloat(e.target.value) || 0)}
                        className="input"
                        style={{ width: '90px' }}
                      />

                      {assumptions.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeAssumption(idx)}
                          className="btn btn-ghost btn-sm"
                          style={{ color: 'var(--color-danger)' }}
                        >
                          <Trash2 size={16} />
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '24px' }}>
                <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" disabled={isSimulating} className="btn btn-primary">
                  {isSimulating ? 'Running Simulation...' : 'Run Simulation'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
