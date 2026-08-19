import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { Activity, TrendingUp } from 'lucide-react';

interface Props {
  kpiTitle?: string;
  preLaunchValue?: string;
  postLaunchValue?: string;
  delta?: string;
}

export const KPIRecoveryChart: React.FC<Props> = ({
  kpiTitle = 'Customer Retention Trajectory (Pre vs. Post Initiative Launch)',
  preLaunchValue = '85.8%',
  postLaunchValue = '88.9%',
  delta = '+3.1% Recovery',
}) => {
  const data = [
    { period: 'W-4', value: 90.1, label: 'Baseline' },
    { period: 'W-3', value: 88.2, label: 'SLA Failure' },
    { period: 'W-2', value: 86.4, label: 'Anomaly' },
    { period: 'W-1 (Launch)', value: 85.8, label: 'Trough' },
    { period: 'W+1', value: 86.7, label: 'Incentives Active' },
    { period: 'W+2', value: 87.9, label: 'SLA Enforced' },
    { period: 'W+3 (Current)', value: 88.9, label: 'Current Lift' },
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
          <h4 style={{ fontSize: '13.5px', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
            {kpiTitle}
          </h4>
          <span style={{ fontSize: '11px', color: '#64748B' }}>
            Pre-Launch Trough: {preLaunchValue} → Current Realization: {postLaunchValue}
          </span>
        </div>

        <div style={{
          background: 'rgba(16, 185, 129, 0.1)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          color: '#10B981',
          padding: '3px 10px',
          borderRadius: '5px',
          fontSize: '12px',
          fontWeight: 800,
        }}>
          {delta}
        </div>
      </div>

      <div style={{ width: '100%', height: '180px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="kpiRecoveryGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10B981" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#10B981" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#141C28" vertical={false} />
            <XAxis dataKey="period" stroke="#475569" fontSize={10.5} tickLine={false} />
            <YAxis domain={[84, 92]} stroke="#475569" fontSize={10.5} tickLine={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#090D14',
                borderColor: '#1E293B',
                borderRadius: '8px',
                fontSize: '12px',
                color: '#FFFFFF',
              }}
            />
            <Area type="monotone" dataKey="value" stroke="#10B981" strokeWidth={2.5} fillOpacity={1} fill="url(#kpiRecoveryGrad)" name="Retention %" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
