import React from 'react';
import { InitiativeCard, InitiativeItem, InitiativeStatus } from './InitiativeCard';
import { PlayCircle, CheckCircle2, Clock, AlertOctagon, XCircle, Plus } from 'lucide-react';

interface Props {
  initiatives: InitiativeItem[];
  onMoveStatus?: (id: string, newStatus: InitiativeStatus) => void;
  onOpenNewModal?: () => void;
}

export const InitiativeStatusBoard: React.FC<Props> = ({
  initiatives,
  onMoveStatus,
  onOpenNewModal,
}) => {
  const columns: { status: InitiativeStatus; title: string; color: string; icon: React.ComponentType<{ size: number; color: string }> }[] = [
    { status: 'NOT_STARTED', title: 'Not Started', color: '#94A3B8', icon: Clock },
    { status: 'IN_PROGRESS', title: 'In Progress', color: '#38BDF8', icon: PlayCircle },
    { status: 'BLOCKED', title: 'Blocked / At Risk', color: '#EF4444', icon: AlertOctagon },
    { status: 'COMPLETED', title: 'Completed & Realized', color: '#10B981', icon: CheckCircle2 },
    { status: 'DISMISSED', title: 'Dismissed', color: '#64748B', icon: XCircle },
  ];

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(5, 1fr)',
      gap: '12px',
      alignItems: 'flex-start',
      overflowX: 'auto',
      paddingBottom: '12px',
    }}>
      {columns.map((col) => {
        const colItems = initiatives.filter((i) => i.status === col.status);
        const Icon = col.icon;

        return (
          <div
            key={col.status}
            style={{
              background: '#04060A',
              border: '1px solid #141C28',
              borderRadius: '10px',
              padding: '12px',
              minHeight: '480px',
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            {/* Column Header */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '12px',
              paddingBottom: '8px',
              borderBottom: '1px solid #101622',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Icon size={14} color={col.color} />
                <span style={{ fontSize: '11.5px', fontWeight: 800, color: '#FFFFFF' }}>
                  {col.title}
                </span>
              </div>

              <span style={{
                fontSize: '10.5px',
                fontWeight: 800,
                color: col.color,
                background: 'rgba(255, 255, 255, 0.05)',
                padding: '1px 6px',
                borderRadius: '4px',
              }}>
                {colItems.length}
              </span>
            </div>

            {/* Column Cards */}
            <div style={{ flex: 1 }}>
              {colItems.length === 0 ? (
                <div style={{
                  padding: '24px 8px',
                  textAlign: 'center',
                  color: '#475569',
                  fontSize: '11px',
                  fontStyle: 'italic',
                }}>
                  No initiatives in this state.
                </div>
              ) : (
                colItems.map((item) => (
                  <InitiativeCard
                    key={item.id}
                    initiative={item}
                    onMoveStatus={onMoveStatus}
                  />
                ))
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
