import React from 'react';
import { Activity, Sparkles, CheckCircle2, TrendingUp, AlertTriangle, ShieldCheck, Database, Layers } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useDataset } from '../../context/DatasetContext';
import { useQuery } from '@tanstack/react-query';
import { DecisionApi } from '../../api';
import { queryKeys } from '../../shared/api/queryKeys';
import { IntelligenceReportResponse } from '../../types';

export const ActivityFeed: React.FC = () => {
  const { activeDataset } = useDataset();

  const { data: reportData } = useQuery<IntelligenceReportResponse>({
    queryKey: queryKeys.reports.executive(activeDataset?.id || ''),
    queryFn: () => DecisionApi.getIntelligenceReport(activeDataset!.id),
    enabled: !!activeDataset?.id,
    staleTime: 60000,
  });

  const datasetName = activeDataset?.name || 'Active Dataset';
  const recordCount = activeDataset?.row_count ?? (activeDataset as any)?.record_count ?? 0;
  const findings = reportData?.findings || [];
  const recs = reportData?.recommendations || [];
  const metrics = reportData?.metrics || [];
  const healthScore = reportData?.executive_summary?.business_health_score;

  const activities = [
    {
      id: 'act-dataset',
      title: `Dataset "${datasetName}" ingested (${recordCount.toLocaleString()} rows verified)`,
      time: 'Live context',
      icon: <Database size={14} color="#38BDF8" />,
      route: '/data-management',
    },
    ...(findings.length > 0
      ? [
          {
            id: 'act-finding',
            title: `Diagnostic Engine: ${findings[0].title || 'Anomaly identified'}`,
            time: 'Diagnosed',
            icon: <AlertTriangle size={14} color="#F59E0B" />,
            route: '/diagnostics',
          },
        ]
      : []),
    ...(metrics.length > 0
      ? [
          {
            id: 'act-kpi',
            title: `KPI Calculation Engine: ${metrics.length} business metrics computed`,
            time: 'Evaluated',
            icon: <Activity size={14} color="#10B981" />,
            route: '/kpis',
          },
        ]
      : []),
    ...(recs.length > 0
      ? [
          {
            id: 'act-rec',
            title: `Prescriptive Action: ${recs[0].title || 'Strategic initiative formulated'}`,
            time: 'Ready',
            icon: <TrendingUp size={14} color="#A855F7" />,
            route: '/recommendations',
          },
        ]
      : []),
    ...(healthScore !== undefined
      ? [
          {
            id: 'act-gov',
            title: `Health Index: ${healthScore}/100 (${reportData?.executive_summary?.business_health_status || 'HEALTHY'})`,
            time: 'Verified',
            icon: <ShieldCheck size={14} color="#10B981" />,
            route: '/reports',
          },
        ]
      : []),
  ];

  return (
    <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: '0.88rem', fontWeight: 800, color: '#FFFFFF' }}>Platform Activity Feed</span>
        <span style={{ fontSize: '0.72rem', color: '#10B981', fontWeight: 700 }}>● {activeDataset?.name || 'LIVE CONTEXT'}</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {activities.map((item) => (
          <Link
            key={item.id}
            to={item.route}
            style={{
              padding: '10px 14px',
              background: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid #1E293B',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              textDecoration: 'none',
              transition: 'border-color 0.15s ease',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{ display: 'flex', alignItems: 'center' }}>{item.icon}</div>
              <span style={{ fontSize: '0.8rem', color: '#F1F5F9', fontWeight: 600 }}>{item.title}</span>
            </div>
            <span style={{ fontSize: '0.7rem', color: '#64748B' }}>{item.time}</span>
          </Link>
        ))}
      </div>
    </div>
  );
};
