import React, { useEffect, useState } from 'react';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { AIInsight } from '../../types';
import { LoadingSkeleton } from '../../components/feedback/LoadingSkeleton';
import { ErrorBanner } from '../../components/feedback/ErrorBanner';
import { EmptyState } from '../../components/feedback/EmptyState';
import { Sparkles, RefreshCw, AlertTriangle, ShieldCheck, Calendar, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const AIInsightsView: React.FC = () => {
  const { activeDataset } = useDataset();
  const [insight, setInsight] = useState<AIInsight | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchInsight = async (datasetId: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await DecisionApi.getLatestInsight(datasetId);
      setInsight(data);
    } catch (err: any) {
      console.error('Failed to load AI insight:', err);
      // If 404, allow user to generate
      setInsight(null);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!activeDataset) return;
    try {
      setIsGenerating(true);
      setError(null);
      const fresh = await DecisionApi.generateInsight(activeDataset.id);
      setInsight(fresh);
    } catch (err: any) {
      console.error('Insight generation failed:', err);
      setError(err?.message || 'Failed to generate AI executive insights.');
    } finally {
      setIsGenerating(false);
    }
  };

  useEffect(() => {
    if (activeDataset?.id) {
      fetchInsight(activeDataset.id);
    } else {
      setLoading(false);
    }
  }, [activeDataset?.id]);

  if (!activeDataset) {
    return (
      <div className="page-container">
        <EmptyState
          title="No Active Dataset Selected"
          description="Select a dataset to view or generate executive AI insights."
          icon={Sparkles}
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
            <span className="badge badge-ai">Phase 6.0 AI Executive Narrative</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--color-ai-light)' }}>
              Multi-Provider LLM Intelligence Synthesis
            </span>
          </div>
          <h1>AI Insights & Executive Narrative</h1>
          <p style={{ marginTop: '4px', fontSize: '0.9rem' }}>
            Synthesized business intelligence translating deterministic findings into executive strategy.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="btn btn-ai"
          >
            <RefreshCw size={16} className={isGenerating ? 'spin' : ''} />
            <span>{isGenerating ? 'Synthesizing...' : 'Regenerate AI Narrative'}</span>
          </button>

          <Link to="/chat" className="btn btn-secondary">
            <span>DEX Analyst</span>
            <ArrowRight size={16} />
          </Link>
        </div>
      </div>

      {error && <ErrorBanner message={error} onRetry={handleGenerate} />}

      {loading ? (
        <LoadingSkeleton count={4} height="140px" />
      ) : insight ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Executive Narrative Lead Card */}
          <div className="card-elevated card-ai">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
              <span className="badge badge-ai">✨ Executive Decision Narrative</span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Generated: {new Date(insight.created_at).toLocaleString()} | Model: {insight.model_name}
              </span>
            </div>
            <p style={{ fontSize: '1.05rem', color: '#ffffff', lineHeight: 1.7, fontWeight: 400 }}>
              {insight.executive_narrative}
            </p>
          </div>

          {/* Key Takeaways & Strategic Priorities Grid */}
          <div className="grid-2">
            {/* Key Takeaways */}
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
                <ShieldCheck size={18} color="var(--color-success)" />
                <h3>Executive Key Takeaways</h3>
              </div>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {(insight.key_takeaways || []).map((point, idx) => (
                  <li key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', fontSize: '0.875rem' }}>
                    <span style={{ color: 'var(--color-success)', fontWeight: 700 }}>•</span>
                    <span style={{ color: 'var(--text-main)', lineHeight: 1.5 }}>{point}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Strategic Priorities */}
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
                <Sparkles size={18} color="var(--color-ai-light)" />
                <h3>Strategic Priorities</h3>
              </div>
              <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {(insight.strategic_priorities || []).map((p, idx) => (
                  <li key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', fontSize: '0.875rem' }}>
                    <span style={{ color: 'var(--color-ai-light)', fontWeight: 700 }}>{idx + 1}.</span>
                    <span style={{ color: 'var(--text-main)', lineHeight: 1.5 }}>{p}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Risk Analysis Card */}
          {insight.risk_analysis && insight.risk_analysis.length > 0 && (
            <div className="card" style={{ borderLeft: '4px solid var(--color-warning)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                <AlertTriangle size={18} color="var(--color-warning)" />
                <h3>Risk & Vulnerability Analysis</h3>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px' }}>
                {insight.risk_analysis.map((r, idx) => (
                  <div
                    key={idx}
                    style={{
                      backgroundColor: 'var(--bg-app)',
                      padding: '12px 16px',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '0.85rem',
                      color: 'var(--text-secondary)',
                      lineHeight: 1.5,
                    }}
                  >
                    ⚠️ {r}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 90-Day Action Plan Briefing */}
          {insight.action_plan_90_day && insight.action_plan_90_day.length > 0 && (
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
                <Calendar size={18} color="var(--color-primary-light)" />
                <h3>Recommended 90-Day Action Trajectory</h3>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {insight.action_plan_90_day.map((step, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      padding: '10px 14px',
                      backgroundColor: 'var(--bg-surface-elevated)',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '0.875rem',
                    }}
                  >
                    <span className="badge badge-primary">Step {idx + 1}</span>
                    <span style={{ color: 'var(--text-main)' }}>{step}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <EmptyState
          title="No AI Executive Insights Generated Yet"
          description="Click below to generate a synthesized executive narrative and risk assessment for this dataset."
          icon={Sparkles}
          actionText={isGenerating ? 'Synthesizing...' : 'Generate AI Executive Narrative'}
          onAction={handleGenerate}
        />
      )}

      <style>{`
        .spin { animation: spin 1s linear infinite; }
        @keyframes spin { 100% { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};
