import React from 'react';
import { Clock, Play, CheckCircle2, AlertTriangle, RotateCcw, Layers } from 'lucide-react';
import { Card, Badge, Button, MetricTile } from '../../design-system';

export const JobCenterView: React.FC = () => {
  const jobs = [
    {
      id: 'job-01',
      name: 'Dataset Ingestion & Feature Vectorization: Q1-2026',
      type: 'INGESTION',
      status: 'COMPLETED',
      duration: '42s',
      computeCost: '$0.04',
      completedAt: '12m ago',
    },
    {
      id: 'job-02',
      name: 'Digital Twin Macro Simulation (SIM-018 Benchmark Convergence)',
      type: 'SIMULATION',
      status: 'COMPLETED',
      duration: '1m 18s',
      computeCost: '$0.12',
      completedAt: '34m ago',
    },
    {
      id: 'job-03',
      name: 'Boardroom PDF & Markdown Presentation Generation (Q1)',
      type: 'REPORTING',
      status: 'COMPLETED',
      duration: '18s',
      computeCost: '$0.02',
      completedAt: '2h ago',
    },
    {
      id: 'job-04',
      name: 'Autonomous Playbook Execution (PBT-RETENTION-RECOVERY)',
      type: 'PLAYBOOK',
      status: 'COMPLETED',
      duration: '24s',
      computeCost: '$0.14',
      completedAt: '3h ago',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div>
        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#38BDF8', fontWeight: 800 }}>
          Asynchronous Compute & Task Processing
        </div>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
          Background Job Center & Worker Stream
        </h1>
      </div>

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <MetricTile label="TOTAL EXECUTED JOBS" value="1,420" sublabel="100% Success Rate (0 Failures)" valueColor="#10B981" />
        <MetricTile label="ACTIVE WORKER QUEUE" value="0 Pending" sublabel="Zero Backlog Latency" valueColor="#38BDF8" />
        <MetricTile label="AVG JOB EXECUTION TIME" value="28.4s" sublabel="Optimized Polars Ingestion" valueColor="#A855F7" />
        <MetricTile label="TOTAL COMPUTE SPEND" value="$8.42" sublabel="Average: $0.06 per Job" valueColor="#F59E0B" />
      </div>

      {/* Jobs Table */}
      <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Recent Background Job Executions</span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Telemetry Worker Queue</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {jobs.map((j) => (
            <div
              key={j.id}
              style={{
                background: 'rgba(15, 23, 42, 0.6)',
                border: '1px solid #1E293B',
                borderRadius: '10px',
                padding: '16px 20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '14px',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '0.94rem', fontWeight: 800, color: '#FFFFFF' }}>{j.name}</span>
                  <Badge variant="emerald" size="sm">
                    {j.status}
                  </Badge>
                </div>
                <div style={{ fontSize: '0.76rem', color: '#94A3B8', marginTop: '4px' }}>
                  Type: {j.type} • Duration: <strong style={{ color: '#FFFFFF' }}>{j.duration}</strong> • Cost: <strong style={{ color: '#10B981' }}>{j.computeCost}</strong>
                </div>
              </div>

              <span style={{ fontSize: '0.74rem', color: '#64748B' }}>{j.completedAt}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
