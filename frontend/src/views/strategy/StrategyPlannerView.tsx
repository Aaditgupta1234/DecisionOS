import React, { useEffect, useState } from 'react';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { StrategicMilestone, StrategyPlan } from '../../types';
import { LoadingSkeleton } from '../../components/feedback/LoadingSkeleton';
import { ErrorBanner } from '../../components/feedback/ErrorBanner';
import { EmptyState } from '../../components/feedback/EmptyState';
import { Compass, RefreshCw, CheckSquare, Square, Target, Shield } from 'lucide-react';

export const StrategyPlannerView: React.FC = () => {
  const { activeDataset } = useDataset();
  const [strategy, setStrategy] = useState<StrategyPlan | null>(null);
  const [selectedHorizon, setSelectedHorizon] = useState<string>('ALL');
  const [loading, setLoading] = useState<boolean>(true);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStrategy = async (datasetId: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await DecisionApi.getLatestStrategy(datasetId);
      setStrategy(data);
    } catch (err: any) {
      console.error('Failed to load strategy plan:', err);
      setStrategy(null);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!activeDataset) return;
    try {
      setIsGenerating(true);
      setError(null);
      const fresh = await DecisionApi.generateStrategy(activeDataset.id);
      setStrategy(fresh);
    } catch (err: any) {
      console.error('Strategy generation failed:', err);
      setError(err?.message || 'Failed to generate AI strategy roadmap.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleToggleAction = async (milestoneIdx: number, actionIdx: number) => {
    if (!strategy || !strategy.strategic_milestones) return;
    const milestone = strategy.strategic_milestones[milestoneIdx];
    if (!milestone || !milestone.actions) return;
    const action = milestone.actions[actionIdx];
    const newStatus = !action.is_completed;

    // Optimistic UI update
    const updated = JSON.parse(JSON.stringify(strategy)) as StrategyPlan;
    if (updated.strategic_milestones?.[milestoneIdx]?.actions?.[actionIdx]) {
      updated.strategic_milestones[milestoneIdx].actions![actionIdx].is_completed = newStatus;
    }
    setStrategy(updated);

    try {
      if (action.id) {
        await DecisionApi.updateActionStatus(strategy.id, action.id, newStatus);
      }
    } catch (err) {
      console.error('Failed to patch action status:', err);
      // Revert on error
      fetchStrategy(activeDataset!.id);
    }
  };

  useEffect(() => {
    if (activeDataset?.id) {
      fetchStrategy(activeDataset.id);
    } else {
      setLoading(false);
    }
  }, [activeDataset?.id]);

  if (!activeDataset) {
    return (
      <div className="page-container">
        <EmptyState
          title="No Active Dataset Selected"
          description="Select a dataset to view or generate an AI strategic execution roadmap."
          icon={Compass}
        />
      </div>
    );
  }

  const milestones = strategy?.strategic_milestones || [];
  const filteredMilestones = milestones.filter(
    (m) => selectedHorizon === 'ALL' || m.horizon === selectedHorizon
  );

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <span className="badge badge-ai">Phase 6.2 AI Strategy Planner</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--color-ai-light)' }}>
              Deterministic Validation & Execution Roadmap
            </span>
          </div>
          <h1>90-Day Execution Roadmap</h1>
          <p style={{ marginTop: '4px', fontSize: '0.9rem' }}>
            Phased milestone execution tracking operational actions across Immediate, 30, 60, and 90-day horizons.
          </p>
        </div>

        <button onClick={handleGenerate} disabled={isGenerating} className="btn btn-ai">
          <RefreshCw size={16} className={isGenerating ? 'spin' : ''} />
          <span>{isGenerating ? 'Synthesizing...' : 'Regenerate Strategy'}</span>
        </button>
      </div>

      {error && <ErrorBanner message={error} onRetry={handleGenerate} />}

      {loading ? (
        <LoadingSkeleton count={4} height="120px" />
      ) : strategy ? (
        <div>
          {/* Executive Summary Card */}
          <div className="card-elevated card-ai" style={{ marginBottom: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span className="badge badge-ai">Strategic Executive Intent</span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Plan Version: {strategy.plan_version}
              </span>
            </div>
            <p style={{ fontSize: '1rem', color: '#ffffff', lineHeight: 1.6 }}>
              {strategy.executive_summary}
            </p>
          </div>

          {/* Horizon Filter Tabs */}
          <div style={{ display: 'flex', gap: '8px', marginBottom: '20px' }}>
            {['ALL', 'IMMEDIATE', '30_DAYS', '60_DAYS', '90_DAYS'].map((h) => (
              <button
                key={h}
                onClick={() => setSelectedHorizon(h)}
                className={`btn btn-sm ${selectedHorizon === h ? 'btn-primary' : 'btn-secondary'}`}
              >
                {h.replace('_', ' ')}
              </button>
            ))}
          </div>

          {/* Milestones & Actions List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {filteredMilestones.map((m, mIdx) => (
              <div key={mIdx} className="card">
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span className="badge badge-primary">{m.horizon}</span>
                    <h3 style={{ fontSize: '1.1rem', color: '#ffffff' }}>{m.theme}</h3>
                  </div>

                  {m.target_metrics && m.target_metrics.length > 0 && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Target size={14} color="var(--color-primary-light)" />
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Target KPIs:</span>
                      {m.target_metrics.map((t: string) => (
                        <span key={t} className="badge badge-neutral" style={{ fontSize: '0.65rem' }}>
                          {t}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Actions Checklist */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {(m.actions || []).map((act: any, aIdx: number) => (
                    <div
                      key={act.id || aIdx}
                      onClick={() => handleToggleAction(mIdx, aIdx)}
                      style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '12px',
                        padding: '10px 14px',
                        backgroundColor: act.is_completed ? 'rgba(16, 185, 129, 0.06)' : 'var(--bg-surface-elevated)',
                        border: `1px solid ${act.is_completed ? 'var(--color-success-border)' : 'var(--border-subtle)'}`,
                        borderRadius: 'var(--radius-sm)',
                        cursor: 'pointer',
                        transition: 'all var(--transition-fast)',
                      }}
                    >
                      <button
                        style={{
                          background: 'none',
                          border: 'none',
                          color: act.is_completed ? 'var(--color-success)' : 'var(--text-muted)',
                          cursor: 'pointer',
                          marginTop: '2px',
                        }}
                      >
                        {act.is_completed ? <CheckSquare size={18} /> : <Square size={18} />}
                      </button>

                      <div style={{ flex: 1 }}>
                        <div
                          style={{
                            fontWeight: 600,
                            fontSize: '0.9rem',
                            color: act.is_completed ? 'var(--text-muted)' : 'var(--text-main)',
                            textDecoration: act.is_completed ? 'line-through' : 'none',
                            marginBottom: '2px',
                          }}
                        >
                          {act.title}
                        </div>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                          {act.description}
                        </p>
                      </div>

                      {act.owner_role && (
                        <span className="badge badge-neutral" style={{ fontSize: '0.7rem' }}>
                          {act.owner_role}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <EmptyState
          title="No Strategy Plan Generated Yet"
          description="Synthesize a 90-day execution roadmap aligned with diagnosed recommendations and strategic milestones."
          icon={Compass}
          actionText={isGenerating ? 'Synthesizing...' : 'Generate 90-Day Strategy'}
          onAction={handleGenerate}
        />
      )}
    </div>
  );
};
