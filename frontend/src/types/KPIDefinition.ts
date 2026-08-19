/**
 * Enterprise KPI Dictionary Schema
 */
export interface KPIDefinition {
  id: string;
  metricName: string;
  category: 'REVENUE' | 'RETENTION' | 'OPERATIONS' | 'RISK' | 'EFFICIENCY';
  formula: string;
  owner: string;
  ownerRole: string;
  dataSource: string;
  refreshFrequency: 'REALTIME' | 'HOURLY' | 'DAILY' | 'MONTHLY';
  unit: string;
  targetValue: number;
  currentValue: number;
  description: string;
  version: string;
  isBoardMetric: boolean;
}
