import React from 'react';
import { CheckCircle2, PlayCircle, Clock, Calendar } from 'lucide-react';

export interface MilestoneItem {
  week: string;
  title: string;
  description: string;
  owner: string;
  status: 'COMPLETED' | 'IN_PROGRESS' | 'SCHEDULED';
  completionDate?: string;
}

interface Props {
  milestones?: MilestoneItem[];
}

export const ExecutionTimeline: React.FC<Props> = ({
  milestones = [
    { week: 'Week 1', title: 'Campaign Design & Voucher Ingestion', description: 'Generated tailored discount vouchers for 842 churn-risk customers in southeastern corridors.', owner: 'Growth Team', status: 'COMPLETED', completionDate: 'Aug 20, 2026' },
    { week: 'Week 2', title: 'Audience Segmentation & Courier SLAs', description: 'Enforced delivery SLA penalties on SE regional courier lines and isolated target audience.', owner: 'Logistics Lead', status: 'COMPLETED', completionDate: 'Aug 27, 2026' },
    { week: 'Week 3', title: 'Automated Outreach Launch & Dispatch', description: 'Batch email & SMS outreach triggered with personalized win-back credit incentives.', owner: 'Marketing Lead', status: 'IN_PROGRESS' },
    { week: 'Week 4', title: 'Recovery Telemetry & ROI Validation', description: 'Evaluate repeat purchase conversions and measure verified ARR recovery movement.', owner: 'Data Analytics', status: 'SCHEDULED' },
  ],
}) => {
  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '12px',
      padding: '22px',
      marginBottom: '24px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px' }}>
        <h3 style={{ fontSize: '14.5px', fontWeight: 800, color: '#FFFFFF', margin: 0, textTransform: 'uppercase' }}>
          Phased 4-Week Execution Milestone Roadmap
        </h3>
        <span style={{ fontSize: '10.5px', color: '#38BDF8', fontWeight: 700 }}>
          Week 3 Active
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {milestones.map((m, idx) => {
          const isDone = m.status === 'COMPLETED';
          const isCurrent = m.status === 'IN_PROGRESS';

          return (
            <div
              key={idx}
              style={{
                background: isCurrent ? 'rgba(56, 189, 248, 0.06)' : '#05070B',
                border: `1px solid ${isCurrent ? '#38BDF8' : isDone ? '#10B981' : '#141C28'}`,
                borderRadius: '8px',
                padding: '14px 16px',
                display: 'flex',
                alignItems: 'flex-start',
                justifyContent: 'space-between',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
                <div style={{ marginTop: '2px' }}>
                  {isDone ? (
                    <CheckCircle2 size={18} color="#10B981" />
                  ) : isCurrent ? (
                    <PlayCircle size={18} color="#38BDF8" />
                  ) : (
                    <Clock size={18} color="#64748B" />
                  )}
                </div>

                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '3px' }}>
                    <span style={{ fontSize: '10px', fontWeight: 800, color: '#64748B', textTransform: 'uppercase' }}>
                      {m.week}
                    </span>
                    <span style={{ fontSize: '13px', fontWeight: 800, color: '#FFFFFF' }}>
                      {m.title}
                    </span>
                  </div>

                  <p style={{ fontSize: '12px', color: '#CBD5E1', margin: 0, lineHeight: 1.45 }}>
                    {m.description}
                  </p>
                </div>
              </div>

              <div style={{ textAlign: 'right', flexShrink: 0, marginLeft: '16px' }}>
                <span style={{ fontSize: '10px', color: '#64748B', display: 'block', textTransform: 'uppercase' }}>{m.owner}</span>
                <span style={{
                  fontSize: '11px',
                  fontWeight: 700,
                  color: isDone ? '#10B981' : isCurrent ? '#38BDF8' : '#94A3B8',
                }}>
                  {m.completionDate ? `✓ ${m.completionDate}` : m.status}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
