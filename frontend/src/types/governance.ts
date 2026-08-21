/**
 * Governance Suite – Typed response interfaces for frontend/backend contract alignment.
 *
 * Covers:
 *   GET /api/v1/os/governance/scorecard
 *   GET /api/v1/ai-governance/report
 *   GET /api/v1/security-center/posture
 */

// ---------------------------------------------------------------------------
// Governance Center
// ---------------------------------------------------------------------------

export interface GovernanceDecision {
  code: string;
  title: string;
  type: string;
  owner: string;
  expected_value?: string;
  realized_value?: string;
  accuracy?: string;
  status: string;
  compliance: string;
}

export interface GovernanceScorecardResponse {
  governance_health_score?: number;
  governance_health?: number;
  decision_effectiveness_pct?: number;
  decision_effectiveness?: number;
  realized_decision_value?: string | number;
  board_directive_compliance?: string | number;
  policy_rules_active?: number;
  policy_violations?: number;
  decisions?: GovernanceDecision[];
  active_reviews?: number;
  pending_approvals?: number;
  open_exceptions?: number;
  compliance_score?: number;
}

// ---------------------------------------------------------------------------
// AI Governance Center
// ---------------------------------------------------------------------------

export interface AIGovernanceInteraction {
  id: string;
  user: string;
  query: string;
  grounded_urns: string[];
  model: string;
  latency_ms: number;
  cost: string;
  status: string;
  timestamp: string;
}

export interface AIGovernanceReportResponse {
  total_ai_interactions: number;
  grounded_citation_rate: string;
  hallucination_rate: string;
  average_evidence_coverage: number;
  monthly_token_cost: string;
  average_latency_ms: number;
  recent_interactions: AIGovernanceInteraction[];
  executive_trust_score: number;
}

export interface AIProvider {
  name: string;
  description: string;
  is_active: boolean;
  default_model: string;
  supported_models: string[];
}

export interface AIProvidersResponse {
  active_provider: string;
  active_model: string;
  providers: AIProvider[];
}

// ---------------------------------------------------------------------------
// Security Center
// ---------------------------------------------------------------------------

export interface SecurityControl {
  control: string;
  status: string;
  framework?: string;
}

export interface SecurityPostureResponse {
  overall_security_score: number;
  soc2_type_ii_status: string;
  gdpr_compliance_status: string;
  iso_27001_readiness: string;
  threat_events_past_24h: number;
  mfa_adoption_rate: string;
  active_security_controls: SecurityControl[];
  audit_hash: string;
}
