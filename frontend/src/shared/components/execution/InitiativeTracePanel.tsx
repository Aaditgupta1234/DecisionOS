import React from 'react';
import { Activity, AlertTriangle, GitMerge, Zap, PlayCircle, TrendingUp, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

interface Props {
  metricName?: string;
  findingTitle?: string;
  findingId?: string;
  rootCauseTitle?: string;
  rootCauseId?: string;
  recommendationTitle?: string;
  recommendationId?: string;
  initiativeCode?: string;
  realizedOutcome?: string;
}

export const InitiativeTracePanel: React.FC<Props> = ({
  metricName = 'Customer Retention Rate (85.8%)',
  findingTitle = 'Customer Retention Deterioration in SE Corridor',
  findingId = 'f-1',
  rootCauseTitle = 'Courier Transit Delays in Southeastern Logistics Routes',
  rootCauseId = 'rc_1',
  recommendationTitle = 'Targeted Win-Back Campaign & Courier SLA Penalties',
  recommendationId = 'rec_1',
  initiativeCode = 'INIT-2026-001',
  realizedOutcome = '+$124K Realized ARR (+3.1% Retention Recovery)',
}) => {
  const steps = [
    { label: '01 Triggering KPI', value: metricName, icon: Activity, color: '#38BDF8', to: '/metrics' },
    { label: '02 Diagnostic Finding', value: findingTitle, icon: AlertTriangle, color: '#EF4444', to: `/diagnostics?findingId=${findingId}` },
    { label: '03 Root Cause DAG', value: rootCauseTitle, icon: GitMerge, color: '#F59E0B', to: `/root-causes?rootCauseId=${rootCauseId}` },
    { label: '04 Action Engine', value: recommendationTitle, icon: Zap, color: '#10B981', to: '/recommendations' },
    { label: '05 Active Initiative', value: initiativeCode, icon: PlayCircle, color: '#38BDF8' },
    { label: '06 Realized Outcome', value: realizedOutcome, icon: TrendingUp, color: '#10B981' },
  ];

  return (
    <div style={{
      background: 'linear-gradient(135deg, #090D14 0%, #06090F 100%)',
      border: '1px solid #1A2536',
      borderRadius: '12px',
      padding: '18px 20px',
      marginBottom: '24px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <h4 style={{ fontSize: '12px', fontWeight: 800, color: '#FFFFFF', textTransform: 'uppercase', letterSpacing: '0.05em', margin: 0 }}>
          Closed-Loop 6-Stage Lineage & Provenance Trace
        </h4>
        <span style={{ fontSize: '10.5px', color: '#10B981', fontWeight: 700 }}>
          100% Verifiable Chain of Custody
        </span>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(6, 1fr)',
        gap: '8px',
        alignItems: 'stretch',
      }}>
        {steps.map((step, idx) => {
          const Icon = step.icon;

          return (
            <div
              key={idx}
              style={{
                background: '#04060A',
                border: '1px solid #141C28',
                borderRadius: '8px',
                padding: '10px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
                  <Icon size={11} color={step.color} />
                  <span style={{ fontSize: '9px', fontWeight: 800, color: step.color, textTransform: 'uppercase' }}>
                    {step.label}
                  </span>
                </div>

                <div style={{ fontSize: '11px', fontWeight: 700, color: '#FFFFFF', lineHeight: 1.3, marginBottom: '6px' }}>
                  {step.value}
                </div>
              </div>

              {step.to && (
                <Link
                  to={step.to}
                  style={{
                    fontSize: '9.5px',
                    color: '#38BDF8',
                    textDecoration: 'none',
                    fontWeight: 700,
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '2px',
                  }}
                >
                  <span>Inspect</span>
                  <ArrowRight size={9} />
                </Link>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
