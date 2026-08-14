import React, { forwardRef } from 'react';
import {
  ExecutiveReportData,
  ReportSectionConfig,
} from '../../types';
import { HealthScoreGauge } from '../metrics/HealthScoreGauge';
import { ConfidenceBandChart } from '../charts/ConfidenceBandChart';
import {
  Activity,
  ShieldAlert,
  GitMerge,
  CheckCircle2,
  Sparkles,
  Compass,
  Sliders,
  TrendingUp,
  FileText,
  Lock,
} from 'lucide-react';

interface ExecutiveReportDocumentProps {
  data: ExecutiveReportData;
  config?: ReportSectionConfig;
}

export const ExecutiveReportDocument = forwardRef<HTMLDivElement, ExecutiveReportDocumentProps>(
  ({ data, config }, ref) => {
    const {
      dataset,
      health,
      executiveSummary,
      intelligenceReport,
      rootCausesResponse,
      aiInsight,
      strategyPlan,
      scenarios = [],
      forecasts = [],
      generatedAt,
      reportId,
      generatedBy,
    } = data;

    const showSummary = config?.includeExecutiveSummary ?? true;
    const showMetrics = config?.includeMetrics ?? true;
    const showDiagnostics = config?.includeDiagnostics ?? true;
    const showRootCauses = config?.includeRootCauses ?? true;
    const showRecommendations = config?.includeRecommendations ?? true;
    const showAI = config?.includeAIInsights ?? true;
    const showStrategy = config?.includeStrategyPlan ?? true;
    const showScenarios = config?.includeScenarios ?? true;
    const showForecasts = config?.includeForecasts ?? true;

    const metrics = intelligenceReport?.metrics || [];
    const findings = intelligenceReport?.findings || [];
    const recommendations = intelligenceReport?.recommendations || [];
    const analyses = rootCausesResponse?.analyses || [];
    const summaries = rootCausesResponse?.summaries || [];

    const formatMetricValue = (key: string, val: number, unit?: string) => {
      if (unit) return `${val.toLocaleString()} ${unit}`;
      if (key.includes('revenue') || key.includes('cost') || key.includes('price')) {
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);
      }
      if (key.includes('rate') || key.includes('percentage') || key.includes('margin')) {
        return `${val.toFixed(1)}%`;
      }
      return Number.isInteger(val) ? val.toLocaleString() : val.toFixed(2);
    };

    return (
      <div ref={ref} className="report-document">
        {/* Cover / Header Banner */}
        <div className="report-header-banner">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span className="badge badge-primary">DecisionOS Executive Briefing</span>
              <span className="badge badge-neutral">Confidential</span>
            </div>
            <h1 style={{ fontSize: '1.8rem', color: '#ffffff', marginBottom: '4px' }}>
              Executive Decision Intelligence Report
            </h1>
            <h2 style={{ fontSize: '1.1rem', color: 'var(--color-primary-light)', fontWeight: 500 }}>
              Dataset: {dataset.name}
            </h2>
          </div>

          <div style={{ textAlign: 'right', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            <div><strong>Report ID:</strong> {reportId}</div>
            <div><strong>Generated:</strong> {new Date(generatedAt).toLocaleString()}</div>
            <div><strong>Prepared For:</strong> {generatedBy}</div>
          </div>
        </div>

        {/* Section 1: Executive Briefing */}
        {showSummary && (
          <section className="report-section">
            <h3 className="report-section-title">
              <Activity size={18} color="var(--color-primary-light)" />
              <span>1. Executive Summary & Business Health</span>
            </h3>

            <div className="report-grid-2" style={{ marginBottom: '16px' }}>
              <div className="card-elevated">
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                  Business Health Score
                </span>
                <div style={{ marginTop: '14px' }}>
                  <HealthScoreGauge score={health.score} status={health.status} />
                </div>
              </div>

              <div className="card-elevated" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      Primary Risk Diagnosis
                    </span>
                    <span className="badge badge-danger">
                      Confidence: {(executiveSummary.overall_confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  <h4 style={{ fontSize: '1.05rem', color: '#ffffff', marginBottom: '6px' }}>
                    {executiveSummary.primary_issue}
                  </h4>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                    {executiveSummary.expected_business_impact}
                  </p>
                </div>

                <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '10px', marginTop: '10px', fontSize: '0.8rem' }}>
                  {executiveSummary.top_root_cause && (
                    <div style={{ marginBottom: '4px' }}>
                      <strong style={{ color: 'var(--color-warning)' }}>Top Root Cause: </strong>
                      <span style={{ color: 'var(--text-main)' }}>{executiveSummary.top_root_cause}</span>
                    </div>
                  )}
                  {executiveSummary.top_recommendation && (
                    <div>
                      <strong style={{ color: 'var(--color-success)' }}>Top Action: </strong>
                      <span style={{ color: 'var(--text-main)' }}>{executiveSummary.top_recommendation}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Section 2: Core KPI Performance */}
        {showMetrics && (
          <section className="report-section">
            <h3 className="report-section-title">
              <Activity size={18} color="var(--color-primary-light)" />
              <span>2. Core KPI Performance Indicators</span>
            </h3>

            {metrics.length > 0 ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
                {metrics.map((m) => (
                  <div key={m.id || m.metric_key} className="card" style={{ padding: '12px 16px' }}>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      {m.metric_category || 'GENERAL'}
                    </div>
                    <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-main)', margin: '4px 0' }}>
                      {m.metric_name}
                    </div>
                    <div style={{ fontSize: '1.3rem', fontWeight: 800, color: '#ffffff' }}>
                      {formatMetricValue(m.metric_key, m.metric_value, m.unit)}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="card" style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '16px' }}>
                No KPI metrics calculated for this dataset.
              </div>
            )}
          </section>
        )}

        {/* Section 3: Diagnostic Findings */}
        {showDiagnostics && (
          <section className="report-section">
            <h3 className="report-section-title">
              <ShieldAlert size={18} color="var(--color-danger)" />
              <span>3. Business Diagnostic Findings</span>
            </h3>

            {findings.length > 0 ? (
              <table className="report-table">
                <thead>
                  <tr>
                    <th>SEVERITY</th>
                    <th>FINDING TITLE</th>
                    <th>TYPE</th>
                    <th>CONFIDENCE</th>
                    <th>BUSINESS IMPACT</th>
                  </tr>
                </thead>
                <tbody>
                  {findings.map((f) => (
                    <tr key={f.id}>
                      <td>
                        <span
                          className={`badge ${
                            f.severity === 'CRITICAL' || f.severity === 'HIGH'
                              ? 'badge-danger'
                              : f.severity === 'MEDIUM'
                              ? 'badge-warning'
                              : 'badge-primary'
                          }`}
                        >
                          {f.severity}
                        </span>
                      </td>
                      <td style={{ fontWeight: 600 }}>{f.title}</td>
                      <td style={{ color: 'var(--text-muted)' }}>{f.finding_type}</td>
                      <td>{(f.confidence_score * 100).toFixed(0)}%</td>
                      <td style={{ color: 'var(--text-secondary)' }}>{f.business_impact}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="card" style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '16px' }}>
                No diagnostic anomalies detected.
              </div>
            )}
          </section>
        )}

        {/* Section 4: Root Cause Analysis */}
        {showRootCauses && (
          <section className="report-section">
            <h3 className="report-section-title">
              <GitMerge size={18} color="var(--color-warning)" />
              <span>4. Root Cause Causal Reasoning</span>
            </h3>

            {analyses.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {analyses.map((ana, idx) => (
                  <div key={ana.id} className="card" style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span className="badge badge-warning">Cause #{idx + 1}</span>
                        <span style={{ fontWeight: 600, color: '#ffffff' }}>
                          {ana.root_cause_finding?.title || 'Root Cause'}
                        </span>
                        <span style={{ color: 'var(--text-muted)' }}>→</span>
                        <span style={{ color: 'var(--color-danger)', fontWeight: 500 }}>
                          {ana.primary_finding?.title || 'Business Symptom'}
                        </span>
                      </div>
                      <span className="badge badge-neutral">Strength: {ana.relationship_strength}</span>
                    </div>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                      {ana.explanation}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="card" style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '16px' }}>
                No causal linkages identified meeting confidence thresholds.
              </div>
            )}
          </section>
        )}

        {/* Section 5: Actionable Recommendations */}
        {showRecommendations && (
          <section className="report-section">
            <h3 className="report-section-title">
              <CheckCircle2 size={18} color="var(--color-success)" />
              <span>5. Prescribed Actionable Recommendations</span>
            </h3>

            {recommendations.length > 0 ? (
              <table className="report-table">
                <thead>
                  <tr>
                    <th>PRIORITY</th>
                    <th>RECOMMENDATION</th>
                    <th>EXPECTED IMPACT</th>
                    <th>EFFORT</th>
                    <th>TIME TO VALUE</th>
                  </tr>
                </thead>
                <tbody>
                  {recommendations.map((r) => (
                    <tr key={r.id}>
                      <td>
                        <span
                          className={`badge ${
                            r.priority === 'CRITICAL'
                              ? 'badge-danger'
                              : r.priority === 'HIGH'
                              ? 'badge-warning'
                              : 'badge-primary'
                          }`}
                        >
                          {r.priority}
                        </span>
                      </td>
                      <td>
                        <div style={{ fontWeight: 600 }}>{r.title}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{r.action_summary}</div>
                      </td>
                      <td style={{ color: 'var(--color-success)', fontWeight: 600 }}>{r.expected_impact}</td>
                      <td>{r.estimated_effort}</td>
                      <td>{r.time_to_value}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="card" style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '16px' }}>
                No recommendations prescribed for this dataset yet.
              </div>
            )}
          </section>
        )}

        {/* Section 6: AI Executive Insights (Clearly Labeled AI) */}
        {showAI && aiInsight && (
          <section className="report-section">
            <h3 className="report-section-title">
              <Sparkles size={18} color="var(--color-ai-light)" />
              <span>6. AI-Generated Executive Narrative & Assessment</span>
            </h3>

            <div className="card-elevated card-ai" style={{ marginBottom: '14px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span className="badge badge-ai">✨ AI Synthesis Layer</span>
                <span style={{ fontSize: '0.7rem', color: 'var(--color-ai-light)' }}>
                  Model: {aiInsight.model_name}
                </span>
              </div>
              <p style={{ fontSize: '0.95rem', color: '#ffffff', lineHeight: 1.6 }}>
                {aiInsight.executive_narrative}
              </p>
            </div>

            {aiInsight.key_takeaways && aiInsight.key_takeaways.length > 0 && (
              <div className="card" style={{ marginBottom: '12px' }}>
                <strong style={{ fontSize: '0.85rem', color: '#ffffff' }}>Strategic Key Takeaways:</strong>
                <ul style={{ marginTop: '6px', paddingLeft: '20px', fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {aiInsight.key_takeaways.map((point, idx) => (
                    <li key={idx}>{point}</li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}

        {/* Section 7: 90-Day Strategy Roadmap */}
        {showStrategy && strategyPlan && (
          <section className="report-section">
            <h3 className="report-section-title">
              <Compass size={18} color="var(--color-primary-light)" />
              <span>7. 90-Day Strategic Execution Roadmap</span>
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {(strategyPlan.strategic_milestones || []).map((m, idx) => (
                <div key={idx} className="card" style={{ padding: '12px 16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                    <span className="badge badge-primary">{m.horizon}</span>
                    <strong style={{ color: '#ffffff' }}>{m.theme}</strong>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginTop: '6px' }}>
                    {m.actions.map((act, aIdx) => (
                      <div key={aIdx} style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                        • <strong>{act.title}:</strong> {act.description}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Section 8: What-If Scenario Simulations (Explicitly Labeled Projections) */}
        {showScenarios && scenarios.length > 0 && (
          <section className="report-section">
            <h3 className="report-section-title">
              <Sliders size={18} color="var(--color-primary-light)" />
              <span>8. What-If Scenario Simulations (Projected Outcomes)</span>
            </h3>

            <div
              style={{
                fontSize: '0.75rem',
                backgroundColor: 'rgba(37, 99, 235, 0.08)',
                border: '1px solid var(--border-default)',
                padding: '8px 12px',
                borderRadius: 'var(--radius-sm)',
                marginBottom: '12px',
                color: 'var(--color-primary-light)',
              }}
            >
              ⚠️ <strong>NOTICE:</strong> Scenario simulations represent hypothetical mathematical projections and do NOT alter historical actuals.
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {scenarios.slice(0, 2).map((sc) => (
                <div key={sc.id} className="card" style={{ padding: '12px 16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <div>
                      <span className="badge badge-primary" style={{ marginRight: '6px' }}>
                        Scenario: {sc.name}
                      </span>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{sc.description}</span>
                    </div>
                    <span className="badge badge-success">
                      Projected Health: {sc.projected_health_score}/100
                    </span>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '8px', marginTop: '8px' }}>
                    {Object.entries(sc.projected_metrics || {}).slice(0, 4).map(([k, v]: [string, any]) => (
                      <div key={k} style={{ backgroundColor: 'var(--bg-app)', padding: '6px 10px', borderRadius: 'var(--radius-sm)', fontSize: '0.75rem' }}>
                        <span style={{ color: 'var(--text-muted)' }}>{k}: </span>
                        <strong style={{ color: '#ffffff' }}>{typeof v === 'number' ? v.toLocaleString() : v}</strong>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Section 9: Statistical Time-Series Forecasts */}
        {showForecasts && forecasts.length > 0 && (
          <section className="report-section">
            <h3 className="report-section-title">
              <TrendingUp size={18} color="var(--color-primary-light)" />
              <span>9. Statistical Time-Series Forecasts</span>
            </h3>

            <div
              style={{
                fontSize: '0.75rem',
                backgroundColor: 'rgba(6, 182, 212, 0.08)',
                border: '1px solid var(--border-default)',
                padding: '8px 12px',
                borderRadius: 'var(--radius-sm)',
                marginBottom: '12px',
                color: 'var(--color-info)',
              }}
            >
              📊 <strong>STATISTICAL PROJECTION:</strong> Generated via backtested deterministic time-series algorithms ({forecasts[0].model_name}, RMSE: {forecasts[0].model_metrics.rmse}).
            </div>

            <div className="card" style={{ padding: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                <span className="badge badge-primary">{forecasts[0].metric_key}</span>
                <span className="badge badge-neutral">Horizon: {forecasts[0].horizon}</span>
                <span className="badge badge-neutral">Confidence: {Math.round(forecasts[0].confidence_level * 100)}%</span>
              </div>

              <div style={{ backgroundColor: 'var(--bg-app)', padding: '12px', borderRadius: 'var(--radius-md)' }}>
                <ConfidenceBandChart
                  points={forecasts[0].forecast_points}
                  metricKey={forecasts[0].metric_key}
                  height={180}
                />
              </div>
            </div>
          </section>
        )}

        {/* Section 10: Appendix & Audit Trail */}
        <section className="report-section" style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <Lock size={14} color="var(--text-muted)" />
            <strong style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Appendix & Data Provenance</strong>
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            Dataset ID: <code>{dataset.id}</code> | Original Source: <code>{dataset.original_filename}</code> | Size: {(dataset.file_size / 1024).toFixed(1)} KB | Ingestion Timestamp: {new Date(dataset.created_at).toLocaleString()} | Generated by DecisionOS Engine v1.0.0. All analytics computed deterministically under dataset isolation protocols.
          </div>
        </section>
      </div>
    );
  }
);
