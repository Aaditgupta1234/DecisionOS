import { describe, it, expect } from 'vitest';
import { buildHarmonizedExecutiveIntelligence } from '../features/enterprise-os/enterpriseIntelligenceEngine';
import { Dataset, IntelligenceReportResponse, BusinessHealthResponse } from '../types';

describe('Enterprise Intelligence Quarantine & Resilience Framework', () => {
  it('activates quarantine mode and caps confidence at <= 44% for unverified schemas', () => {
    const unverifiedDataset: Partial<Dataset> = {
      id: 'd0000000-0000-0000-0000-000000000001',
      name: 'Garbage Dataset',
      column_count: 3,
      columns: [
        { id: 'c1', original_name: 'foo', normalized_name: 'foo' },
        { id: 'c2', original_name: 'bar', normalized_name: 'bar' },
        { id: 'c3', original_name: 'baz', normalized_name: 'baz' },
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
    expect(intel.snapshot.confidenceScore).toBeLessThanOrEqual(44);
    expect(intel.primaryRisk.title).toBe('UNVERIFIED SCHEMA CONTRACT');
    expect(intel.rootCause.title).toBe('Not Assessable');
    expect(intel.rootCause.attributions).toEqual([]);
    expect(intel.recommendedPrograms).toEqual([]);
    expect(intel.recommendedAction.primaryAction).toBe('No Actionable Intelligence Available');
    expect(intel.dataGroundingStatus.badge).toBe('UNVERIFIED SCHEMA CONTRACT');
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
    expect(intel.snapshot.confidenceScore).toBeLessThanOrEqual(44);
    expect(intel.primaryRisk.title).toBe('UNIVARIATE TELEMETRY');
    expect(intel.rootCause.title).toBe('CAUSAL ATTRIBUTION SUSPENDED');
    expect(intel.rootCause.causalPathway).toContain('CAUSAL ATTRIBUTION SUSPENDED');
    expect(intel.rootCause.attributions).toEqual([]);
    expect(intel.recommendedPrograms).toEqual([]);
    expect(intel.workspaces.diagnosticGraph.statusDetail).toContain('CAUSAL ATTRIBUTION SUSPENDED');
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
});
