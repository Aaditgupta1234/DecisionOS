import React from 'react';
import { Check, Database, Table, Activity, AlertTriangle, GitMerge, CheckCircle2, FileText, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

export type PipelineStepId = 'ingest' | 'schema' | 'metrics' | 'diagnostics' | 'rootcause' | 'recommendations' | 'reports' | 'ai';

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
  ];

  const currentIdx = steps.findIndex(s => s.id === currentStep);

  return (
    <div style={{
      background: 'rgba(8, 11, 16, 0.85)',
      border: '1px solid #1A2230',
      borderRadius: '10px',
      padding: '8px 16px',
      marginBottom: '20px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      backdropFilter: 'blur(12px)',
      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.4)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px', fontWeight: 700, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
        <span>Intelligence Pipeline:</span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', overflowX: 'auto' }}>
        {steps.map((step, idx) => {
          const isPassed = idx < currentIdx;
          const isCurrent = idx === currentIdx;
          const Icon = step.icon;

          return (
            <React.Fragment key={step.id}>
              <Link
                to={step.to}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '5px',
                  padding: '4px 8px',
                  borderRadius: '5px',
                  fontSize: '11px',
                  fontWeight: isCurrent ? 800 : 600,
                  color: isCurrent ? '#FFFFFF' : isPassed ? '#10B981' : '#64748B',
                  background: isCurrent ? '#1D4ED8' : isPassed ? 'rgba(16, 185, 129, 0.08)' : 'transparent',
                  border: `1px solid ${isCurrent ? '#3B82F6' : isPassed ? 'rgba(16, 185, 129, 0.2)' : 'transparent'}`,
                  textDecoration: 'none',
                  whiteSpace: 'nowrap',
                  transition: 'all 0.15s ease',
                  boxShadow: isCurrent ? '0 0 10px rgba(59, 130, 246, 0.4)' : 'none',
                }}
              >
                {isPassed ? (
                  <Check size={11} strokeWidth={3} />
                ) : (
                  <Icon size={11} />
                )}
                <span>{step.name}</span>
              </Link>

              {idx < steps.length - 1 && (
                <span style={{ color: '#1E293B', fontSize: '10px', margin: '0 2px' }}>→</span>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
