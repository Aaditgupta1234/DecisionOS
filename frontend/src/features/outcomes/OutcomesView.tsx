import React from 'react';
import { useDataset } from '../../context/DatasetContext';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { BackendOfflineScreen } from '../../shared/components/feedback/BackendOfflineScreen';
import { NoDatasetEmptyState } from '../../shared/components/feedback/NoDatasetEmptyState';
import { IntelligencePipelineBreadcrumb } from '../../shared/components/pipeline/IntelligencePipelineBreadcrumb';
import { OutcomeScorecard } from '../../shared/components/execution/OutcomeScorecard';
import { PortfolioHealthForecast } from '../../shared/components/execution/PortfolioHealthForecast';
import { RecoveryConfidenceBreakdown } from '../../shared/components/execution/RecoveryConfidenceBreakdown';
import { DecisionAccuracyCard } from '../../shared/components/execution/DecisionAccuracyCard';
import { KPIAttributionCard } from '../../shared/components/execution/KPIAttributionCard';
import { RecoveryWaterfallActual } from '../../shared/components/execution/RecoveryWaterfallActual';
import { Award, TrendingUp, CheckCircle2, Building2, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export const OutcomesView: React.FC = () => {
  const { activeDataset } = useDataset();
  const { status: healthStatus, checkHealth } = useBackendHealth();

  if (healthStatus === 'offline') {
    return <BackendOfflineScreen onRetry={checkHealth} />;
  }

  if (!activeDataset) {
    return (
      <div style={{ padding: '32px' }}>
        <NoDatasetEmptyState
          title="No Active Dataset Selected"
          description="Select or upload a dataset to review realized business recovery and ROI performance."
        />
      </div>
    );
  }

  const initiativeRoiList = [
    {
      id: 'init_1',
      title: 'Targeted Win-Back Campaign & Courier SLA Penalties',
      owner: 'VP Customer Success',
      predicted: '$180K',
      actual: '$124K',
      achievement: '68.8%',
      roi: '3.4x',
      status: 'IN_PROGRESS',
    },
    {
      id: 'init_4',
      title: 'One-Click Payment Gateway Integration & Retry Engine',
      owner: 'VP Customer Success',
      predicted: '$40K',
      actual: '$40K',
      achievement: '100%',
      roi: '4.2x',
      status: 'COMPLETED',
    },
    {
      id: 'init_5',
      title: 'Northern Corridors Micro-Courier Redundancy Partnership',
      owner: 'Head of Logistics',
      predicted: '$35K',
      actual: '$35K',
      achievement: '100%',
      roi: '2.8x',
      status: 'COMPLETED',
    },
    {
      id: 'init_2',
      title: 'Secondary Hub Dispatch Load-Balancing',
      owner: 'Head of Logistics',
      predicted: '$140K',
      actual: '$0K (In Flight)',
      achievement: '20.0%',
      roi: 'Pending',
      status: 'IN_PROGRESS',
    },
    {
      id: 'init_3',
      title: 'Automated Post-Purchase Cross-Sell Recommendation Engine',
      owner: 'VP Customer Success',
      predicted: '$85K',
      actual: '$0K (Scheduled)',
      achievement: '0.0%',
      roi: 'Pending',
      status: 'NOT_STARTED',
    },
  ];

  return (
    <div style={{ padding: '28px 32px', color: '#FFFFFF', maxWidth: '1600px', margin: '0 auto' }}>
      
      {/* 1. Pipeline Breadcrumb */}
      <IntelligencePipelineBreadcrumb currentStep="outcomes" />

      {/* 2. Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '10.5px', fontWeight: 700, color: '#10B981', background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.28)', padding: '1px 7px', borderRadius: '4px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Phase 12 Realized Recovery & Value Capture
            </span>
            <span style={{ fontSize: '12px', color: '#64748B' }}>•</span>
            <span style={{ fontSize: '12px', color: '#94A3B8', fontWeight: 600 }}>{activeDataset.name}</span>
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, letterSpacing: '-0.02em' }}>
            Recovery Outcomes & ROI Validation
          </h1>
          <p style={{ fontSize: '13px', color: '#94A3B8', marginTop: '4px' }}>
            Closing the loop from intelligence to executed value: track realized ARR recovery, validate engine accuracy, and forecast business health.
          </p>
        </div>

        <Link
          to="/execution"
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
            textDecoration: 'none',
          }}
        >
          <span>Open Execution Kanban</span>
        </Link>
      </div>

      {/* 3. Executive Outcome Command Center Scorecard */}
      <OutcomeScorecard />

      {/* 4. Portfolio Recovery by Operating Department */}
      <div style={{
        background: '#090C12',
        border: '1px solid #1A2230',
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '24px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
          <Building2 size={16} color="#38BDF8" />
          <h3 style={{ fontSize: '14.5px', fontWeight: 800, color: '#FFFFFF', margin: 0, textTransform: 'uppercase' }}>
            Portfolio Recovery by Operating Department
          </h3>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
          <div style={{ background: '#05070B', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', padding: '14px' }}>
            <span style={{ fontSize: '11px', color: '#10B981', fontWeight: 800, textTransform: 'uppercase' }}>Growth & Customer Success</span>
            <div style={{ fontSize: '18px', fontWeight: 800, color: '#FFFFFF', margin: '4px 0 2px' }}>+$164K ARR Realized</div>
            <span style={{ fontSize: '11px', color: '#94A3B8' }}>Target: $220K (74.5% Captured)</span>
          </div>

          <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '14px' }}>
            <span style={{ fontSize: '11px', color: '#38BDF8', fontWeight: 800, textTransform: 'uppercase' }}>Logistics & Fulfillment</span>
            <div style={{ fontSize: '18px', fontWeight: 800, color: '#FFFFFF', margin: '4px 0 2px' }}>+$35K ARR Realized</div>
            <span style={{ fontSize: '11px', color: '#94A3B8' }}>Target: $175K (20.0% Captured)</span>
          </div>

          <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '14px' }}>
            <span style={{ fontSize: '11px', color: '#F59E0B', fontWeight: 800, textTransform: 'uppercase' }}>Product & Merchandising</span>
            <div style={{ fontSize: '18px', fontWeight: 800, color: '#FFFFFF', margin: '4px 0 2px' }}>$0K Realized</div>
            <span style={{ fontSize: '11px', color: '#94A3B8' }}>Target: $85K (Scheduled Q4)</span>
          </div>
        </div>
      </div>

      {/* 5. Future Portfolio Health Forecast */}
      <PortfolioHealthForecast />

      {/* 6. Recovery Confidence Tier Segmentation */}
      <RecoveryConfidenceBreakdown />

      {/* 7. Decision Intelligence Precision & Learning Trend */}
      <DecisionAccuracyCard />

      {/* 8. KPI Attribution Engine */}
      <KPIAttributionCard />

      {/* 9. Realized Recovery Financial Bridge Waterfall */}
      <RecoveryWaterfallActual />

      {/* 10. Initiative ROI Performance Table */}
      <div style={{ background: '#090C12', border: '1px solid #1A2230', borderRadius: '12px', overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #141A24', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Award size={16} color="#10B981" />
            <h4 style={{ fontSize: '13.5px', fontWeight: 800, color: '#FFFFFF', margin: 0, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Initiative Realization & Campaign ROI Performance
            </h4>
          </div>
        </div>

        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #141A24', color: '#64748B', textAlign: 'left', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              <th style={{ padding: '12px 20px' }}>Initiative</th>
              <th style={{ padding: '12px 16px' }}>Owner</th>
              <th style={{ padding: '12px 16px' }}>Predicted</th>
              <th style={{ padding: '12px 16px' }}>Actual Realized</th>
              <th style={{ padding: '12px 16px' }}>Achievement</th>
              <th style={{ padding: '12px 16px' }}>Campaign ROI</th>
              <th style={{ padding: '12px 20px', textAlign: 'right' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {initiativeRoiList.map((init) => (
              <tr key={init.id} style={{ borderBottom: '1px solid #111620' }}>
                <td style={{ padding: '14px 20px', fontWeight: 700, color: '#FFFFFF' }}>
                  <Link to={`/initiatives/${init.id}`} style={{ color: '#FFFFFF', textDecoration: 'none' }}>
                    {init.title}
                  </Link>
                </td>
                <td style={{ padding: '14px 16px', color: '#94A3B8' }}>{init.owner}</td>
                <td style={{ padding: '14px 16px', color: '#CBD5E1' }}>{init.predicted}</td>
                <td style={{ padding: '14px 16px', fontWeight: 800, color: init.actual.includes('$0') ? '#64748B' : '#10B981' }}>{init.actual}</td>
                <td style={{ padding: '14px 16px', color: '#38BDF8', fontWeight: 700 }}>{init.achievement}</td>
                <td style={{ padding: '14px 16px', color: '#F59E0B', fontWeight: 800 }}>{init.roi}</td>
                <td style={{ padding: '14px 20px', textAlign: 'right' }}>
                  <span style={{
                    fontSize: '10.5px',
                    fontWeight: 700,
                    color: init.status === 'COMPLETED' ? '#10B981' : init.status === 'IN_PROGRESS' ? '#38BDF8' : '#64748B',
                    background: 'rgba(255, 255, 255, 0.04)',
                    padding: '2px 7px',
                    borderRadius: '4px',
                  }}>
                    {init.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
};

export default OutcomesView;
