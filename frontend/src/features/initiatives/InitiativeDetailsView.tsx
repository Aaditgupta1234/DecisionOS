import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useDataset } from '../../context/DatasetContext';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { BackendOfflineScreen } from '../../shared/components/feedback/BackendOfflineScreen';
import { NoDatasetEmptyState } from '../../shared/components/feedback/NoDatasetEmptyState';
import { IntelligencePipelineBreadcrumb } from '../../shared/components/pipeline/IntelligencePipelineBreadcrumb';
import { InitiativeTracePanel } from '../../shared/components/execution/InitiativeTracePanel';
import { DependencyGraph } from '../../shared/components/execution/DependencyGraph';
import { KPIBaselineSnapshotCard } from '../../shared/components/execution/KPIBaselineSnapshotCard';
import { ExecutionTimeline } from '../../shared/components/execution/ExecutionTimeline';
import { KPIRecoveryChart } from '../../shared/components/execution/KPIRecoveryChart';
import { ExecutionForecastCard } from '../../shared/components/execution/ExecutionForecastCard';
import { InitiativeRiskPanel } from '../../shared/components/execution/InitiativeRiskPanel';
import { ExecutiveNotesPanel } from '../../shared/components/execution/ExecutiveNotesPanel';
import { InitiativeAuditTimeline } from '../../shared/components/execution/InitiativeAuditTimeline';
import { ArrowLeft, User, Calendar, ShieldCheck, CheckCircle2, TrendingUp, PlayCircle } from 'lucide-react';

export const InitiativeDetailsView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
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
          description="Select or upload a dataset to inspect initiative execution blueprints and KPI recovery telemetry."
        />
      </div>
    );
  }

  return (
    <div style={{ padding: '28px 32px', color: '#FFFFFF', maxWidth: '1600px', margin: '0 auto' }}>
      
      {/* 1. Pipeline Breadcrumb */}
      <IntelligencePipelineBreadcrumb currentStep="execution" />

      {/* 2. Top Navigation Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <Link
          to="/execution"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            color: '#38BDF8',
            fontSize: '12px',
            fontWeight: 700,
            textDecoration: 'none',
          }}
        >
          <ArrowLeft size={14} />
          <span>Back to Execution Command Center</span>
        </Link>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '10.5px', color: '#94A3B8' }}>{activeDataset.name}</span>
          <span style={{ fontSize: '10.5px', color: '#10B981', fontWeight: 700, background: 'rgba(16, 185, 129, 0.1)', padding: '2px 8px', borderRadius: '4px' }}>
            INIT-2026-001 Active
          </span>
        </div>
      </div>

      {/* 3. Initiative Hero Card */}
      <div style={{
        background: 'linear-gradient(135deg, #0B111A 0%, #06090F 100%)',
        border: '1px solid #1E293B',
        borderRadius: '12px',
        padding: '24px',
        marginBottom: '24px',
        boxShadow: '0 15px 35px rgba(0, 0, 0, 0.6)',
      }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span style={{ fontSize: '11px', fontWeight: 800, color: '#38BDF8', fontFamily: 'monospace', background: 'rgba(56, 189, 248, 0.12)', padding: '2px 8px', borderRadius: '4px' }}>
                INIT-2026-001
              </span>
              <span style={{ fontSize: '10.5px', fontWeight: 800, color: '#EF4444', background: 'rgba(239, 68, 68, 0.12)', padding: '2px 8px', borderRadius: '4px' }}>
                CRITICAL PRIORITY
              </span>
              <span style={{ fontSize: '10.5px', fontWeight: 800, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.12)', padding: '2px 8px', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <PlayCircle size={12} />
                <span>IN PROGRESS</span>
              </span>
            </div>

            <h1 style={{ fontSize: '22px', fontWeight: 800, letterSpacing: '-0.02em', margin: '0 0 8px' }}>
              Targeted Win-Back Campaign & Courier SLA Penalties
            </h1>

            <p style={{ fontSize: '13px', color: '#CBD5E1', lineHeight: 1.5, margin: 0, maxWidth: '900px' }}>
              Automate personalized discount incentives for the 842 churn-risk customers in southeastern corridors while enforcing courier SLA delivery caps and dispute concessions.
            </p>
          </div>

          {/* Owner Box */}
          <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 16px', textAlign: 'right' }}>
            <span style={{ fontSize: '10.5px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Executive Owner</span>
            <div style={{ fontSize: '13.5px', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>Marcus Vance</div>
            <span style={{ fontSize: '11px', color: '#38BDF8' }}>VP Customer Success</span>
          </div>
        </div>

        {/* Financial Metrics Strip */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', borderTop: '1px solid #141C28', paddingTop: '16px' }}>
          <div>
            <span style={{ fontSize: '10.5px', color: '#64748B', textTransform: 'uppercase' }}>Target Recovery</span>
            <div style={{ fontSize: '18px', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>+$180K ARR</div>
          </div>

          <div>
            <span style={{ fontSize: '10.5px', color: '#10B981', textTransform: 'uppercase', fontWeight: 700 }}>Actual Realized</span>
            <div style={{ fontSize: '18px', fontWeight: 800, color: '#10B981', marginTop: '2px' }}>+$124K ARR</div>
          </div>

          <div>
            <span style={{ fontSize: '10.5px', color: '#64748B', textTransform: 'uppercase' }}>Achievement Rate</span>
            <div style={{ fontSize: '18px', fontWeight: 800, color: '#38BDF8', marginTop: '2px' }}>68.8%</div>
          </div>

          <div>
            <span style={{ fontSize: '10.5px', color: '#64748B', textTransform: 'uppercase' }}>Commitment Target</span>
            <div style={{ fontSize: '18px', fontWeight: 800, color: '#CBD5E1', marginTop: '2px' }}>Sep 15, 2026</div>
          </div>
        </div>
      </div>

      {/* 4. 6-Stage Lineage Trace Panel */}
      <InitiativeTracePanel />

      {/* 5. Immutable Baseline KPI Telemetry Snapshot Card */}
      <KPIBaselineSnapshotCard />

      {/* 6. Visual Dependency Graph with Classified Badges */}
      <DependencyGraph />

      {/* 7. Milestone Timeline & KPI Recovery Charts Split Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '20px', marginBottom: '24px' }}>
        <ExecutionTimeline />
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <KPIRecoveryChart />
          <ExecutionForecastCard />
        </div>
      </div>

      {/* 8. Risk Register & Executive Notes Split */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
        <InitiativeRiskPanel />
        <ExecutiveNotesPanel />
      </div>

      {/* 9. Enterprise Append-Only Audit Trail */}
      <InitiativeAuditTimeline />

    </div>
  );
};

export default InitiativeDetailsView;
