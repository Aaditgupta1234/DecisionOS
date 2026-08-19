/**
 * Universal Evidence Reference Standard (URN Lineage Schema)
 * Format: "KPI:RETENTION:SNP-042", "ROOTCAUSE:RC-004", "REC:REC-001", "INIT:INIT-051"
 */
export interface EvidenceReference {
  sourceType: 'KPI' | 'ROOT_CAUSE' | 'RECOMMENDATION' | 'SCENARIO' | 'DECISION' | 'INITIATIVE' | 'ALERT' | 'DATASET';
  sourceId: string;
  urn: string;
  snapshotId?: string;
  confidence: number;
  evidenceCount?: number;
  timestamp: string;
  summary?: string;
}

export const formatURN = (type: EvidenceReference['sourceType'], id: string): string => {
  return `${type}:${id.toUpperCase()}`;
};
