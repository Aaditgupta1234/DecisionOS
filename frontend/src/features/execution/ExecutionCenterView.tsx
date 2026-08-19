import React, { useState } from 'react';
import { useDataset } from '../../context/DatasetContext';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { BackendOfflineScreen } from '../../shared/components/feedback/BackendOfflineScreen';
import { NoDatasetEmptyState } from '../../shared/components/feedback/NoDatasetEmptyState';
import { IntelligencePipelineBreadcrumb } from '../../shared/components/pipeline/IntelligencePipelineBreadcrumb';
import { InitiativeStatusBoard } from '../../shared/components/execution/InitiativeStatusBoard';
import { InitiativeItem, InitiativeStatus } from '../../shared/components/execution/InitiativeCard';
import { ExecutivePerformanceCard } from '../../shared/components/execution/ExecutivePerformanceCard';
import { ExecutionAnalyticsTimeline } from '../../shared/components/execution/ExecutionAnalyticsTimeline';
import { PlayCircle, Plus, Search, Filter, RefreshCw, CheckCircle2, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';

export const ExecutionCenterView: React.FC = () => {
  const { activeDataset } = useDataset();
  const { status: healthStatus, checkHealth } = useBackendHealth();

  const [initiatives, setInitiatives] = useState<InitiativeItem[]>([
    {
      id: 'init_1',
      code: 'INIT-2026-001',
      title: 'Targeted Win-Back Campaign & Courier SLA Penalties',
      owner: 'Marcus Vance',
      department: 'VP Customer Success',
      priority: 'CRITICAL',
      status: 'IN_PROGRESS',
      targetDate: 'Sep 15, 2026',
      predictedRecovery: '+$180K ARR',
      actualRecovery: '+$124K ARR',
      achievementRate: 68.8,
    },
    {
      id: 'init_2',
      code: 'INIT-2026-002',
      title: 'Secondary Hub Dispatch Load-Balancing',
      owner: 'Elena Rostova',
      department: 'Head of Logistics',
      priority: 'HIGH',
      status: 'IN_PROGRESS',
      targetDate: 'Sep 30, 2026',
      predictedRecovery: '+$140K ARR',
      actualRecovery: '$0',
      achievementRate: 20,
    },
    {
      id: 'init_3',
      code: 'INIT-2026-003',
      title: 'Automated Post-Purchase Cross-Sell Recommendation Engine',
      owner: 'Marcus Vance',
      department: 'VP Customer Success',
      priority: 'MEDIUM',
      status: 'NOT_STARTED',
      targetDate: 'Oct 15, 2026',
      predictedRecovery: '+$85K ARR',
      actualRecovery: '$0',
      achievementRate: 0,
      blockedBy: 'INIT-2026-001 Cohort Data',
    },
    {
      id: 'init_4',
      code: 'INIT-2026-004',
      title: 'One-Click Payment Gateway Integration & Retry Engine',
      owner: 'Marcus Vance',
      department: 'VP Customer Success',
      priority: 'MEDIUM',
      status: 'COMPLETED',
      targetDate: 'Aug 15, 2026',
      predictedRecovery: '+$40K ARR',
      actualRecovery: '+$40K ARR',
      achievementRate: 100,
    },
    {
      id: 'init_5',
      code: 'INIT-2026-005',
      title: 'Northern Corridors Micro-Courier Redundancy Partnership',
      owner: 'Elena Rostova',
      department: 'Head of Logistics',
      priority: 'MEDIUM',
      status: 'COMPLETED',
      targetDate: 'Aug 20, 2026',
      predictedRecovery: '+$35K ARR',
      actualRecovery: '+$35K ARR',
      achievementRate: 100,
    },
    {
      id: 'init_6',
      code: 'INIT-2026-006',
      title: 'Warehouse Automation & Sorting Line Overhaul',
      owner: 'Elena Rostova',
      department: 'Head of Logistics',
      priority: 'HIGH',
      status: 'IN_PROGRESS',
      targetDate: 'Nov 01, 2026',
      predictedRecovery: '+$110K ARR',
      actualRecovery: '$0',
      achievementRate: 15,
    },
  ]);

  if (healthStatus === 'offline') {
    return <BackendOfflineScreen onRetry={checkHealth} />;
  }

  if (!activeDataset) {
    return (
      <div style={{ padding: '32px' }}>
        <NoDatasetEmptyState
          title="No Active Dataset Selected"
          description="Select or upload a dataset to initialize and track executive execution initiatives."
        />
      </div>
    );
  }

  const handleMoveStatus = (id: string, newStatus: InitiativeStatus) => {
    setInitiatives((prev) =>
      prev.map((item) => (item.id === id ? { ...item, status: newStatus } : item))
    );
  };

  const inProgressCount = initiatives.filter((i) => i.status === 'IN_PROGRESS').length;
  const completedCount = initiatives.filter((i) => i.status === 'COMPLETED').length;
  const notStartedCount = initiatives.filter((i) => i.status === 'NOT_STARTED').length;
  const blockedCount = initiatives.filter((i) => i.status === 'BLOCKED').length;

  return (
    <div style={{ padding: '28px 32px', color: '#FFFFFF', maxWidth: '1600px', margin: '0 auto' }}>
      
      {/* 1. Pipeline Breadcrumb */}
      <IntelligencePipelineBreadcrumb currentStep="execution" />

      {/* 2. Header & Action Controls */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '10.5px', fontWeight: 700, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.12)', border: '1px solid rgba(56, 189, 248, 0.28)', padding: '1px 7px', borderRadius: '4px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Phase 11 Closed-Loop Execution Center
            </span>
            <span style={{ fontSize: '12px', color: '#64748B' }}>•</span>
            <span style={{ fontSize: '12px', color: '#94A3B8', fontWeight: 600 }}>{activeDataset.name}</span>
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, letterSpacing: '-0.02em' }}>
            Executive Execution Command Center
          </h1>
          <p style={{ fontSize: '13px', color: '#94A3B8', marginTop: '4px' }}>
            Track initiative lifecycles, assign ownership accountability, monitor progress velocity, and capture realized business recovery.
          </p>
        </div>

        <Link
          to="/outcomes"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            background: '#1D4ED8',
            border: '1px solid #3B82F6',
            color: '#FFFFFF',
            padding: '8px 16px',
            borderRadius: '6px',
            fontSize: '12.5px',
            fontWeight: 700,
            textDecoration: 'none',
            boxShadow: '0 0 12px rgba(59, 130, 246, 0.35)',
          }}
        >
          <TrendingUp size={14} />
          <span>View Recovery Outcomes</span>
        </Link>
      </div>

      {/* 3. Executive Execution Summary Banner */}
      <div style={{
        background: '#090C12',
        border: '1px solid #1A2230',
        borderRadius: '12px',
        padding: '18px 20px',
        marginBottom: '24px',
        display: 'grid',
        gridTemplateColumns: 'repeat(5, 1fr)',
        gap: '12px',
      }}>
        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Total Initiatives</span>
          <div style={{ fontSize: '18px', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>{initiatives.length} Active</div>
        </div>

        <div style={{ background: '#05070B', border: '1px solid rgba(56, 189, 248, 0.3)', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#38BDF8', textTransform: 'uppercase', fontWeight: 700 }}>In Progress</span>
          <div style={{ fontSize: '18px', fontWeight: 800, color: '#38BDF8', marginTop: '2px' }}>{inProgressCount} Initiatives</div>
        </div>

        <div style={{ background: '#05070B', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#10B981', textTransform: 'uppercase', fontWeight: 700 }}>Completed</span>
          <div style={{ fontSize: '18px', fontWeight: 800, color: '#10B981', marginTop: '2px' }}>{completedCount} Realized</div>
        </div>

        <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700 }}>Target Recovery</span>
          <div style={{ fontSize: '18px', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>+$480K ARR</div>
        </div>

        <div style={{ background: '#05070B', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', padding: '12px 14px' }}>
          <span style={{ fontSize: '10px', color: '#10B981', textTransform: 'uppercase', fontWeight: 700 }}>Actual Realized</span>
          <div style={{ fontSize: '18px', fontWeight: 800, color: '#10B981', marginTop: '2px' }}>+$124K ARR (25.8%)</div>
        </div>
      </div>

      {/* 4. 5-Column Kanban Status Board */}
      <div style={{ marginBottom: '28px' }}>
        <h3 style={{ fontSize: '14.5px', fontWeight: 800, color: '#FFFFFF', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '14px' }}>
          Initiative Lifecycle Kanban Workflow
        </h3>
        <InitiativeStatusBoard initiatives={initiatives} onMoveStatus={handleMoveStatus} />
      </div>

      {/* 5. Executive Accountability Scorecard */}
      <ExecutivePerformanceCard />

      {/* 6. Execution Velocity Analytics Timeline */}
      <ExecutionAnalyticsTimeline />

    </div>
  );
};

export default ExecutionCenterView;
