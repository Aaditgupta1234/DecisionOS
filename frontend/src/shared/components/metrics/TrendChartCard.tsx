import React, { useState } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

interface DataPoint {
  period: string;
  value: number;
  comparisonValue?: number;
}

interface Props {
  title: string;
  metricKey?: string;
  data?: DataPoint[];
  unit?: string;
}

export const TrendChartCard: React.FC<Props> = ({
  title = 'Revenue Performance Trend',
  data,
  unit = '$',
}) => {
  const [periodMode, setPeriodMode] = useState<'MoM' | 'QoQ'>('MoM');

  const defaultDataMoM: DataPoint[] = [
    { period: 'Jan', value: 320000, comparisonValue: 290000 },
    { period: 'Feb', value: 345000, comparisonValue: 310000 },
    { period: 'Mar', value: 390000, comparisonValue: 330000 },
    { period: 'Apr', value: 410000, comparisonValue: 360000 },
    { period: 'May', value: 460000, comparisonValue: 390000 },
    { period: 'Jun', value: 490000, comparisonValue: 420000 },
    { period: 'Jul', value: 540000, comparisonValue: 460000 },
    { period: 'Aug', value: 610000, comparisonValue: 510000 },
  ];

  const defaultDataQoQ: DataPoint[] = [
    { period: 'Q1 2025', value: 1055000, comparisonValue: 930000 },
    { period: 'Q2 2025', value: 1360000, comparisonValue: 1170000 },
    { period: 'Q3 2025', value: 1640000, comparisonValue: 1390000 },
    { period: 'Q4 2025', value: 1980000, comparisonValue: 1620000 },
  ];

  const chartData = data && data.length > 0 ? data : periodMode === 'MoM' ? defaultDataMoM : defaultDataQoQ;

  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '12px',
      padding: '20px',
      marginBottom: '24px',
    }}>
      {/* Header with Period Comparison Toggles */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div>
          <h3 style={{ fontSize: '15px', fontWeight: 700, color: '#FFFFFF', margin: 0 }}>
            {title}
          </h3>
          <span style={{ fontSize: '11px', color: '#64748B' }}>
            Historical transactional progression vs prior period
          </span>
        </div>

        {/* Comparison Toggle */}
        <div style={{ display: 'flex', background: '#04060A', border: '1px solid #1E293B', borderRadius: '6px', padding: '2px' }}>
          <button
            type="button"
            onClick={() => setPeriodMode('MoM')}
            style={{
              background: periodMode === 'MoM' ? '#1D4ED8' : 'transparent',
              color: periodMode === 'MoM' ? '#FFFFFF' : '#94A3B8',
              border: 'none',
              borderRadius: '4px',
              padding: '4px 10px',
              fontSize: '11px',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            Month-over-Month
          </button>
          <button
            type="button"
            onClick={() => setPeriodMode('QoQ')}
            style={{
              background: periodMode === 'QoQ' ? '#1D4ED8' : 'transparent',
              color: periodMode === 'QoQ' ? '#FFFFFF' : '#94A3B8',
              border: 'none',
              borderRadius: '4px',
              padding: '4px 10px',
              fontSize: '11px',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            Quarter-over-Quarter
          </button>
        </div>
      </div>

      {/* Chart Canvas */}
      <div style={{ width: '100%', height: '240px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="metricGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#38BDF8" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#38BDF8" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="compareGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#64748B" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#64748B" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#141C28" vertical={false} />
            <XAxis dataKey="period" stroke="#475569" fontSize={11} tickLine={false} />
            <YAxis
              stroke="#475569"
              fontSize={11}
              tickLine={false}
              tickFormatter={(v) => (v >= 1000000 ? `${(v / 1000000).toFixed(1)}M` : v >= 1000 ? `${(v / 1000).toFixed(0)}K` : `${v}`)}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#090D14',
                borderColor: '#1E293B',
                borderRadius: '8px',
                fontSize: '12px',
                color: '#FFFFFF',
              }}
              formatter={(val: any) => [`$${Number(val).toLocaleString()}`, 'Value']}
            />
            <Area
              type="monotone"
              dataKey="comparisonValue"
              stroke="#475569"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              fillOpacity={1}
              fill="url(#compareGradient)"
              name="Prior Period"
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#38BDF8"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#metricGradient)"
              name="Current Value"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
