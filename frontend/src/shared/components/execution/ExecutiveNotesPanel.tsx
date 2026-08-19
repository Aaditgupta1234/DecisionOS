import React from 'react';
import { FileText, UserCheck, CheckCircle2, MessageSquare } from 'lucide-react';

interface NoteItem {
  author: string;
  role: string;
  date: string;
  note: string;
}

interface Props {
  notes?: NoteItem[];
}

export const ExecutiveNotesPanel: React.FC<Props> = ({
  notes = [
    { author: 'Elena Rostova', role: 'Chief Executive Officer', date: 'Aug 24, 2026', note: 'Approved $25K discretionary budget for SE customer credit vouchers. Mandated courier penalty enforcement as prerequisite.' },
    { author: 'Marcus Vance', role: 'VP Customer Success', date: 'Aug 28, 2026', note: 'Batch 1 of customer credit incentives dispatched (420 customers). Early 48-hour conversion tracking at 41.2% repeat orders.' },
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
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px' }}>
        <MessageSquare size={16} color="#38BDF8" />
        <h4 style={{ fontSize: '13.5px', fontWeight: 800, color: '#FFFFFF', margin: 0, textTransform: 'uppercase' }}>
          Executive Committee Review Notes & Directives
        </h4>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {notes.map((n, idx) => (
          <div
            key={idx}
            style={{
              background: '#05070B',
              border: '1px solid #141C28',
              borderRadius: '8px',
              padding: '12px 14px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ fontSize: '12.5px', fontWeight: 800, color: '#FFFFFF' }}>{n.author}</span>
                <span style={{ fontSize: '11px', color: '#64748B' }}>({n.role})</span>
              </div>
              <span style={{ fontSize: '10.5px', color: '#94A3B8' }}>{n.date}</span>
            </div>

            <p style={{ fontSize: '12px', color: '#CBD5E1', margin: 0, lineHeight: 1.45 }}>
              {n.note}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
