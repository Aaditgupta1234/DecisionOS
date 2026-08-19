/**
 * Unified Search Entity across 11 core intelligence types
 */
export type SearchEntityType =
  | 'KPI'
  | 'PORTFOLIO'
  | 'FINDING'
  | 'ROOT_CAUSE'
  | 'RECOMMENDATION'
  | 'INITIATIVE'
  | 'DECISION'
  | 'REPORT'
  | 'ALERT'
  | 'SCENARIO'
  | 'BENCHMARK'
  | 'PLAYBOOK'
  | 'AGENT';

export interface SearchEntity {
  id: string;
  code: string;
  type: SearchEntityType;
  title: string;
  subtitle: string;
  category: string;
  badge?: string;
  badgeColor?: string;
  route: string;
  actionShortcut?: string;
}
