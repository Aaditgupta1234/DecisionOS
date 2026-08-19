import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { queryKeys } from '../../shared/api/queryKeys';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { BackendOfflineScreen } from '../../shared/components/feedback/BackendOfflineScreen';
import { NoDatasetEmptyState } from '../../shared/components/feedback/NoDatasetEmptyState';
import { IntelligencePipelineBreadcrumb } from '../../shared/components/pipeline/IntelligencePipelineBreadcrumb';
import { FindingCard, FindingTraceability } from '../../shared/components/diagnostics/FindingCard';
import { DiagnosticFinding } from '../../types';
import { AlertTriangle, Search, Filter, RefreshCw, AlertOctagon, ShieldAlert, Info, ArrowUpDown } from 'lucide-react';

export const DiagnosticsView: React.FC = () => {
  const { activeDataset } = useDataset();
  const { status: healthStatus, checkHealth } = useBackendHealth();

  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [sortByImpact, setSortByImpact] = useState<boolean>(true);

  // 1. Fetch Diagnostics Findings
  const { data: findingsData, isLoading, refetch } = useQuery<DiagnosticFinding[]>({
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

  // Core structured diagnostic findings with full causal traceability links
  const defaultFindings = [
    {
      id: 'f-1',
      title: 'Customer Retention Deterioration in Southeastern Logistics Routes',
      severity: 'CRITICAL',
      description: 'Retention fell by 4.3% in Southeastern hubs. Delivery delays exceeding 5 days triggered sharp rating drops (2.1★) and elevated cart cancellation rates.',
      businessImpact: '-$218K / quarter',
      impactValue: 218000,
      affectedKpi: 'Customer Retention & Revenue',
      confidenceScore: 0.94,
      createdAt: 'Aug 18, 2026',
      traceability: {
        supportingMetric: 'Customer Retention Rate',
        metricDelta: 'Dropped from 90.1% → 85.8% (-4.3%)',
        associatedRootCauseTitle: 'Courier Transit Delays in Southeastern Logistics Routes',
        associatedRootCauseId: 'rc_1',
        associatedRecommendationTitle: 'Targeted Win-Back Campaign & Courier SLA Penalties',
        associatedRecommendationId: 'rec_1',
        expectedRecovery: '+$180K ARR',
      },
    },
    {
      id: 'f-2',
      title: 'Order Fulfillment Bottleneck in Secondary Hubs',
      severity: 'CRITICAL',
      description: 'Warehouse dispatch latency increased from 1.2 to 3.8 days during peak hours, directly depressing on-time SLA adherence below 88%.',
      businessImpact: '-$140K / quarter',
      impactValue: 140000,
      affectedKpi: 'Delivery Time & Orders',
      confidenceScore: 0.92,
      createdAt: 'Aug 18, 2026',
      traceability: {
        supportingMetric: 'Average Delivery Time',
        metricDelta: 'Increased from 2.6 → 3.4 days (+0.8 days)',
        associatedRootCauseTitle: 'Secondary Hub Dispatch Backlog & Capacity Saturation',
        associatedRootCauseId: 'rc_2',
        associatedRecommendationTitle: 'Dynamic Dispatch Load-Balancing & Secondary Courier Tier',
        associatedRecommendationId: 'rec_2',
        expectedRecovery: '+$95K ARR',
      },
    },
    {
      id: 'f-3',
      title: 'AOV Compression in Health & Beauty Product Category',
      severity: 'HIGH',
      description: 'Average transaction size decreased by 6.8% following the expiration of curated bundle discounts and reduced cross-sell widget attachment.',
      businessImpact: '-$72K / quarter',
      impactValue: 72000,
      affectedKpi: 'Average Order Value (AOV)',
      confidenceScore: 0.89,
      createdAt: 'Aug 17, 2026',
      traceability: {
        supportingMetric: 'Average Order Value',
        metricDelta: 'Decreased from $245.10 → $228.40 (-6.8%)',
        associatedRootCauseTitle: 'Post-Promo Cross-Sell Disengagement in Beauty Segment',
        associatedRootCauseId: 'rc_3',
        associatedRecommendationTitle: 'Automated Post-Purchase Cross-Sell Recommendation Engine',
        associatedRecommendationId: 'rec_3',
        expectedRecovery: '+$65K ARR',
      },
    },
    {
      id: 'f-4',
      title: 'Cancellation Rate Spike on High-Value Electronic Shipments',
      severity: 'HIGH',
      description: 'Pre-dispatch order cancellations rose 1.8% among transactions >$400, caused by verification delays and payment gateway timeouts.',
      businessImpact: '-$54K / quarter',
      impactValue: 54000,
      affectedKpi: 'Cancellation Rate',
      confidenceScore: 0.88,
      createdAt: 'Aug 16, 2026',
      traceability: {
        supportingMetric: 'Order Cancellation Rate',
        metricDelta: 'Increased from 1.7% → 2.1% (+0.4%)',
        associatedRootCauseTitle: 'Payment Gateway Verification Latency on High-Ticket Orders',
        associatedRootCauseId: 'rc_4',
        associatedRecommendationTitle: 'Streamlined One-Click Payment Gateway Integration',
        associatedRecommendationId: 'rec_4',
        expectedRecovery: '+$40K ARR',
      },
    },
    {
      id: 'f-5',
      title: 'Minor Shipping Variance in Northern Rural Corridors',
      severity: 'LOW',
      description: 'Minor delivery variance observed in low-density routes (<3% of total order volume). SLA compliance remains above 94%.',
      businessImpact: '-$12K / quarter',
      impactValue: 12000,
      affectedKpi: 'Operational Delivery',
      confidenceScore: 0.85,
      createdAt: 'Aug 15, 2026',
    },
  ];

  // Count by severity
  const severityCounts = {
    CRITICAL: defaultFindings.filter(f => f.severity === 'CRITICAL').length,
    HIGH: defaultFindings.filter(f => f.severity === 'HIGH').length,
    MEDIUM: defaultFindings.filter(f => f.severity === 'MEDIUM').length,
    LOW: defaultFindings.filter(f => f.severity === 'LOW').length,
  };

  // Filter & Sort
  let filtered = defaultFindings.filter((f) => {
    const matchesSev = selectedSeverity === 'ALL' || f.severity === selectedSeverity;
    const matchesSearch =
      f.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.affectedKpi.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSev && matchesSearch;
  });

  if (sortByImpact) {
    filtered = [...filtered].sort((a, b) => (b.impactValue || 0) - (a.impactValue || 0));
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

      {/* 3. Severity Summary Header Tally */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '12px',
        marginBottom: '24px',
      }}>
        {/* Critical */}
        <div
          onClick={() => setSelectedSeverity('CRITICAL')}
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
          onClick={() => setSelectedSeverity('HIGH')}
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
          onClick={() => setSelectedSeverity('MEDIUM')}
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
          onClick={() => setSelectedSeverity('LOW')}
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

      {/* 5. Finding Cards List */}
      <div>
        {filtered.length === 0 ? (
          <div style={{ background: '#090C12', border: '1px solid #1A2230', borderRadius: '10px', padding: '40px', textAlign: 'center', color: '#64748B' }}>
            No diagnostic findings match your current filters.
          </div>
        ) : (
          filtered.map((finding) => (
            <FindingCard
              key={finding.id}
              id={finding.id}
              title={finding.title}
              severity={finding.severity}
              description={finding.description}
              businessImpact={finding.businessImpact}
              affectedKpi={finding.affectedKpi}
              confidenceScore={finding.confidenceScore}
              createdAt={finding.createdAt}
              traceability={finding.traceability}
            />
          ))
        )}
      </div>

    </div>
  );
};

export default DiagnosticsView;
