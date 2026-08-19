import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';

export const ExecutionAnalyticsTimeline: React.FC = () => {
  const data = [
    { period: 'Week 1', started: 1, completed: 0, recoveryRealized: 0 },
    { period: 'Week 2', started: 3, completed: 1, recoveryRealized: 45 },
    { period: 'Week 3', started: 5, completed: 2, recoveryRealized: 90 },
    { period: 'Week 4 (Current)', started: 6, completed: 2, recoveryRealized: 124 },
  ];

  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '12px',
      padding: '20px',
      marginBottom: '24px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div>
          <h4 style={{ fontSize: '13.5px', fontWeight: 800, color: '#FFFFFF', margin: 0, textTransform: 'uppercase' }}>
            Portfolio Execution Velocity & Cumulative ARR Realization
          </h4>
          <span style={{ fontSize: '11px', color: '#64748B' }}>Tracking initiative throughput and cumulative recovery</span>
        </div>

        <span style={{ fontSize: '11px', color: '#10B981', fontWeight: 700 }}>
          +$124K ARR Realized
        </span>
      </div>

      <div style={{ width: '100%', height: '200px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#141C28" vertical={false} />
            <XAxis dataKey="period" stroke="#475569" fontSize={10.5} tickLine={false} />
            <YAxis stroke="#475569" fontSize={10.5} tickLine={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#090D14',
                borderColor: '#1E293B',
                borderRadius: '8px',
                fontSize: '12px',
                color: '#FFFFFF',
              }}
            />
            <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
            <Line type="monotone" dataKey="started" stroke="#38BDF8" strokeWidth={2} name="Initiatives Started" />
            <Line type="monotone" dataKey="completed" stroke="#10B981" strokeWidth={2} name="Initiatives Completed" />
            <Line type="monotone" dataKey="recoveryRealized" stroke="#F59E0B" strokeWidth={2.5} name="Realized ARR ($K)" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
