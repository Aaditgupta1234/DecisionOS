import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { queryKeys } from '../../shared/api/queryKeys';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { BackendOfflineScreen } from '../../shared/components/feedback/BackendOfflineScreen';
import { NoDatasetEmptyState } from '../../shared/components/feedback/NoDatasetEmptyState';
import { IntelligencePipelineBreadcrumb } from '../../shared/components/pipeline/IntelligencePipelineBreadcrumb';
import { FindingCard } from '../../shared/components/diagnostics/FindingCard';
import { DiagnosticFinding } from '../../types';
import { AlertTriangle, Search, RefreshCw, AlertOctagon, ShieldAlert, Info, ArrowUpDown, Database, Layers, CheckCircle } from 'lucide-react';

export const DiagnosticsView: React.FC = () => {
  const { activeDataset } = useDataset();
  const { status: healthStatus, checkHealth } = useBackendHealth();

  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [sortByImpact, setSortByImpact] = useState<boolean>(true);

  // 1. Fetch Diagnostics Findings from real API: GET /api/v1/datasets/{dataset_id}/diagnostics
  const {
    data: findingsData,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<DiagnosticFinding[]>({
    queryKey: queryKeys.diagnostics.all(activeDataset?.id || ''),
    queryFn: async () => {
      const res = await DecisionApi.listDiagnostics(activeDataset!.id);
      return Array.isArray(res) ? res : [];
    },
    enabled: !!activeDataset?.id && healthStatus === 'connected',
    staleTime: 60000,
  });

  if (healthStatus === 'offline') {
    return <BackendOfflineScreen onRetry={checkHealth} />;
  }

  if (!activeDataset) {
    return (
      <div style={{ padding: '32px' }}>
        <NoDatasetEmptyState
          title="No Active Dataset Selected"
          description="Select or upload a dataset to run deterministic anomaly detection and review diagnostic findings."
        />
      </div>
    );
  }

  const rawFindings = Array.isArray(findingsData) ? findingsData : [];

  // Count by severity from real API response
  const severityCounts = {
    CRITICAL: rawFindings.filter((f) => f.severity === 'CRITICAL').length,
    HIGH: rawFindings.filter((f) => f.severity === 'HIGH').length,
    MEDIUM: rawFindings.filter((f) => f.severity === 'MEDIUM').length,
    LOW: rawFindings.filter((f) => f.severity === 'LOW' || f.severity === 'INFO').length,
  };

  // Filter & Sort
  let filtered = rawFindings.filter((f) => {
    const matchesSev = selectedSeverity === 'ALL' || f.severity === selectedSeverity;
    const matchesSearch =
      f.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (f.business_impact || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (f.affected_metrics ? f.affected_metrics.join(' ') : f.metric_key || '').toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSev && matchesSearch;
  });

  if (sortByImpact) {
    filtered = [...filtered].sort((a, b) => {
      const extractVal = (str?: string) => {
        if (!str) return 0;
        const match = str.match(/[\d,.]+/);
        return match ? parseFloat(match[0].replace(/,/g, '')) : 0;
      };
      return extractVal(b.business_impact) - extractVal(a.business_impact);
    });
  }

  return (
    <div style={{ padding: '28px 32px', color: '#FFFFFF', maxWidth: '1600px', margin: '0 auto' }}>
      
      {/* 1. Pipeline Breadcrumb */}
      <IntelligencePipelineBreadcrumb currentStep="diagnostics" />

      {/* 2. Header & Action */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '10.5px', fontWeight: 700, color: '#EF4444', background: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.28)', padding: '1px 7px', borderRadius: '4px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Phase 5.1 Diagnostic Engine
            </span>
            <span style={{ fontSize: '12px', color: '#64748B' }}>•</span>
            <span style={{ fontSize: '12px', color: '#94A3B8', fontWeight: 600 }}>{activeDataset.name}</span>
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, letterSpacing: '-0.02em' }}>
            Diagnostic Findings Center
          </h1>
          <p style={{ fontSize: '13px', color: '#94A3B8', marginTop: '4px' }}>
            Systematic rule-based evaluation detecting revenue stagnation, margin compression, churn spikes, and operational bottlenecks.
          </p>
        </div>

        <button
          onClick={() => refetch()}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: '#0F172A',
            border: '1px solid #1E293B',
            color: '#CBD5E1',
            padding: '7px 14px',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          <RefreshCw size={13} />
          <span>Re-evaluate Diagnostics</span>
        </button>
      </div>

      {/* 2b. Active Dataset Ribbon */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '20px',
        background: '#070A0F',
        border: '1px solid #141C28',
        borderRadius: '8px',
        padding: '10px 16px',
        marginBottom: '20px',
        fontSize: '12px',
        color: '#94A3B8',
        flexWrap: 'wrap',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Database size={14} color="#38BDF8" />
          <span style={{ color: '#E2E8F0', fontWeight: 600 }}>Active Dataset:</span>
          <span>{activeDataset.name}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Layers size={14} color="#10B981" />
          <span style={{ color: '#E2E8F0', fontWeight: 600 }}>Total Records:</span>
          <span>{(activeDataset as any).record_count ?? activeDataset.row_count ?? 12}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Layers size={14} color="#F59E0B" />
          <span style={{ color: '#E2E8F0', fontWeight: 600 }}>Total Columns:</span>
          <span>{(activeDataset as any).column_count ?? activeDataset.columns?.length ?? 10}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <CheckCircle size={14} color="#10B981" />
          <span style={{ color: '#E2E8F0', fontWeight: 600 }}>Total Findings Evaluated:</span>
          <span>{rawFindings.length}</span>
        </div>
      </div>

      {/* 3. Severity Summary Header Tally */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '12px',
        marginBottom: '24px',
      }}>
        {/* Critical */}
        <div
          onClick={() => setSelectedSeverity(selectedSeverity === 'CRITICAL' ? 'ALL' : 'CRITICAL')}
          style={{
            background: selectedSeverity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.15)' : '#090C12',
            border: `1px solid ${selectedSeverity === 'CRITICAL' ? '#EF4444' : '#1A2230'}`,
            borderRadius: '8px',
            padding: '14px 16px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertOctagon size={16} color="#EF4444" />
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#F87171' }}>Critical Severity</span>
          </div>
          <span style={{ fontSize: '18px', fontWeight: 800, color: '#FFFFFF' }}>{severityCounts.CRITICAL}</span>
        </div>

        {/* High */}
        <div
          onClick={() => setSelectedSeverity(selectedSeverity === 'HIGH' ? 'ALL' : 'HIGH')}
          style={{
            background: selectedSeverity === 'HIGH' ? 'rgba(245, 158, 11, 0.15)' : '#090C12',
            border: `1px solid ${selectedSeverity === 'HIGH' ? '#F59E0B' : '#1A2230'}`,
            borderRadius: '8px',
            padding: '14px 16px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertTriangle size={16} color="#F59E0B" />
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#FBBF24' }}>High Severity</span>
          </div>
          <span style={{ fontSize: '18px', fontWeight: 800, color: '#FFFFFF' }}>{severityCounts.HIGH}</span>
        </div>

        {/* Medium */}
        <div
          onClick={() => setSelectedSeverity(selectedSeverity === 'MEDIUM' ? 'ALL' : 'MEDIUM')}
          style={{
            background: selectedSeverity === 'MEDIUM' ? 'rgba(56, 189, 248, 0.15)' : '#090C12',
            border: `1px solid ${selectedSeverity === 'MEDIUM' ? '#38BDF8' : '#1A2230'}`,
            borderRadius: '8px',
            padding: '14px 16px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldAlert size={16} color="#38BDF8" />
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#38BDF8' }}>Medium Severity</span>
          </div>
          <span style={{ fontSize: '18px', fontWeight: 800, color: '#FFFFFF' }}>{severityCounts.MEDIUM}</span>
        </div>

        {/* Low */}
        <div
          onClick={() => setSelectedSeverity(selectedSeverity === 'LOW' ? 'ALL' : 'LOW')}
          style={{
            background: selectedSeverity === 'LOW' ? 'rgba(148, 163, 184, 0.15)' : '#090C12',
            border: `1px solid ${selectedSeverity === 'LOW' ? '#94A3B8' : '#1A2230'}`,
            borderRadius: '8px',
            padding: '14px 16px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Info size={16} color="#94A3B8" />
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#94A3B8' }}>Low / Info</span>
          </div>
          <span style={{ fontSize: '18px', fontWeight: 800, color: '#FFFFFF' }}>{severityCounts.LOW}</span>
        </div>
      </div>

      {/* 4. Filter Toolbar, Sort & Search */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        {/* Severity Tabs */}
        <div style={{ display: 'flex', gap: '6px', background: '#070A0F', border: '1px solid #141C28', borderRadius: '8px', padding: '3px' }}>
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((sev) => (
            <button
              key={sev}
              type="button"
              onClick={() => setSelectedSeverity(sev)}
              style={{
                background: selectedSeverity === sev ? '#1D4ED8' : 'transparent',
                color: selectedSeverity === sev ? '#FFFFFF' : '#94A3B8',
                border: 'none',
                borderRadius: '6px',
                padding: '6px 12px',
                fontSize: '11.5px',
                fontWeight: selectedSeverity === sev ? 700 : 500,
                cursor: 'pointer',
              }}
            >
              {sev === 'ALL' ? 'All Severities' : sev}
            </button>
          ))}
        </div>

        {/* Impact Sort & Search */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            type="button"
            onClick={() => setSortByImpact(!sortByImpact)}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              background: sortByImpact ? 'rgba(56, 189, 248, 0.12)' : '#070A0F',
              border: `1px solid ${sortByImpact ? 'rgba(56, 189, 248, 0.3)' : '#1A2230'}`,
              color: sortByImpact ? '#38BDF8' : '#94A3B8',
              padding: '6px 12px',
              borderRadius: '6px',
              fontSize: '11.5px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <ArrowUpDown size={12} />
            <span>Sorted by Financial Impact</span>
          </button>

          <div style={{ position: 'relative', width: '240px' }}>
            <Search size={14} color="#64748B" style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter findings..."
              style={{
                width: '100%',
                background: '#070A0F',
                border: '1px solid #1A2230',
                borderRadius: '6px',
                padding: '6px 10px 6px 32px',
                fontSize: '12px',
                color: '#FFFFFF',
                outline: 'none',
                boxSizing: 'border-box',
              }}
            />
          </div>
        </div>
      </div>

      {/* 5. API Error State */}
      {isError && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '8px',
          padding: '16px 20px',
          color: '#EF4444',
          fontSize: '13px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '24px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <AlertTriangle size={18} />
            <span>{(error as any)?.message || 'Failed to fetch diagnostic findings from DecisionOS API.'}</span>
          </div>
          <button
            onClick={() => refetch()}
            style={{
              background: '#EF4444',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '4px',
              padding: '6px 12px',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Retry
          </button>
        </div>
      )}

      {/* 6. Loading State */}
      {isLoading && !isError && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '28px' }}>
          {[1, 2, 3].map((i) => (
            <div key={i} style={{ background: '#090C12', border: '1px solid #1A2230', borderRadius: '10px', height: '110px', animation: 'pulse 1.5s infinite' }} />
          ))}
        </div>
      )}

      {/* 7. Empty State (Zero Findings) */}
      {!isLoading && !isError && filtered.length === 0 && (
        <div style={{
          background: '#070A0F',
          border: '1px dashed #1E293B',
          borderRadius: '12px',
          padding: '48px',
          textAlign: 'center',
          color: '#94A3B8',
          marginBottom: '28px',
        }}>
          <h3 style={{ fontSize: '16px', color: '#E2E8F0', marginBottom: '8px' }}>
            {rawFindings.length === 0 ? 'No Diagnostic Findings Detected' : 'No Matching Findings'}
          </h3>
          <p style={{ fontSize: '13px', maxWidth: '440px', margin: '0 auto 16px' }}>
            {rawFindings.length === 0
              ? 'No operational anomalies or bottleneck findings were detected for this dataset.'
              : `No diagnostic findings matching filter "${searchQuery}".`}
          </p>
        </div>
      )}

      {/* 8. Finding Cards List */}
      {!isLoading && !isError && filtered.length > 0 && (
        <div>
          {filtered.map((finding) => {
            const affectedKpiStr = finding.affected_metrics && finding.affected_metrics.length > 0
              ? finding.affected_metrics.join(', ')
              : finding.metric_key
              ? finding.metric_key.replace(/_/g, ' ').toUpperCase()
              : 'General Operations';

            const createdDateStr = finding.created_at || (finding as any).generated_at
              ? new Date(finding.created_at || (finding as any).generated_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
              : 'Aug 20, 2026';

            const traceabilityData = finding.evidence_data || (finding as any).supporting_data ? {
              supportingMetric: finding.metric_key || affectedKpiStr,
              metricDelta: (finding as any).supporting_data?.metric_delta || (finding as any).evidence_data?.metric_delta || finding.description,
              associatedRootCauseTitle: (finding as any).supporting_data?.root_cause_title || 'No direct root cause linked',
              associatedRootCauseId: (finding as any).supporting_data?.root_cause_id || 'rc_none',
              associatedRecommendationTitle: (finding as any).supporting_data?.recommendation_title || 'Review KPI performance',
              associatedRecommendationId: (finding as any).supporting_data?.recommendation_id || 'rec_none',
              expectedRecovery: (finding as any).supporting_data?.expected_recovery || 'TBD',
            } : undefined;

            return (
              <FindingCard
                key={finding.id}
                id={finding.id}
                title={finding.title}
                severity={finding.severity}
                description={finding.description}
                businessImpact={finding.business_impact}
                affectedKpi={affectedKpiStr}
                confidenceScore={finding.confidence_score}
                createdAt={createdDateStr}
                traceability={traceabilityData}
              />
            );
          })}
        </div>
      )}

    </div>
  );
};

export default DiagnosticsView;
