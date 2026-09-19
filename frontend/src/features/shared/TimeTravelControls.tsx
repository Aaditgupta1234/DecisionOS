import React, { useState } from 'react';
import { Clock } from 'lucide-react';

export const TimeTravelControls: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState('LIVE (Current Telemetry)');

  const snapshots = [
    'LIVE (Current Telemetry)',
    '2026-03-15 (Q1 Strategy Review)',
    '2026-02-01 (Pre-Courier Baseline)',
    '2025-12-31 (Year-End Snapshot)',
  ];

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        background: 'rgba(12, 17, 26, 0.95)',
        border: '1px solid #1E293B',
        borderRadius: '6px',
        padding: '0 10px',
        height: '32px',
        minWidth: '160px',
        flexShrink: 0,
      }}
    >
      <Clock size={13} color="#38BDF8" style={{ flexShrink: 0 }} />
      <span style={{ fontSize: '0.66rem', color: '#64748B', fontWeight: 800, whiteSpace: 'nowrap', letterSpacing: '0.04em' }}>TIME:</span>
      <select
        value={selectedDate}
        onChange={(e) => setSelectedDate(e.target.value)}
        style={{
          background: 'transparent',
          border: 'none',
          color: selectedDate.startsWith('LIVE') ? '#10B981' : '#F59E0B',
          fontSize: '0.72rem',
          fontWeight: 800,
          outline: 'none',
          cursor: 'pointer',
          width: '100%',
          maxWidth: '170px',
          textOverflow: 'ellipsis',
        }}
      >
        {snapshots.map((s) => (
          <option key={s} value={s} style={{ background: '#090D14', color: '#FFFFFF' }}>
            {s}
          </option>
        ))}
      </select>
    </div>
  );
};


