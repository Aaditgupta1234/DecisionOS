import React, { useEffect, useState } from 'react';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { Recommendation, RecommendationPriority } from '../../types';
import { LoadingSkeleton } from '../../components/feedback/LoadingSkeleton';
import { ErrorBanner } from '../../components/feedback/ErrorBanner';
import { EmptyState } from '../../components/feedback/EmptyState';
import { CheckCircle2, ArrowRight, Clock, Zap, Target } from 'lucide-react';
import { Link } from 'react-router-dom';

export const RecommendationsView: React.FC = () => {
  const { activeDataset } = useDataset();
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRecommendations = async (datasetId: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await DecisionApi.listRecommendations(datasetId);
      setRecommendations(Array.isArray(data) ? data : []);
    } catch (err: any) {
      console.error('Failed to load recommendations:', err);
      setError(err?.message || 'Could not fetch actionable recommendations.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeDataset?.id) {
      fetchRecommendations(activeDataset.id);
    } else {
      setLoading(false);
    }
  }, [activeDataset?.id]);

  if (!activeDataset) {
    return (
      <div className="page-container">
        <EmptyState
          title="No Active Dataset Selected"
          description="Select a dataset to inspect its actionable recommendations."
          icon={CheckCircle2}
        />
      </div>
    );
  }

  const filtered = recommendations.filter(
    (r) => priorityFilter === 'ALL' || r.priority === priorityFilter
  );

  const getPriorityBadge = (p: RecommendationPriority) => {
    switch (p) {
      case 'CRITICAL':
        return 'badge-danger';
      case 'HIGH':
        return 'badge-warning';
      case 'MEDIUM':
        return 'badge-primary';
      default:
        return 'badge-neutral';
    }
  };

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <span className="badge badge-primary">Phase 5.7 Recommendation Engine</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Deterministic Actionable Prescriptions
            </span>
          </div>
          <h1>Actionable Recommendations</h1>
          <p style={{ marginTop: '4px', fontSize: '0.9rem' }}>
            Prescriptions linked directly to diagnosed root causes with estimated impact and effort.
          </p>
        </div>

        <Link to="/strategy" className="btn btn-ai">
          <span>View 90-Day Strategy Roadmap</span>
          <ArrowRight size={16} />
        </Link>
      </div>

      {error && <ErrorBanner message={error} onRetry={() => fetchRecommendations(activeDataset.id)} />}

      {/* Priority Tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px' }}>
        {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM'].map((p) => (
          <button
            key={p}
            onClick={() => setPriorityFilter(p)}
            className={`btn btn-sm ${priorityFilter === p ? 'btn-primary' : 'btn-secondary'}`}
          >
            {p}
          </button>
        ))}
      </div>

      {/* Recommendations List */}
      {loading ? (
        <LoadingSkeleton count={3} height="140px" />
      ) : filtered.length > 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {filtered.map((rec) => (
            <div key={rec.id} className="card-elevated">
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '10px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                    <span className={`badge ${getPriorityBadge(rec.priority)}`}>{rec.priority} Priority</span>
                    <span className="badge badge-neutral">Status: {rec.status || 'PROPOSED'}</span>
                  </div>
                  <h3 style={{ fontSize: '1.15rem', color: '#ffffff', marginBottom: '6px' }}>
                    {rec.title}
                  </h3>
                </div>
              </div>

              <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '16px' }}>
                {rec.action_summary}
              </p>

              {/* Attributes Grid */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                  gap: '12px',
                  backgroundColor: 'var(--bg-app)',
                  padding: '12px 16px',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.8rem',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Target size={16} color="var(--color-success)" />
                  <div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>EXPECTED IMPACT</div>
                    <div style={{ fontWeight: 600, color: '#ffffff' }}>{rec.expected_impact}</div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Zap size={16} color="var(--color-warning)" />
                  <div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>ESTIMATED EFFORT</div>
                    <div style={{ fontWeight: 600, color: '#ffffff' }}>{rec.estimated_effort}</div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Clock size={16} color="var(--color-primary-light)" />
                  <div>
                    <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>TIME TO VALUE</div>
                    <div style={{ fontWeight: 600, color: '#ffffff' }}>{rec.time_to_value}</div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState
          title="No Recommendations Found"
          description="No recommendations in this priority tier."
          icon={CheckCircle2}
        />
      )}
    </div>
  );
};
