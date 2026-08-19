import React from 'react';
import {
  Check,
  Database,
  Table,
  Activity,
  AlertTriangle,
  GitMerge,
  CheckCircle2,
  FileText,
  Sparkles,
  PlayCircle,
  TrendingUp,
} from 'lucide-react';
import { Link } from 'react-router-dom';

export type PipelineStepId =
  | 'ingest'
  | 'schema'
  | 'metrics'
  | 'diagnostics'
  | 'rootcause'
  | 'recommendations'
  | 'reports'
  | 'ai'
  | 'execution'
  | 'outcomes';

interface Props {
  currentStep: PipelineStepId;
}

export const IntelligencePipelineBreadcrumb: React.FC<Props> = ({ currentStep }) => {
  const steps = [
    { id: 'ingest', name: '01 Ingest', to: '/datasets', icon: Database },
    { id: 'schema', name: '02 Schema', to: '/datasets', icon: Table },
    { id: 'metrics', name: '03 KPIs', to: '/metrics', icon: Activity },
    { id: 'diagnostics', name: '04 Diagnostics', to: '/diagnostics', icon: AlertTriangle },
    { id: 'rootcause', name: '05 Root Cause', to: '/root-causes', icon: GitMerge },
    { id: 'recommendations', name: '06 Actions', to: '/recommendations', icon: CheckCircle2 },
    { id: 'reports', name: '07 Executive Brief', to: '/reports', icon: FileText },
    { id: 'ai', name: '08 AI Narrative', to: '/ai-insights', icon: Sparkles },
    { id: 'execution', name: '09 Execution', to: '/execution', icon: PlayCircle },
    { id: 'outcomes', name: '10 Outcomes', to: '/outcomes', icon: TrendingUp },
  ];

  const currentIdx = steps.findIndex((s) => s.id === currentStep);

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        background: '#070A0F',
        border: '1px solid #141C28',
        borderRadius: '10px',
        padding: '8px 12px',
        marginBottom: '24px',
        overflowX: 'auto',
        gap: '4px',
      }}
    >
      {steps.map((step, idx) => {
        const isCurrent = step.id === currentStep;
        const isCompleted = idx < currentIdx;
        const Icon = step.icon;

        return (
          <React.Fragment key={step.id}>
            <Link
              to={step.to}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '6px 10px',
                borderRadius: '6px',
                fontSize: '11px',
                fontWeight: isCurrent ? 800 : isCompleted ? 600 : 500,
                color: isCurrent ? '#FFFFFF' : isCompleted ? '#38BDF8' : '#64748B',
                background: isCurrent ? '#1D4ED8' : isCompleted ? 'rgba(56, 189, 248, 0.08)' : 'transparent',
                border: isCurrent
                  ? '1px solid #3B82F6'
                  : isCompleted
                  ? '1px solid rgba(56, 189, 248, 0.2)'
                  : '1px solid transparent',
                textDecoration: 'none',
                whiteSpace: 'nowrap',
                transition: 'all 0.15s ease',
              }}
            >
              {isCompleted ? (
                <Check size={11} color="#38BDF8" />
              ) : (
                <Icon size={11} color={isCurrent ? '#FFFFFF' : '#64748B'} />
              )}
              <span>{step.name}</span>
            </Link>

            {idx < steps.length - 1 && (
              <span style={{ color: '#1E293B', fontSize: '10px', margin: '0 1px' }}>→</span>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};
