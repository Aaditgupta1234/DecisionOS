import React from 'react';
import { ForecastPoint } from '../../types';

interface ConfidenceBandChartProps {
  points: ForecastPoint[];
  metricKey: string;
  height?: number;
}

export const ConfidenceBandChart: React.FC<ConfidenceBandChartProps> = ({
  points,
  metricKey,
  height = 240,
}) => {
  if (!points || points.length === 0) {
    return (
      <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
        No projection points available
      </div>
    );
  }

  // Calculate scaling
  const allValues: number[] = [];
  points.forEach((p) => {
    allValues.push(p.predicted_value);
    if (p.lower_bound !== undefined) allValues.push(p.lower_bound);
    if (p.upper_bound !== undefined) allValues.push(p.upper_bound);
  });

  const minVal = Math.min(...allValues) * 0.95;
  const maxVal = Math.max(...allValues) * 1.05;
  const valRange = maxVal - minVal || 1;

  const width = 600;
  const paddingX = 40;
  const paddingY = 30;
  const chartW = width - 2 * paddingX;
  const chartH = height - 2 * paddingY;

  const getX = (idx: number) => paddingX + (idx / Math.max(1, points.length - 1)) * chartW;
  const getY = (val: number) => height - paddingY - ((val - minVal) / valRange) * chartH;

  // Build points string for polyline & ribbon
  const predCoords = points.map((p, i) => `${getX(i)},${getY(p.predicted_value)}`).join(' ');

  // Ribbon path: lower forward, upper backward
  const upperCoords = points.map((p, i) => `${getX(i)},${getY(p.upper_bound ?? p.predicted_value)}`);
  const lowerCoordsRev = points
    .slice()
    .reverse()
    .map((p, i) => {
      const origIdx = points.length - 1 - i;
      return `${getX(origIdx)},${getY(p.lower_bound ?? p.predicted_value)}`;
    });

  const ribbonPath = `M ${upperCoords.join(' L ')} L ${lowerCoordsRev.join(' L ')} Z`;

  return (
    <div style={{ width: '100%', overflowX: 'auto' }}>
      <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', height, overflow: 'visible' }}>
        {/* Grid lines */}
        <line x1={paddingX} y1={paddingY} x2={width - paddingX} y2={paddingY} stroke="var(--border-subtle)" strokeDasharray="3 3" />
        <line x1={paddingX} y1={paddingY + chartH / 2} x2={width - paddingX} y2={paddingY + chartH / 2} stroke="var(--border-subtle)" strokeDasharray="3 3" />
        <line x1={paddingX} y1={height - paddingY} x2={width - paddingX} y2={height - paddingY} stroke="var(--border-subtle)" />

        {/* Confidence Ribbon */}
        <path d={ribbonPath} fill="rgba(37, 99, 235, 0.15)" stroke="rgba(37, 99, 235, 0.3)" strokeDasharray="2 2" />

        {/* Predicted Line */}
        <polyline points={predCoords} fill="none" stroke="var(--color-primary-light)" strokeWidth="3" />

        {/* Point Dots */}
        {points.map((p, i) => (
          <g key={i}>
            <circle cx={getX(i)} cy={getY(p.predicted_value)} r="4" fill="#ffffff" stroke="var(--color-primary)" strokeWidth="2" />
            <text
              x={getX(i)}
              y={height - 10}
              textAnchor="middle"
              fill="var(--text-muted)"
              fontSize="10"
            >
              {p.period}
            </text>
          </g>
        ))}

        {/* Y Axis Labels */}
        <text x={paddingX - 6} y={paddingY + 4} textAnchor="end" fill="var(--text-muted)" fontSize="10">
          {maxVal >= 1000 ? `${(maxVal / 1000).toFixed(0)}k` : maxVal.toFixed(0)}
        </text>
        <text x={paddingX - 6} y={height - paddingY} textAnchor="end" fill="var(--text-muted)" fontSize="10">
          {minVal >= 1000 ? `${(minVal / 1000).toFixed(0)}k` : minVal.toFixed(0)}
        </text>
      </svg>
    </div>
  );
};
