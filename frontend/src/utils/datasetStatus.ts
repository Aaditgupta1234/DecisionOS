import { Dataset } from '../types';

export interface DatasetStatusDisplay {
  badge: 'Verified Telemetry' | 'Quarantined Telemetry' | 'Empty Dataset' | 'Invalid Dataset' | 'No Dataset';
  statusLabel: string;
  statusKey: 'VERIFIED' | 'UNVERIFIED_SCHEMA' | 'UNIVARIATE' | 'EMPTY' | 'INVALID';
  badgeColor: string;
  badgeBg: string;
  badgeBorder: string;
  isQuarantined: boolean;
}

/**
 * Resolves the display metadata for a dataset based strictly on its `dataset_status`
 * and schema verification state as the single source of truth.
 *
 * Rules:
 * - VERIFIED: Badge = 'Verified Telemetry', Status = 'Verified'
 * - UNVERIFIED_SCHEMA: Badge = 'Quarantined Telemetry', Status = 'Unverified Schema Contract'
 * - UNIVARIATE: Badge = 'Quarantined Telemetry', Status = 'Insufficient Telemetry'
 * - EMPTY: Badge = 'Empty Dataset', Status = 'Empty Dataset'
 * - INVALID: Badge = 'Invalid Dataset', Status = 'Invalid Dataset'
 *
 * No UI component may display "Verified Telemetry" unless dataset_status === "VERIFIED".
 */
export function getDatasetStatusDisplay(dataset?: Dataset | null): DatasetStatusDisplay {
  if (!dataset) {
    return {
      badge: 'No Dataset',
      statusLabel: 'No Active Source',
      statusKey: 'EMPTY',
      badgeColor: '#94A3B8',
      badgeBg: 'rgba(148, 163, 184, 0.12)',
      badgeBorder: 'rgba(148, 163, 184, 0.30)',
      isQuarantined: false,
    };
  }

  const meta = dataset.metadata_json || {};
  const rawStatus = (dataset.dataset_status || meta.dataset_status || '').toUpperCase();
  const schemaVerified = dataset.schema_verified ?? meta.schema_verified;
  const colCount = dataset.column_count ?? dataset.columns?.length ?? 2;
  const rowCount = dataset.record_count ?? dataset.row_count ?? 100;

  let resolvedStatus: 'VERIFIED' | 'UNVERIFIED_SCHEMA' | 'UNIVARIATE' | 'EMPTY' | 'INVALID' = 'VERIFIED';

  if (rawStatus === 'INVALID') {
    resolvedStatus = 'INVALID';
  } else if (rawStatus === 'EMPTY' || rowCount === 0) {
    resolvedStatus = 'EMPTY';
  } else if (rawStatus === 'UNIVARIATE' || (colCount > 0 && colCount < 2)) {
    resolvedStatus = 'UNIVARIATE';
  } else if (rawStatus === 'UNVERIFIED_SCHEMA' || schemaVerified === false) {
    resolvedStatus = 'UNVERIFIED_SCHEMA';
  } else if (rawStatus === 'VERIFIED' || schemaVerified === true) {
    resolvedStatus = 'VERIFIED';
  } else {
    // If not explicitly set, inspect column names against recognized business concepts
    const cols = (dataset.columns || []).map((c) => (c.original_name || c.normalized_name || '').toLowerCase());
    const RECOGNIZED = [
      'revenue', 'sales', 'profit', 'margin', 'cost', 'expense',
      'customer', 'churn', 'retention', 'support', 'tickets', 'sla',
      'delivery', 'shipment', 'inventory', 'orders', 'transactions',
      'utilization', 'availability', 'latency', 'risk', 'compute',
      'amount', 'price', 'mrr', 'arr', 'spend', 'charge', 'fee', 'tenure'
    ];
    const hasRecognized = cols.length > 0 && cols.some((c) => RECOGNIZED.some((rec) => c.includes(rec)));
    resolvedStatus = hasRecognized ? 'VERIFIED' : 'UNVERIFIED_SCHEMA';
  }

  switch (resolvedStatus) {
    case 'UNVERIFIED_SCHEMA':
      return {
        badge: 'Quarantined Telemetry',
        statusLabel: 'Unverified Schema Contract',
        statusKey: 'UNVERIFIED_SCHEMA',
        badgeColor: '#F59E0B',
        badgeBg: 'rgba(245, 158, 11, 0.12)',
        badgeBorder: 'rgba(245, 158, 11, 0.30)',
        isQuarantined: true,
      };
    case 'UNIVARIATE':
      return {
        badge: 'Quarantined Telemetry',
        statusLabel: 'Insufficient Telemetry',
        statusKey: 'UNIVARIATE',
        badgeColor: '#F59E0B',
        badgeBg: 'rgba(245, 158, 11, 0.12)',
        badgeBorder: 'rgba(245, 158, 11, 0.30)',
        isQuarantined: true,
      };
    case 'EMPTY':
      return {
        badge: 'Empty Dataset',
        statusLabel: 'Empty Dataset',
        statusKey: 'EMPTY',
        badgeColor: '#94A3B8',
        badgeBg: 'rgba(148, 163, 184, 0.12)',
        badgeBorder: 'rgba(148, 163, 184, 0.30)',
        isQuarantined: true,
      };
    case 'INVALID':
      return {
        badge: 'Invalid Dataset',
        statusLabel: 'Invalid Dataset',
        statusKey: 'INVALID',
        badgeColor: '#EF4444',
        badgeBg: 'rgba(239, 68, 68, 0.12)',
        badgeBorder: 'rgba(239, 68, 68, 0.30)',
        isQuarantined: true,
      };
    case 'VERIFIED':
    default:
      return {
        badge: 'Verified Telemetry',
        statusLabel: 'Verified',
        statusKey: 'VERIFIED',
        badgeColor: '#10B981',
        badgeBg: 'rgba(16, 185, 129, 0.12)',
        badgeBorder: 'rgba(16, 185, 129, 0.30)',
        isQuarantined: false,
      };
  }
}
