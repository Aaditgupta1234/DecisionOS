/**
 * Enterprise Event Bus Model
 */
export type EnterpriseEventType =
  | 'ALERT_CREATED'
  | 'ALERT_ESCALATED'
  | 'SCENARIO_COMPLETED'
  | 'DECISION_APPROVED'
  | 'DECISION_BLOCKED'
  | 'INITIATIVE_APPROVED'
  | 'INITIATIVE_COMPLETED'
  | 'REPORT_PUBLISHED'
  | 'PLAYBOOK_EXECUTED'
  | 'AGENT_TASK_DISPATCHED'
  | 'DATASET_PROCESSED';

export interface EnterpriseEvent<T = Record<string, unknown>> {
  id: string;
  type: EnterpriseEventType;
  payload: T;
  source: string;
  timestamp: string;
  correlationId?: string;
}
