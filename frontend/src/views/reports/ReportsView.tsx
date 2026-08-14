import React, { useEffect, useState, useRef } from 'react';
import { useDataset } from '../../context/DatasetContext';
import { useAuth } from '../../context/AuthContext';
import { aggregateReportData } from '../../services/reportAggregator';
import { ExecutiveReportData, ReportSectionConfig } from '../../types';
import { ExecutiveReportDocument } from '../../components/report/ExecutiveReportDocument';
import { LoadingSkeleton } from '../../components/feedback/LoadingSkeleton';
import { ErrorBanner } from '../../components/feedback/ErrorBanner';
import { EmptyState } from '../../components/feedback/EmptyState';
import { Printer, Download, FileText, CheckSquare, Square, RefreshCw, Eye } from 'lucide-react';
import { useReactToPrint } from 'react-to-print';
import '../../styles/report.css';

export const ReportsView: React.FC = () => {
  const { activeDataset } = useDataset();
  const { user } = useAuth();
  const [reportData, setReportData] = useState<ExecutiveReportData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Section Config State
  const [config, setConfig] = useState<ReportSectionConfig>({
    includeExecutiveSummary: true,
    includeMetrics: true,
    includeDiagnostics: true,
    includeRootCauses: true,
    includeRecommendations: true,
    includeAIInsights: true,
    includeStrategyPlan: true,
    includeScenarios: true,
    includeForecasts: true,
  });

  const reportRef = useRef<HTMLDivElement>(null);

  const handlePrint = useReactToPrint({
    contentRef: reportRef,
    documentTitle: `DecisionOS_Executive_Report_${activeDataset?.name || 'Dataset'}`,
  });

  const loadReport = async (dataset = activeDataset) => {
    if (!dataset) return;
    try {
      setLoading(true);
      setError(null);
      const data = await aggregateReportData(dataset, user?.email || 'executive@decisionos.ai');
      setReportData(data);
    } catch (err: any) {
      console.error('Failed to load executive report data:', err);
      setError(err?.message || 'Could not compile executive report for this dataset.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeDataset?.id) {
      loadReport(activeDataset);
    } else {
      setLoading(false);
    }
  }, [activeDataset?.id]);

  const toggleSection = (key: keyof ReportSectionConfig) => {
    setConfig((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  if (!activeDataset) {
    return (
      <div className="page-container">
        <EmptyState
          title="No Active Dataset Selected"
          description="Select a dataset to compile and export its executive decision intelligence briefing."
          icon={FileText}
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
            <span className="badge badge-primary">Phase 7.2 Report Exports</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Executive PDF & Boardroom Synthesis
            </span>
          </div>
          <h1>Executive Report Studio</h1>
          <p style={{ marginTop: '4px', fontSize: '0.9rem' }}>
            Consolidate deterministic diagnostics, root causes, recommendations, and AI assessments into a downloadable PDF report.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={() => loadReport()} className="btn btn-secondary btn-sm" title="Refresh intelligence data">
            <RefreshCw size={14} />
            <span>Refresh</span>
          </button>

          <button
            onClick={() => handlePrint()}
            disabled={loading || !reportData}
            className="btn btn-primary"
            style={{ gap: '8px' }}
          >
            <Download size={16} />
            <span>Export Executive PDF</span>
          </button>
        </div>
      </div>

      {error && <ErrorBanner message={error} onRetry={() => loadReport()} />}

      {/* Control Panel: Section Selection */}
      <div
        className="card"
        style={{
          marginBottom: '24px',
          padding: '14px 20px',
          backgroundColor: 'var(--bg-surface-elevated)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
          <Eye size={16} color="var(--color-primary-light)" />
          <strong style={{ fontSize: '0.85rem', color: '#ffffff' }}>Include Report Sections:</strong>
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
          {[
            { key: 'includeExecutiveSummary', label: 'Executive Summary' },
            { key: 'includeMetrics', label: 'KPI Metrics' },
            { key: 'includeDiagnostics', label: 'Diagnostics' },
            { key: 'includeRootCauses', label: 'Root Causes' },
            { key: 'includeRecommendations', label: 'Recommendations' },
            { key: 'includeAIInsights', label: 'AI Narrative' },
            { key: 'includeStrategyPlan', label: 'Strategy Roadmap' },
            { key: 'includeScenarios', label: 'Scenarios' },
            { key: 'includeForecasts', label: 'Forecasts' },
          ].map(({ key, label }) => {
            const isChecked = config[key as keyof ReportSectionConfig];
            return (
              <button
                key={key}
                onClick={() => toggleSection(key as keyof ReportSectionConfig)}
                className="btn btn-ghost btn-sm"
                style={{
                  padding: '4px 8px',
                  fontSize: '0.8rem',
                  gap: '6px',
                  color: isChecked ? 'var(--text-main)' : 'var(--text-muted)',
                  backgroundColor: isChecked ? 'var(--bg-app)' : 'transparent',
                }}
              >
                {isChecked ? (
                  <CheckSquare size={14} color="var(--color-primary-light)" />
                ) : (
                  <Square size={14} color="var(--text-muted)" />
                )}
                <span>{label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Live Preview Document */}
      {loading ? (
        <LoadingSkeleton count={5} height="140px" />
      ) : reportData ? (
        <div style={{ overflowX: 'auto', paddingBottom: '40px' }}>
          <ExecutiveReportDocument ref={reportRef} data={reportData} config={config} />
        </div>
      ) : (
        <EmptyState
          title="No Intelligence Ready to Export"
          description="Please compute diagnostics and KPI metrics for this dataset first."
          icon={FileText}
        />
      )}
    </div>
  );
};
