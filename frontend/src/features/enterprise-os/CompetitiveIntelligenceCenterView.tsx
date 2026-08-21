import React, { useState } from 'react';
import {
  TrendingUp,
  TrendingDown,
  Award,
  Sparkles,
  CheckCircle2,
  BarChart3,
  ShieldCheck,
  AlertTriangle,
  Lightbulb,
  Target,
  Zap,
  WifiOff,
  RefreshCw,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import {
  useMarketPosition,
  useBenchmarkComparisons,
  useBenchmarkOpportunities,
} from '../../shared/hooks/useCompetitiveIntelligence';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import type { CompetitiveBenchmarkResponse, BenchmarkOpportunityResponse } from '../../types/competitiveIntelligence';

// ---------------------------------------------------------------------------
// Design tokens
// ---------------------------------------------------------------------------
const T = {
  amber: '#F59E0B',
  emerald: '#10B981',
  sky: '#38BDF8',
  purple: '#A855F7',
  rose: '#EF4444',
  slate: '#64748B',
  white: '#FFFFFF',
  cardBg: '#090D14',
  border: '#1E293B',
};

function PulseSkeleton({ width = '100%', height = '24px' }: { width?: string; height?: string }) {
  return (
    <div
      style={{
        width,
        height,
        borderRadius: '6px',
        background: 'rgba(100,116,139,0.15)',
        animation: 'pulse 1.5s ease-in-out infinite',
      }}
    />
  );
}

function MetricCard({
  label,
  value,
  sublabel,
  color,
}: {
  label: string;
  value: React.ReactNode;
  sublabel: string;
  color: string;
}) {
  return (
    <div
      style={{
        background: T.cardBg,
        border: `1px solid ${T.border}`,
        borderRadius: '14px',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
      }}
    >
      <div style={{ fontSize: '0.72rem', color: T.slate, fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
        {label}
      </div>
      <div style={{ fontSize: '2.2rem', fontWeight: 900, color }}>{value}</div>
      <div style={{ fontSize: '0.75rem', color: T.emerald, fontWeight: 700 }}>{sublabel}</div>
    </div>
  );
}

function tierColor(tier: string): string {
  const t = tier.toUpperCase();
  if (t.includes('LAGGING') || t === 'BELOW_MEDIAN') return T.rose;
  if (t === 'LEADER' || t.includes('BEST') || t === 'TOP_QUARTILE') return T.emerald;
  if (t.includes('MEDIAN_LEADER') || t === 'AVERAGE') return T.sky;
  return T.amber;
}

function difficultyColor(tier: string): string {
  const t = tier.toUpperCase();
  if (t === 'HIGH') return T.rose;
  if (t === 'MEDIUM') return T.amber;
  return T.emerald;
}

// ---------------------------------------------------------------------------
// SWOT Quadrant component
// ---------------------------------------------------------------------------
function SwotQuadrant({
  title,
  items,
  color,
  icon,
}: {
  title: string;
  items: string[];
  color: string;
  icon: React.ReactNode;
}) {
  return (
    <div
      style={{
        background: `rgba(${color === T.emerald ? '16,185,129' : color === T.rose ? '239,68,68' : color === T.sky ? '56,189,248' : '245,158,11'},0.06)`,
        border: `1px solid ${color}33`,
        borderRadius: '10px',
        padding: '16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        {icon}
        <span style={{ fontSize: '0.8rem', fontWeight: 800, color, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{title}</span>
      </div>
      {items.length === 0 ? (
        <div style={{ fontSize: '0.76rem', color: T.slate }}>No data available.</div>
      ) : (
        <ul style={{ margin: 0, padding: '0 0 0 16px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {items.map((item, i) => (
            <li key={i} style={{ fontSize: '0.78rem', color: '#CBD5E1', lineHeight: 1.5 }}>{item}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main view
// ---------------------------------------------------------------------------
export const CompetitiveIntelligenceCenterView: React.FC = () => {
  const [generatedScenarioId, setGeneratedScenarioId] = useState<string | null>(null);

  const { status, checkHealth } = useBackendHealth();
  const isOffline = status === 'offline';

  const snapshotQuery = useMarketPosition();
  const comparisonsQuery = useBenchmarkComparisons();
  const opportunitiesQuery = useBenchmarkOpportunities();

  // Combined loading + error — prevent partial rendering
  const isLoading = snapshotQuery.isLoading || comparisonsQuery.isLoading || opportunitiesQuery.isLoading;
  const isError = snapshotQuery.isError || comparisonsQuery.isError || opportunitiesQuery.isError;

  // ── Offline ──────────────────────────────────────────────────────────────
  if (isOffline) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px', padding: '80px 24px', textAlign: 'center' }}>
        <WifiOff size={40} color={T.amber} />
        <div style={{ fontSize: '1.1rem', fontWeight: 800, color: T.white }}>DecisionOS Backend Offline</div>
        <div style={{ fontSize: '0.85rem', color: T.slate }}>Cannot load competitive intelligence. Start the FastAPI server to continue.</div>
        <button onClick={checkHealth} style={{ padding: '10px 20px', background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.3)', borderRadius: '8px', color: T.amber, fontWeight: 700, cursor: 'pointer' }}>
          Retry Connection
        </button>
      </div>
    );
  }

  const snapshot = snapshotQuery.data;
  const comparisons: CompetitiveBenchmarkResponse[] = Array.isArray(comparisonsQuery.data)
    ? comparisonsQuery.data
    : (comparisonsQuery.data as any)?.data ?? [];
  const opportunities: BenchmarkOpportunityResponse[] = Array.isArray(opportunitiesQuery.data)
    ? opportunitiesQuery.data
    : (opportunitiesQuery.data as any)?.data ?? [];

  const snapshotDate = snapshot?.snapshot_date
    ? new Date(snapshot.snapshot_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
    : null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: T.amber, fontWeight: 800 }}>
              Competitive Intelligence &amp; Benchmarking
            </span>
            {snapshot && (
              <span style={{ fontSize: '0.68rem', fontWeight: 800, color: T.emerald, background: 'rgba(16,185,129,0.15)', padding: '2px 6px', borderRadius: '4px' }}>
                Snapshot: {snapshotDate}
              </span>
            )}
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: T.white, margin: '4px 0 0 0' }}>
            Industry Benchmarks &amp; Competitive Positioning
          </h1>
        </div>

        {snapshotQuery.isFetching && (
          <div style={{ fontSize: '0.75rem', color: T.slate, display: 'flex', alignItems: 'center', gap: '6px' }}>
            <RefreshCw size={12} style={{ animation: 'spin 1s linear infinite' }} />
            Refreshing
          </div>
        )}
      </div>

      {/* Error Banner */}
      {isError && (
        <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '10px', padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}>
          <div style={{ fontSize: '0.85rem', color: '#FCA5A5' }}>
            <strong>Failed to load competitive intelligence data.</strong> The benchmark endpoints require authentication.
          </div>
          <button
            onClick={() => { snapshotQuery.refetch(); comparisonsQuery.refetch(); opportunitiesQuery.refetch(); }}
            style={{ padding: '6px 14px', background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.4)', borderRadius: '6px', color: '#FCA5A5', fontSize: '0.78rem', fontWeight: 700, cursor: 'pointer', whiteSpace: 'nowrap' }}
          >
            Retry
          </button>
        </div>
      )}

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        {isLoading ? (
          <>
            {[1, 2, 3, 4].map((i) => (
              <div key={i} style={{ background: T.cardBg, border: `1px solid ${T.border}`, borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <PulseSkeleton height="14px" width="55%" />
                <PulseSkeleton height="40px" />
                <PulseSkeleton height="12px" width="70%" />
              </div>
            ))}
          </>
        ) : (
          <>
            <MetricCard
              label="Industry Rank"
              value={snapshot ? `#${snapshot.market_rank} of ${snapshot.total_tracked_competitors}` : '—'}
              sublabel={snapshot ? `${snapshot.percentile.toFixed(1)}th Industry Percentile` : 'Live market ranking'}
              color={T.amber}
            />
            <MetricCard
              label="Discovered Revenue Opportunity"
              value={
                opportunities.length > 0
                  ? `+$${opportunities.reduce((sum, o) => sum + o.potential_arr_gain, 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}`
                  : '—'
              }
              sublabel={opportunities.length > 0 ? `Across ${opportunities.length} benchmark gap${opportunities.length !== 1 ? 's' : ''}` : 'No opportunities computed yet'}
              color={T.sky}
            />
            <MetricCard
              label="Competitive Tiers"
              value={
                comparisons.length > 0
                  ? `${comparisons.filter((c) => !c.performance_tier.toUpperCase().includes('LAGGING') && !c.performance_tier.toUpperCase().includes('BELOW')).length} Leader`
                  : '—'
              }
              sublabel={
                comparisons.length > 0
                  ? `${comparisons.filter((c) => c.performance_tier.toUpperCase().includes('LAGGING') || c.performance_tier.toUpperCase().includes('BELOW')).length} Median Lagging`
                  : 'Benchmark comparisons loading'
              }
              color={T.emerald}
            />
            <MetricCard
              label="SWOT Synthesis"
              value={snapshot ? 'Live' : '—'}
              sublabel={snapshot ? `${snapshot.swot_strengths.length + snapshot.swot_weaknesses.length + snapshot.swot_opportunities.length + snapshot.swot_threats.length} Active SWOT Items` : 'Continuously re-indexed'}
              color={T.purple}
            />
          </>
        )}
      </div>

      {/* Benchmark Scorecard Table */}
      <div style={{ background: T.cardBg, border: `1px solid ${T.border}`, borderRadius: '14px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: T.white }}>Competitive Scorecards &amp; Digital Twin Feeder</span>
          <span style={{ fontSize: '0.75rem', color: T.slate }}>Benchmark Gap → Scenario Pipeline</span>
        </div>

        {isLoading ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {[1, 2, 3].map((i) => <PulseSkeleton key={i} height="72px" />)}
          </div>
        ) : comparisons.length === 0 ? (
          <div style={{ padding: '32px', textAlign: 'center', color: T.slate, fontSize: '0.9rem' }}>
            {isError ? 'Could not load benchmark comparisons.' : 'No competitive intelligence data available.'}
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {comparisons.map((item) => {
              // Find matching opportunity for this metric (to surface scenario link)
              const matchedOpportunity = opportunities.find((o) => o.benchmark_id === item.id || o.target_metric === item.metric_name);
              const isLagging = item.performance_tier.toUpperCase().includes('LAGGING') || item.performance_tier.toUpperCase().includes('BELOW');
              const color = tierColor(item.performance_tier);

              return (
                <div
                  key={item.id}
                  style={{
                    background: 'rgba(15,23,42,0.6)',
                    border: `1px solid ${T.border}`,
                    borderRadius: '10px',
                    padding: '18px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    flexWrap: 'wrap',
                    gap: '14px',
                  }}
                >
                  <div>
                    <div style={{ fontSize: '1rem', fontWeight: 800, color: T.white }}>{item.metric_name}</div>
                    <div style={{ fontSize: '0.78rem', color: '#94A3B8', marginTop: '2px' }}>
                      Our Value: <strong style={{ color: T.white }}>{item.our_value}</strong> •
                      Median: {item.industry_median} •
                      Top Quartile: {item.top_quartile} •
                      Best in Class: {item.best_in_class}
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                    <span style={{
                      fontSize: '0.75rem',
                      fontWeight: 800,
                      padding: '4px 10px',
                      borderRadius: '6px',
                      background: isLagging ? 'rgba(239,68,68,0.15)' : 'rgba(16,185,129,0.15)',
                      color: isLagging ? T.rose : T.emerald,
                    }}>
                      {item.gap_to_median > 0 ? '+' : ''}{item.gap_to_median.toFixed(1)} vs Median
                    </span>

                    <span style={{
                      fontSize: '0.72rem',
                      fontWeight: 800,
                      padding: '4px 8px',
                      borderRadius: '6px',
                      background: `${color}18`,
                      color,
                    }}>
                      {item.performance_tier.replace(/_/g, ' ')}
                    </span>

                    {matchedOpportunity ? (
                      <button
                        onClick={() => {
                          if (matchedOpportunity.auto_scenario_id) {
                            setGeneratedScenarioId(matchedOpportunity.auto_scenario_id);
                          } else {
                            setGeneratedScenarioId(matchedOpportunity.id);
                          }
                        }}
                        style={{
                          padding: '8px 12px',
                          background: 'rgba(56,189,248,0.1)',
                          border: '1px solid rgba(56,189,248,0.3)',
                          borderRadius: '8px',
                          color: T.sky,
                          fontSize: '0.75rem',
                          fontWeight: 700,
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px',
                        }}
                      >
                        <Sparkles size={14} />
                        <span>
                          Generate Scenario (+${matchedOpportunity.potential_arr_gain.toLocaleString('en-US', { maximumFractionDigits: 0 })} ARR)
                        </span>
                      </button>
                    ) : isLagging ? (
                      <button
                        onClick={() => setGeneratedScenarioId(item.id)}
                        style={{
                          padding: '8px 12px',
                          background: 'rgba(56,189,248,0.1)',
                          border: '1px solid rgba(56,189,248,0.3)',
                          borderRadius: '8px',
                          color: T.sky,
                          fontSize: '0.75rem',
                          fontWeight: 700,
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px',
                        }}
                      >
                        <Sparkles size={14} />
                        <span>Generate Scenario</span>
                      </button>
                    ) : null}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Scenario generated confirmation */}
        {generatedScenarioId && (
          <div style={{ background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)', padding: '14px 18px', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CheckCircle2 size={16} color={T.emerald} />
              <span style={{ fontSize: '0.82rem', color: '#F1F5F9' }}>
                Digital Twin Scenario dispatched to Scenario Studio.
              </span>
            </div>
            <Link
              to="/scenarios"
              style={{ color: T.emerald, fontSize: '0.78rem', fontWeight: 800, textDecoration: 'none' }}
            >
              View in Scenario Studio →
            </Link>
          </div>
        )}
      </div>

      {/* Opportunity Cards */}
      {!isLoading && opportunities.length > 0 && (
        <div style={{ background: T.cardBg, border: `1px solid ${T.border}`, borderRadius: '14px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '1rem', fontWeight: 800, color: T.white }}>Benchmark Revenue Opportunity Radar</span>
            <span style={{ fontSize: '0.75rem', color: T.slate }}>Auto-Generated from Benchmark Gap Analysis</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px' }}>
            {opportunities.map((opp) => (
              <div
                key={opp.id}
                style={{
                  background: 'rgba(15,23,42,0.6)',
                  border: `1px solid ${T.border}`,
                  borderRadius: '10px',
                  padding: '16px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '8px' }}>
                  <span style={{ fontSize: '0.9rem', fontWeight: 800, color: T.white, flex: 1 }}>{opp.opportunity_title}</span>
                  <span style={{
                    fontSize: '0.68rem',
                    fontWeight: 800,
                    padding: '2px 8px',
                    borderRadius: '4px',
                    background: `${difficultyColor(opp.difficulty_tier)}20`,
                    color: difficultyColor(opp.difficulty_tier),
                    whiteSpace: 'nowrap',
                  }}>
                    {opp.difficulty_tier}
                  </span>
                </div>

                <div style={{ fontSize: '0.76rem', color: '#94A3B8' }}>
                  Metric: <strong style={{ color: T.sky }}>{opp.target_metric}</strong>
                </div>

                <div style={{ fontSize: '1.5rem', fontWeight: 900, color: T.emerald }}>
                  +${opp.potential_arr_gain.toLocaleString('en-US', { maximumFractionDigits: 0 })} ARR
                </div>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '4px' }}>
                  <span style={{
                    fontSize: '0.7rem',
                    fontWeight: 800,
                    color: opp.status === 'OPEN' ? T.sky : T.slate,
                    background: opp.status === 'OPEN' ? 'rgba(56,189,248,0.1)' : 'rgba(100,116,139,0.1)',
                    padding: '2px 8px',
                    borderRadius: '4px',
                  }}>
                    {opp.status}
                  </span>
                  {opp.auto_scenario_id && (
                    <Link
                      to="/scenarios"
                      style={{ fontSize: '0.74rem', color: T.emerald, fontWeight: 800, textDecoration: 'none' }}
                    >
                      View Scenario →
                    </Link>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SWOT Analysis Panel — fully live from CompetitiveSnapshotResponse */}
      {!isLoading && snapshot && (
        <div style={{ background: T.cardBg, border: `1px solid ${T.border}`, borderRadius: '14px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '1rem', fontWeight: 800, color: T.white }}>Autonomous SWOT Analysis</span>
            <span style={{ fontSize: '0.75rem', color: T.slate }}>Continuously Re-Indexed · {snapshotDate}</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '12px' }}>
            <SwotQuadrant
              title="Strengths"
              items={snapshot.swot_strengths}
              color={T.emerald}
              icon={<ShieldCheck size={16} color={T.emerald} />}
            />
            <SwotQuadrant
              title="Weaknesses"
              items={snapshot.swot_weaknesses}
              color={T.rose}
              icon={<AlertTriangle size={16} color={T.rose} />}
            />
            <SwotQuadrant
              title="Opportunities"
              items={snapshot.swot_opportunities}
              color={T.sky}
              icon={<Lightbulb size={16} color={T.sky} />}
            />
            <SwotQuadrant
              title="Threats"
              items={snapshot.swot_threats}
              color={T.amber}
              icon={<Zap size={16} color={T.amber} />}
            />
          </div>
        </div>
      )}
    </div>
  );
};
