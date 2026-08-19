import React from 'react';
import { Drawer } from '../../design-system/Drawer';
import { Badge } from '../../design-system/Badge';
import { EvidenceReference } from '../../types/EvidenceReference';
import { getConfidenceScore } from '../../types/ConfidenceScore';
import { GitMerge, Database, ShieldCheck, CheckCircle2 } from 'lucide-react';

interface EvidenceDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  evidenceList: EvidenceReference[];
  causalPath?: string[];
}

export const EvidenceDrawer: React.FC<EvidenceDrawerProps> = ({
  isOpen,
  onClose,
  title = 'Grounded Evidence & Lineage Citation',
  evidenceList,
  causalPath = [
    'KPI: Telemetry Ingestion',
    'RCA: Southeastern Transit Delays',
    'REC: Carrier Reallocation',
    'INIT: SLA Penalty Enforcement',
  ],
}) => {
  return (
    <Drawer isOpen={isOpen} onClose={onClose} title={title} subtitle="Deterministic Grounding Ledger">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {/* Causal DAG Path */}
        <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '10px', padding: '16px' }}>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', marginBottom: '8px' }}>
            CAUSAL REASONING CHAIN
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {causalPath.map((node, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', color: '#F1F5F9' }}>
                <span style={{ color: '#38BDF8', fontWeight: 800 }}>{idx + 1}.</span>
                <span>{node}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Evidence Items */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <span style={{ fontSize: '0.82rem', fontWeight: 800, color: '#FFFFFF' }}>Grounded Data Sources</span>
          {evidenceList.map((item, idx) => {
            const conf = getConfidenceScore(item.confidence);
            return (
              <div
                key={idx}
                style={{
                  background: 'rgba(15, 23, 42, 0.6)',
                  border: '1px solid #1E293B',
                  borderRadius: '10px',
                  padding: '14px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <code style={{ fontSize: '0.75rem', color: '#38BDF8' }}>{item.urn}</code>
                  <Badge variant={conf.tier === 'VERY_HIGH' ? 'emerald' : 'sky'} size="sm">
                    {conf.value}% Confidence
                  </Badge>
                </div>
                <div style={{ fontSize: '0.78rem', color: '#94A3B8' }}>{item.summary || 'Verified live data telemetry citation.'}</div>
                <div style={{ fontSize: '0.7rem', color: '#64748B' }}>Timestamp: {item.timestamp}</div>
              </div>
            );
          })}
        </div>
      </div>
    </Drawer>
  );
};
