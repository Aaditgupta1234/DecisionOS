import { describe, it, expect } from 'vitest';
import { buildHarmonizedExecutiveIntelligence } from '../features/enterprise-os/enterpriseIntelligenceEngine';
import { getDatasetStatusDisplay } from '../utils/datasetStatus';
import { Dataset, IntelligenceReportResponse, BusinessHealthResponse } from '../types';

describe('Enterprise Intelligence Quarantine & Resilience Framework', () => {
  it('activates quarantine mode and caps confidence at <= 44% for unverified schemas', () => {
    const unverifiedDataset: Partial<Dataset> = {
      id: 'd0000000-0000-0000-0000-000000000001',
      name: 'Garbage Dataset',
      column_count: 3,
      columns: [
        { id: 'c1', original_name: 'abc', normalized_name: 'abc' },
        { id: 'c2', original_name: 'xyz', normalized_name: 'xyz' },
        { id: 'c3', original_name: 'qwerty', normalized_name: 'qwerty' },
      ],
      metadata_json: {
        schema_verified: false,
        dataset_status: 'UNVERIFIED_SCHEMA',
        schema_match_rate: 0.0,
      },
    } as any;

    const intel = buildHarmonizedExecutiveIntelligence(
      null,
      null,
      'Garbage Dataset',
      unverifiedDataset as Dataset
    );

    expect(intel.intelligenceSuppressed).toBe(true);
    expect(intel.healthScore).toBeNull();
    expect(intel.healthClassification).toBe('Not Assessable');
    expect(intel.primaryRisk.title).toBe('Not Assessable');
    expect(intel.rootCause.title).toBe('Causal Attribution Suspended');
    expect(intel.rootCause.attributions).toEqual([]);
    expect(intel.rootCause.chain).toEqual([]);
    expect(intel.rootCause.datasetEvidence).toBe('Insufficient Telemetry');
    expect(intel.rootCause.businessInterpretation).toBe('No Actionable Intelligence Available');
    expect(intel.recommendedPrograms).toEqual([]);
    expect(intel.recommendedAction.primaryAction).toBe('No Actionable Intelligence Available');
    expect(intel.recommendedAction.targetKPIImpact).toBe('Not Assessable');
    expect(intel.workspaces.diagnosticGraph.badge).toBe('Insufficient Telemetry');
    expect(intel.snapshot.confidenceScore).toBeLessThanOrEqual(44);
    expect(intel.snapshot.financialExposure).toBe('Not Assessable');
    expect(intel.dataGroundingStatus.badge).toBe('UNVERIFIED SCHEMA CONTRACT');
    expect(intel.dataGroundingStatus.subtitle).toBe('No recognized enterprise business metrics detected.');
    expect(intel.validationPassed).toBe(true);
  });

  it('activates univariate quarantine when dataset has fewer than 2 columns', () => {
    const univariateDataset: Partial<Dataset> = {
      id: 'd0000000-0000-0000-0000-000000000002',
      name: 'Single Column Telemetry',
      column_count: 1,
      columns: [{ id: 'c1', original_name: 'customer_id', normalized_name: 'customer_id' }],
      metadata_json: {
        schema_verified: true,
        dataset_status: 'UNIVARIATE',
      },
    } as any;

    const intel = buildHarmonizedExecutiveIntelligence(
      null,
      null,
      'Single Column Telemetry',
      univariateDataset as Dataset
    );

    expect(intel.intelligenceSuppressed).toBe(true);
    expect(intel.healthScore).toBeNull();
    expect(intel.healthClassification).toBe('Not Assessable');
    expect(intel.primaryRisk.title).toBe('Not Assessable');
    expect(intel.rootCause.title).toBe('Causal Attribution Suspended');
    expect(intel.rootCause.attributions).toEqual([]);
    expect(intel.recommendedPrograms).toEqual([]);
    expect(intel.recommendedAction.primaryAction).toBe('No Actionable Intelligence Available');
    expect(intel.workspaces.diagnosticGraph.badge).toBe('Insufficient Telemetry');
    expect(intel.snapshot.confidenceScore).toBeLessThanOrEqual(44);
    expect(intel.validationPassed).toBe(true);
  });

  it('generates rich actionable intelligence and high confidence for verified enterprise schemas', () => {
    const verifiedDataset: Partial<Dataset> = {
      id: 'd0000000-0000-0000-0000-000000000003',
      name: 'Customer Churn Telemetry',
      column_count: 4,
      columns: [
        { id: 'c1', original_name: 'customer_id', normalized_name: 'customer_id' },
        { id: 'c2', original_name: 'monthly_revenue', normalized_name: 'monthly_revenue' },
        { id: 'c3', original_name: 'churn_risk', normalized_name: 'churn_risk' },
        { id: 'c4', original_name: 'support_tickets', normalized_name: 'support_tickets' },
      ],
      metadata_json: {
        schema_verified: true,
        dataset_status: 'VERIFIED',
        schema_match_rate: 1.0,
      },
    } as any;

    const intel = buildHarmonizedExecutiveIntelligence(
      null,
      null,
      'Customer Churn Telemetry',
      verifiedDataset as Dataset
    );

    expect(intel.intelligenceSuppressed).toBe(false);
    expect(intel.snapshot.confidenceScore).toBeGreaterThan(60);
    expect(intel.rootCause.attributions.length).toBeGreaterThan(0);
    expect(intel.recommendedPrograms.length).toBeGreaterThan(0);
    expect(intel.recommendedAction.primaryAction).not.toBe('No Actionable Intelligence Available');
  });

  it('handles empty report and health responses gracefully with deterministic defaults', () => {
    const intel = buildHarmonizedExecutiveIntelligence(null, null, undefined, null);
    expect(intel).toBeDefined();
    expect(intel.healthScore).toBeGreaterThanOrEqual(0);
    expect(intel.healthScore).toBeLessThanOrEqual(100);
    expect(intel.primaryRisk.title).toBeDefined();
    expect(intel.rootCause.title).toBeDefined();
    expect(intel.executiveNarrative).toBeDefined();
  });

  describe('Dataset Card Status Mapping & Single Source of Truth', () => {
    it('maps UNVERIFIED_SCHEMA dataset to Quarantined Telemetry and never Verified Telemetry', () => {
      const ds: Partial<Dataset> = {
        name: 'Garbage Dataset',
        column_count: 3,
        metadata_json: {
          schema_verified: false,
          dataset_status: 'UNVERIFIED_SCHEMA',
        },
      } as any;

      const display = getDatasetStatusDisplay(ds as Dataset);
      expect(display.badge).toBe('Quarantined Telemetry');
      expect(display.badge).not.toBe('Verified Telemetry');
      expect(display.statusLabel).toBe('Unverified Schema Contract');
      expect(display.isQuarantined).toBe(true);
    });

    it('maps UNIVARIATE dataset to Quarantined Telemetry and Insufficient Telemetry', () => {
      const ds: Partial<Dataset> = {
        name: 'Single Column',
        column_count: 1,
        metadata_json: {
          schema_verified: true,
          dataset_status: 'UNIVARIATE',
        },
      } as any;

      const display = getDatasetStatusDisplay(ds as Dataset);
      expect(display.badge).toBe('Quarantined Telemetry');
      expect(display.badge).not.toBe('Verified Telemetry');
      expect(display.statusLabel).toBe('Insufficient Telemetry');
      expect(display.isQuarantined).toBe(true);
    });

    it('maps EMPTY dataset to Empty Dataset badge', () => {
      const ds: Partial<Dataset> = {
        name: 'Empty CSV',
        record_count: 0,
        row_count: 0,
        metadata_json: {
          dataset_status: 'EMPTY',
        },
      } as any;

      const display = getDatasetStatusDisplay(ds as Dataset);
      expect(display.badge).toBe('Empty Dataset');
      expect(display.badge).not.toBe('Verified Telemetry');
      expect(display.isQuarantined).toBe(true);
    });

    it('maps INVALID dataset to Invalid Dataset badge', () => {
      const ds: Partial<Dataset> = {
        name: 'Corrupt CSV',
        metadata_json: {
          dataset_status: 'INVALID',
        },
      } as any;

      const display = getDatasetStatusDisplay(ds as Dataset);
      expect(display.badge).toBe('Invalid Dataset');
      expect(display.badge).not.toBe('Verified Telemetry');
      expect(display.isQuarantined).toBe(true);
    });

    it('maps VERIFIED dataset to Verified Telemetry', () => {
      const ds: Partial<Dataset> = {
        name: 'Customer Churn',
        column_count: 4,
        record_count: 1000,
        metadata_json: {
          schema_verified: true,
          dataset_status: 'VERIFIED',
        },
      } as any;

      const display = getDatasetStatusDisplay(ds as Dataset);
      expect(display.badge).toBe('Verified Telemetry');
      expect(display.statusLabel).toBe('Verified');
      expect(display.isQuarantined).toBe(false);
    });
  });
});
