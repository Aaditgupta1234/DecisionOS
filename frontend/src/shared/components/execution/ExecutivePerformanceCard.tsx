import React from 'react';
import { UserCheck, CheckCircle2, TrendingUp, Briefcase } from 'lucide-react';

interface OwnerPerformance {
  owner: string;
  department: string;
  assignedCount: number;
  completedCount: number;
  inProgressCount: number;
  recoveryGenerated: string;
}

interface Props {
  owners?: OwnerPerformance[];
}

export const ExecutivePerformanceCard: React.FC<Props> = ({
  owners = [
    { owner: 'VP Customer Success', department: 'Growth & Success', assignedCount: 4, completedCount: 3, inProgressCount: 1, recoveryGenerated: '+$124K ARR' },
    { owner: 'Head of Logistics Operations', department: 'Fulfillment', assignedCount: 2, completedCount: 1, inProgressCount: 1, recoveryGenerated: '+$0K (In Progress)' },
  ],
}) => {
  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '12px',
      padding: '20px',
      marginBottom: '24px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <UserCheck size={16} color="#38BDF8" />
          <h3 style={{ fontSize: '14px', fontWeight: 800, color: '#FFFFFF', margin: 0, textTransform: 'uppercase' }}>
            Executive Accountability & Ownership Scorecard
          </h3>
        </div>
        <span style={{ fontSize: '10.5px', color: '#64748B', fontWeight: 600 }}>Leadership Review Metric</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
        {owners.map((o, idx) => (
          <div
            key={idx}
            style={{
              background: '#05070B',
              border: '1px solid #141C28',
              borderRadius: '8px',
              padding: '14px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div style={{ fontSize: '13.5px', fontWeight: 800, color: '#FFFFFF', marginBottom: '2px' }}>
                {o.owner}
              </div>
              <span style={{ fontSize: '11px', color: '#64748B', display: 'block', marginBottom: '12px' }}>
                {o.department}
              </span>
            </div>

            <div style={{ borderTop: '1px solid #101620', paddingTop: '10px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ fontSize: '11px', color: '#94A3B8' }}>
                <strong style={{ color: '#FFFFFF' }}>{o.completedCount}</strong> of {o.assignedCount} Completed ({o.inProgressCount} active)
              </div>

              <div style={{ fontSize: '13px', fontWeight: 800, color: '#10B981' }}>
                {o.recoveryGenerated}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
