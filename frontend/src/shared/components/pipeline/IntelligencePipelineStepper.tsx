import React from 'react';
import { Check, Loader2, Database, Table, Activity, AlertTriangle, GitMerge, CheckCircle2, FileText, Sparkles } from 'lucide-react';

export interface PipelineStage {
  id: string;
  name: string;
  shortName: string;
  status: 'completed' | 'running' | 'pending' | 'idle';
  icon: React.FC<{ size?: number; color?: string }>;
}

interface Props {
  activeStageIndex?: number; // 0 to 7, or 8 for all completed
  datasetStatus?: 'READY' | 'PROCESSING' | 'FAILED' | 'PENDING';
}

export const IntelligencePipelineStepper: React.FC<Props> = ({
  datasetStatus = 'READY',
}) => {
  const isReady = datasetStatus === 'READY';
  const isProcessing = datasetStatus === 'PROCESSING';

  const stages = [
    { id: 'ingest', name: '01 Ingestion', shortName: 'Ingestion', icon: Database },
    { id: 'schema', name: '02 Schema Mapping', shortName: 'Schema', icon: Table },
    { id: 'metrics', name: '03 Metrics', shortName: 'Metrics', icon: Activity },
    { id: 'diagnostics', name: '04 Diagnostics', shortName: 'Diagnostics', icon: AlertTriangle },
    { id: 'rootcause', name: '05 Root Cause', shortName: 'Attribution', icon: GitMerge },
    { id: 'actions', name: '06 Recommendations', shortName: 'Actions', icon: CheckCircle2 },
    { id: 'synthesis', name: '07 Executive Brief', shortName: 'Synthesis', icon: FileText },
    { id: 'ai', name: '08 AI Narrative', shortName: 'Autonomous', icon: Sparkles },
  ];

  return (
    <div style={{
      background: 'rgba(8, 11, 17, 0.75)',
      border: '1px solid #1A2230',
      borderRadius: '12px',
      padding: '16px 20px',
      backdropFilter: 'blur(16px)',
      boxShadow: '0 10px 30px rgba(0, 0, 0, 0.5)',
      marginBottom: '24px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: isReady ? '#10B981' : isProcessing ? '#F59E0B' : '#64748B',
            boxShadow: isReady ? '0 0 10px #10B981' : 'none',
          }} />
          <span style={{ fontSize: '11.5px', fontWeight: 700, color: '#E2E8F0', letterSpacing: '0.04em', textTransform: 'uppercase' }}>
            DecisionOS Intelligence Pipeline
          </span>
        </div>

        <span style={{
          fontSize: '10.5px',
          fontWeight: 700,
          color: isReady ? '#10B981' : isProcessing ? '#F59E0B' : '#94A3B8',
          background: isReady ? 'rgba(16, 185, 129, 0.12)' : 'rgba(255, 255, 255, 0.06)',
          border: `1px solid ${isReady ? 'rgba(16, 185, 129, 0.28)' : 'rgba(255, 255, 255, 0.12)'}`,
          padding: '2px 8px',
          borderRadius: '12px',
        }}>
          {isReady ? 'All 8 Engines Synced' : isProcessing ? 'Pipeline Computing...' : 'Ready for Ingestion'}
        </span>
      </div>

      {/* Stepper Track */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(8, 1fr)',
        gap: '8px',
        position: 'relative',
      }}>
        {stages.map((stage, idx) => {
          const Icon = stage.icon;
          const stageDone = isReady;
          const stageRunning = isProcessing && idx === 3;

          return (
            <div
              key={stage.id}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
                padding: '8px 4px',
                background: stageDone ? 'rgba(16, 185, 129, 0.04)' : 'rgba(255, 255, 255, 0.02)',
                border: `1px solid ${stageDone ? 'rgba(16, 185, 129, 0.22)' : '#161D27'}`,
                borderRadius: '8px',
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{
                width: '26px',
                height: '26px',
                borderRadius: '50%',
                background: stageDone ? 'rgba(16, 185, 129, 0.15)' : 'rgba(255, 255, 255, 0.06)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '6px',
                color: stageDone ? '#10B981' : '#64748B',
              }}>
                {stageDone ? (
                  <Check size={13} strokeWidth={3} />
                ) : stageRunning ? (
                  <Loader2 size={13} className="animate-spin" color="#F59E0B" />
                ) : (
                  <Icon size={12} />
                )}
              </div>

              <span style={{ fontSize: '10.5px', fontWeight: 700, color: stageDone ? '#F1F5F9' : '#64748B', lineHeight: 1.2 }}>
                {stage.shortName}
              </span>
              <span style={{ fontSize: '9px', color: stageDone ? '#10B981' : '#475569', marginTop: '2px', fontWeight: 600 }}>
                {stageDone ? '✓ Live' : `0${idx + 1}`}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
