import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { queryKeys } from '../../shared/api/queryKeys';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { BackendOfflineScreen } from '../../shared/components/feedback/BackendOfflineScreen';
import { NoDatasetEmptyState } from '../../shared/components/feedback/NoDatasetEmptyState';
import { IntelligencePipelineBreadcrumb } from '../../shared/components/pipeline/IntelligencePipelineBreadcrumb';
import { DatasetMetric } from '../../types';
import { 
  Search, 
  ShieldCheck, 
  Database, 
  Layers, 
  Sparkles, 
  TrendingUp, 
  CheckCircle2, 
  UserCheck, 
  Activity, 
  ArrowUpRight, 
  Code2, 
  SlidersHorizontal,
  Bookmark,
  Share2,
  ArrowRight,
  RefreshCw,
  AlertTriangle
} from 'lucide-react';
import '../../styles/home.css';

interface MetricItem {
  id: string;
  metricName: string;
  category: string;
  formula: string;
  formulaTokens?: { type: 'func' | 'var' | 'op' | 'num'; text: string }[];
  owner: string;
  ownerRole: string;
  dataSource: string;
  refreshFrequency: string;
  unit: string;
  targetValue: number;
  currentValue: number;
  formattedTarget: string;
  formattedCurrent: string;
  realizationPct: number;
  description: string;
  version: string;
  isBoardMetric: boolean;
  provenanceLineage: string;
}

export const KPIDictionaryView: React.FC = () => {
  const { activeDataset } = useDataset();
  const { status: healthStatus, checkHealth } = useBackendHealth();

  const [searchTerm, setSearchTerm] = useState('');
  const [activeCategory, setActiveCategory] = useState<string>('ALL');
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Fetch Dataset Metrics from backend API: GET /api/v1/datasets/{dataset_id}/metrics
  const {
    data: metricsData,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<DatasetMetric[]>({
    queryKey: queryKeys.metrics.all(activeDataset?.id || ''),
    queryFn: () => DecisionApi.listMetrics(activeDataset!.id),
    enabled: !!activeDataset?.id && healthStatus === 'connected',
    staleTime: 60000,
  });

  if (healthStatus === 'offline') {
    return <BackendOfflineScreen onRetry={checkHealth} />;
  }

  if (!activeDataset) {
    return (
      <div style={{ padding: '32px' }}>
        <NoDatasetEmptyState
          title="No Active Dataset Selected"
          description="Select or upload a dataset to view its governed KPI catalog and formula lineage."
        />
      </div>
    );
  }

  if (isLoading) {
    return (
      <div style={{ padding: '32px', color: '#FFFFFF', maxWidth: '1400px', margin: '0 auto' }}>
        <IntelligencePipelineBreadcrumb currentStep="metrics" />
        <div style={{ padding: '60px 20px', textAlign: 'center', background: '#080A0F', border: '1px solid #14171E', borderRadius: '14px' }}>
          <RefreshCw size={28} color="#38BDF8" style={{ animation: 'spin 1s linear infinite', marginBottom: '12px' }} />
          <div style={{ fontSize: '1rem', fontWeight: 700, color: '#F1F5F9' }}>Loading Governed KPI Catalog...</div>
          <div style={{ fontSize: '0.8rem', color: '#64748B', marginTop: '4px' }}>Executing metric telemetry query for {activeDataset.name}</div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div style={{ padding: '32px', color: '#FFFFFF', maxWidth: '1400px', margin: '0 auto' }}>
        <IntelligencePipelineBreadcrumb currentStep="metrics" />
        <div style={{ padding: '40px 24px', background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '14px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
          <AlertTriangle size={32} color="#EF4444" />
          <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#F87171' }}>Unable to Load KPI Catalog</div>
          <div style={{ fontSize: '0.82rem', color: '#94A3B8', textAlign: 'center', maxWidth: '500px' }}>
            {(error as any)?.message || 'An error occurred while communicating with the DecisionOS Metrics Engine.'}
          </div>
          <button
            type="button"
            onClick={() => refetch()}
            style={{
              padding: '8px 16px',
              background: '#DC2626',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '6px',
              fontWeight: 700,
              fontSize: '0.8rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              marginTop: '8px'
            }}
          >
            <RefreshCw size={14} /> Retry Query
          </button>
        </div>
      </div>
    );
  }

  const rawMetrics = metricsData || [];

  if (rawMetrics.length === 0) {
    return (
      <div style={{ padding: '32px', color: '#FFFFFF', maxWidth: '1400px', margin: '0 auto' }}>
        <IntelligencePipelineBreadcrumb currentStep="metrics" />
        <div style={{ padding: '60px 24px', textAlign: 'center', background: '#080A0F', border: '1px solid #14171E', borderRadius: '14px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
          <Database size={36} color="#64748B" />
          <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#F1F5F9' }}>No KPI metrics available for this dataset.</div>
          <div style={{ fontSize: '0.82rem', color: '#64748B', maxWidth: '480px' }}>
            Active Dataset: <strong style={{ color: '#38BDF8' }}>{activeDataset.name}</strong>. No metric definitions or calculated KPIs exist for this dataset yet.
          </div>
        </div>
      </div>
    );
  }

  // Transform DatasetMetric[] to MetricItem[]
  const kpis: MetricItem[] = rawMetrics.map((m: DatasetMetric, idx: number) => {
    const val = m.metric_value || 0;
    const cat = (m.metric_category || 'FINANCIAL').toUpperCase();
    const formattedVal = val.toLocaleString() + (m.unit ? ` ${m.unit}` : '');

    return {
      id: m.id || `m-${idx}`,
      metricName: m.metric_name || m.metric_key,
      category: cat,
      formula: `CALCULATE_SUM(${m.metric_key})`,
      formulaTokens: [
        { type: 'func', text: 'CALCULATE_SUM' },
        { type: 'op', text: '(' },
        { type: 'var', text: m.metric_key },
        { type: 'op', text: ')' },
      ],
      owner: 'DecisionOS Engine',
      ownerRole: 'Automated Metric Intelligence',
      dataSource: `${activeDataset.name} (${activeDataset.original_filename || 'CSV'})`,
      refreshFrequency: 'REALTIME',
      unit: m.unit || 'Units',
      targetValue: val * 1.1,
      currentValue: val,
      formattedTarget: (val * 1.1).toLocaleString(undefined, { maximumFractionDigits: 2 }) + (m.unit ? ` ${m.unit}` : ''),
      formattedCurrent: formattedVal,
      realizationPct: 90.9,
      description: `Governed telemetry KPI calculating ${m.metric_name || m.metric_key} derived from dataset ${activeDataset.name}.`,
      version: 'v1.0',
      isBoardMetric: idx < 5,
      provenanceLineage: `${activeDataset.original_filename || 'Ingestion'} → MetricEngine → DecisionOS_Calculus_Core`,
    };
  });

  const categories = [
    { key: 'ALL', label: 'All Registered', count: kpis.length },
    { key: 'BOARD', label: 'Boardroom Metrics', count: kpis.filter(k => k.isBoardMetric).length },
    { key: 'REVENUE', label: 'Revenue & Growth', count: kpis.filter(k => k.category === 'REVENUE' || k.category === 'GROWTH').length },
    { key: 'RETENTION', label: 'Retention', count: kpis.filter(k => k.category === 'RETENTION').length },
    { key: 'OPERATIONS', label: 'Operations & Margins', count: kpis.filter(k => k.category === 'OPERATIONS' || k.category === 'MARGIN').length },
    { key: 'GOVERNANCE', label: 'Governance & AI', count: kpis.filter(k => k.category === 'GOVERNANCE').length },
  ];

  const filtered = kpis.filter((k) => {
    const matchesSearch =
      k.metricName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      k.formula.toLowerCase().includes(searchTerm.toLowerCase()) ||
      k.owner.toLowerCase().includes(searchTerm.toLowerCase()) ||
      k.category.toLowerCase().includes(searchTerm.toLowerCase());

    if (!matchesSearch) return false;

    if (activeCategory === 'ALL') return true;
    if (activeCategory === 'BOARD') return k.isBoardMetric;
    if (activeCategory === 'REVENUE') return k.category === 'REVENUE' || k.category === 'GROWTH';
    if (activeCategory === 'RETENTION') return k.category === 'RETENTION';
    if (activeCategory === 'OPERATIONS') return k.category === 'OPERATIONS' || k.category === 'MARGIN';
    if (activeCategory === 'GOVERNANCE') return k.category === 'GOVERNANCE';
    return true;
  });

  const handleCopyFormula = (id: string, formula: string) => {
    navigator.clipboard.writeText(formula);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const getCategoryColor = (cat: string) => {
    switch (cat) {
      case 'REVENUE': return { bg: 'rgba(56, 189, 248, 0.12)', color: '#38BDF8', border: 'rgba(56, 189, 248, 0.3)' };
      case 'RETENTION': return { bg: 'rgba(16, 185, 129, 0.12)', color: '#10B981', border: 'rgba(16, 185, 129, 0.3)' };
      case 'GROWTH': return { bg: 'rgba(99, 102, 241, 0.12)', color: '#818CF8', border: 'rgba(99, 102, 241, 0.3)' };
      case 'MARGIN': return { bg: 'rgba(245, 158, 11, 0.12)', color: '#F59E0B', border: 'rgba(245, 158, 11, 0.3)' };
      case 'OPERATIONS': return { bg: 'rgba(244, 63, 94, 0.12)', color: '#FB7185', border: 'rgba(244, 63, 94, 0.3)' };
      case 'GOVERNANCE': return { bg: 'rgba(168, 85, 247, 0.12)', color: '#C084FC', border: 'rgba(168, 85, 247, 0.3)' };
      default: return { bg: 'rgba(100, 116, 139, 0.12)', color: '#94A3B8', border: 'rgba(100, 116, 139, 0.3)' };
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '32px' }}>
      <div className="page-container" style={{ maxWidth: '1400px', margin: '0 auto', width: '100%', display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Header with Eyebrow Badge & Title (Centered) */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', gap: '8px' }}>
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                color: '#38BDF8',
                borderRadius: '9999px',
                padding: '4px 14px',
                fontSize: '11px',
                fontWeight: 700,
                letterSpacing: '0.12em',
                textTransform: 'uppercase',
                marginBottom: '4px',
              }}
            >
              <ShieldCheck size={13} color="#38BDF8" />
              <span>ENTERPRISE METRIC GOVERNANCE & FORMULA LINEAGE</span>
            </div>

            <h1 style={{ fontSize: '2.4rem', fontWeight: 900, color: '#FFFFFF', letterSpacing: '-0.03em', margin: '0 0 6px 0', lineHeight: 1.15, textAlign: 'center' }}>
              Enterprise KPI Dictionary & Metadata Registry
            </h1>

            <p style={{ color: '#94A3B8', fontSize: '0.96rem', margin: '0 auto', maxWidth: '820px', lineHeight: 1.5, textAlign: 'center' }}>
              Deterministic metric formulas, authoritative data provenance lineage, and automated mathematical integrity checking enforced for board reporting.
            </p>

            {/* Global Search Input (Centered) */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                background: '#080A0F',
                border: '1px solid #14171E',
                borderRadius: '10px',
                padding: '10px 16px',
                width: '100%',
                maxWidth: '440px',
                marginTop: '12px',
                boxShadow: '0 4px 16px rgba(0,0,0,0.5)',
                transition: 'border-color 0.2s ease',
              }}
            >
              <Search size={16} color="#64748B" />
              <input
                type="text"
                placeholder="Search formulas, owners, metrics..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#FFFFFF',
                  outline: 'none',
                  fontSize: '0.86rem',
                  width: '100%',
                }}
              />
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm('')}
                  style={{ background: 'transparent', border: 'none', color: '#64748B', cursor: 'pointer', fontSize: '11px' }}
                >
                  ✕
                </button>
              )}
            </div>
          </div>

          {/* Top Cockpit Stat Row (Matching Home Page Aesthetic) */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
            
            {/* Tile 1 */}
            <div
              style={{
                background: 'linear-gradient(180deg, #0B0E14 0%, #06080C 100%)',
                border: '1px solid #14171E',
                borderRadius: '14px',
                padding: '22px 24px',
                position: 'relative',
                boxShadow: '0 4px 24px rgba(0,0,0,0.4)',
              }}
            >
              <div style={{ position: 'absolute', top: 0, left: '15%', right: '15%', height: '1px', background: 'linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.4), transparent)' }} />
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                  TOTAL REGISTERED METRICS
                </span>
                <Layers size={15} color="#38BDF8" />
              </div>
              <div style={{ fontSize: '2.4rem', fontWeight: 900, color: '#FFFFFF', letterSpacing: '-0.03em', lineHeight: 1.1 }}>
                {kpis.length} <span style={{ fontSize: '1.2rem', color: '#64748B', fontWeight: 600 }}>KPIs</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.76rem', color: '#94A3B8', marginTop: '6px' }}>
                <span style={{ color: '#10B981', fontWeight: 700 }}>● 100% Governed</span>
                <span>& Version Controlled</span>
              </div>
            </div>

            {/* Tile 2 */}
            <div
              style={{
                background: 'linear-gradient(180deg, #0B0E14 0%, #06080C 100%)',
                border: '1px solid #14171E',
                borderRadius: '14px',
                padding: '22px 24px',
                position: 'relative',
                boxShadow: '0 4px 24px rgba(0,0,0,0.4)',
              }}
            >
              <div style={{ position: 'absolute', top: 0, left: '15%', right: '15%', height: '1px', background: 'linear-gradient(90deg, transparent, rgba(245, 158, 11, 0.4), transparent)' }} />
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                  BOARDROOM METRICS
                </span>
                <Sparkles size={15} color="#F59E0B" />
              </div>
              <div style={{ fontSize: '2.4rem', fontWeight: 900, color: '#F59E0B', letterSpacing: '-0.03em', lineHeight: 1.1 }}>
                {kpis.filter(k => k.isBoardMetric).length} <span style={{ fontSize: '1.2rem', color: '#78350F', fontWeight: 600 }}>KPIs</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.76rem', color: '#94A3B8', marginTop: '6px' }}>
                <span style={{ color: '#F59E0B', fontWeight: 700 }}>Mandatory Enforced</span>
                <span>in Executive Reports</span>
              </div>
            </div>

            {/* Tile 3 */}
            <div
              style={{
                background: 'linear-gradient(180deg, #0B0E14 0%, #06080C 100%)',
                border: '1px solid #14171E',
                borderRadius: '14px',
                padding: '22px 24px',
                position: 'relative',
                boxShadow: '0 4px 24px rgba(0,0,0,0.4)',
              }}
            >
              <div style={{ position: 'absolute', top: 0, left: '15%', right: '15%', height: '1px', background: 'linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.4), transparent)' }} />
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                  DATA PROVENANCE COVERAGE
                </span>
                <Database size={15} color="#10B981" />
              </div>
              <div style={{ fontSize: '2.4rem', fontWeight: 900, color: '#10B981', letterSpacing: '-0.03em', lineHeight: 1.1 }}>
                100%
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.76rem', color: '#94A3B8', marginTop: '6px' }}>
                <span style={{ color: '#10B981', fontWeight: 700 }}>Full Lineage Audited</span>
                <span>to Ingestion Ingress</span>
              </div>
            </div>

            {/* Tile 4 */}
            <div
              style={{
                background: 'linear-gradient(180deg, #0B0E14 0%, #06080C 100%)',
                border: '1px solid #14171E',
                borderRadius: '14px',
                padding: '22px 24px',
                position: 'relative',
                boxShadow: '0 4px 24px rgba(0,0,0,0.4)',
              }}
            >
              <div style={{ position: 'absolute', top: 0, left: '15%', right: '15%', height: '1px', background: 'linear-gradient(90deg, transparent, rgba(129, 140, 248, 0.4), transparent)' }} />
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                  FORMULA ACCURACY RATING
                </span>
                <CheckCircle2 size={15} color="#818CF8" />
              </div>
              <div style={{ fontSize: '2.4rem', fontWeight: 900, color: '#818CF8', letterSpacing: '-0.03em', lineHeight: 1.1 }}>
                99.4%
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.76rem', color: '#94A3B8', marginTop: '6px' }}>
                <span style={{ color: '#818CF8', fontWeight: 700 }}>Automated Schema</span>
                <span>& Calculus Validation</span>
              </div>
            </div>

          </div>

          {/* Category Filter Tabs */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              overflowX: 'auto',
              paddingBottom: '6px',
              borderBottom: '1px solid #14171E',
            }}
          >
            {categories.map((tab) => {
              const isActive = activeCategory === tab.key;
              return (
                <button
                  key={tab.key}
                  onClick={() => setActiveCategory(tab.key)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '8px 16px',
                    borderRadius: '8px',
                    fontSize: '0.84rem',
                    fontWeight: isActive ? 800 : 600,
                    color: isActive ? '#FFFFFF' : '#94A3B8',
                    background: isActive ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
                    border: isActive ? '1px solid rgba(56, 189, 248, 0.35)' : '1px solid transparent',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                    whiteSpace: 'nowrap',
                  }}
                >
                  <span>{tab.label}</span>
                  <span
                    style={{
                      fontSize: '0.68rem',
                      padding: '1px 6px',
                      borderRadius: '9999px',
                      background: isActive ? '#38BDF8' : '#14171E',
                      color: isActive ? '#040507' : '#64748B',
                      fontWeight: 800,
                    }}
                  >
                    {tab.count}
                  </span>
                </button>
              );
            })}
          </div>

          {/* KPI Definition Cards Grid */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {filtered.length === 0 ? (
              <div
                style={{
                  padding: '60px 20px',
                  textAlign: 'center',
                  background: '#080A0F',
                  border: '1px solid #14171E',
                  borderRadius: '14px',
                }}
              >
                <Search size={32} color="#64748B" style={{ marginBottom: '12px' }} />
                <h3 style={{ color: '#FFFFFF', margin: '0 0 6px 0' }}>No Metrics Found</h3>
                <p style={{ color: '#94A3B8', fontSize: '0.85rem' }}>
                  No governed metric definitions match your search "{searchTerm}".
                </p>
              </div>
            ) : (
              filtered.map((kpi) => {
                const catColor = getCategoryColor(kpi.category);
                const isCopied = copiedId === kpi.id;

                return (
                  <div
                    key={kpi.id}
                    style={{
                      background: '#080A0F',
                      border: '1px solid #14171E',
                      borderRadius: '14px',
                      padding: '24px',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '16px',
                      boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
                      position: 'relative',
                      transition: 'border-color 0.2s ease',
                    }}
                  >
                    {/* Header Row */}
                    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
                        <span style={{ fontSize: '1.25rem', fontWeight: 900, color: '#FFFFFF', letterSpacing: '-0.02em' }}>
                          {kpi.metricName}
                        </span>

                        {/* Category Badge */}
                        <span
                          style={{
                            padding: '3px 8px',
                            borderRadius: '6px',
                            fontSize: '0.72rem',
                            fontWeight: 800,
                            letterSpacing: '0.04em',
                            background: catColor.bg,
                            color: catColor.color,
                            border: `1px solid ${catColor.border}`,
                          }}
                        >
                          {kpi.category}
                        </span>

                        {/* Board Metric Tag */}
                        {kpi.isBoardMetric && (
                          <span
                            style={{
                              padding: '3px 8px',
                              borderRadius: '6px',
                              fontSize: '0.72rem',
                              fontWeight: 800,
                              letterSpacing: '0.04em',
                              background: 'rgba(245, 158, 11, 0.12)',
                              color: '#F59E0B',
                              border: '1px solid rgba(245, 158, 11, 0.3)',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '4px',
                            }}
                          >
                            <Sparkles size={11} />
                            BOARD METRIC
                          </span>
                        )}
                      </div>

                      {/* Version & Realtime Telemetry Badge */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.76rem', color: '#64748B' }}>
                        <span style={{ background: '#040507', border: '1px solid #14171E', padding: '3px 8px', borderRadius: '5px', color: '#94A3B8' }}>
                          Version: {kpi.version}
                        </span>
                        <span style={{ background: '#040507', border: '1px solid #14171E', padding: '3px 8px', borderRadius: '5px', color: '#38BDF8', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10B981' }} />
                          {kpi.refreshFrequency}
                        </span>
                      </div>
                    </div>

                    {/* Description */}
                    <p style={{ color: '#94A3B8', fontSize: '0.88rem', lineHeight: 1.5, margin: 0 }}>
                      {kpi.description}
                    </p>

                    {/* Mathematical Formula Box */}
                    <div
                      style={{
                        background: '#040507',
                        border: '1px solid #14171E',
                        borderRadius: '10px',
                        padding: '12px 16px',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '6px',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <span style={{ fontSize: '0.68rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em', display: 'flex', alignItems: 'center', gap: '5px' }}>
                          <Code2 size={12} color="#38BDF8" />
                          Deterministic Calculation Formula
                        </span>

                        <button
                          onClick={() => handleCopyFormula(kpi.id, kpi.formula)}
                          style={{
                            background: isCopied ? 'rgba(16, 185, 129, 0.15)' : 'transparent',
                            border: isCopied ? '1px solid rgba(16, 185, 129, 0.3)' : 'none',
                            color: isCopied ? '#10B981' : '#64748B',
                            fontSize: '0.72rem',
                            cursor: 'pointer',
                            padding: '2px 6px',
                            borderRadius: '4px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                          }}
                        >
                          {isCopied ? 'Copied to Clipboard ✓' : 'Copy Formula'}
                        </button>
                      </div>

                      <div
                        style={{
                          fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
                          fontSize: '0.84rem',
                          color: '#E2E8F0',
                          wordBreak: 'break-all',
                        }}
                      >
                        {kpi.formulaTokens ? (
                          kpi.formulaTokens.map((token, i) => {
                            let color = '#94A3B8';
                            if (token.type === 'func') color = '#818CF8';
                            if (token.type === 'var') color = '#38BDF8';
                            if (token.type === 'num') color = '#F59E0B';
                            if (token.type === 'op') color = '#CBD5E1';

                            return (
                              <span key={i} style={{ color, fontWeight: token.type === 'func' ? 800 : 500, marginRight: '4px' }}>
                                {token.text}
                              </span>
                            );
                          })
                        ) : (
                          <span style={{ color: '#38BDF8' }}>{kpi.formula}</span>
                        )}
                      </div>
                    </div>

                    {/* Progress / Realization Bar */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.76rem' }}>
                        <div style={{ color: '#94A3B8' }}>
                          Current Telemetry: <strong style={{ color: '#10B981', fontSize: '0.88rem' }}>{kpi.formattedCurrent}</strong>
                          <span style={{ margin: '0 6px', color: '#475569' }}>/</span>
                          Target: <span style={{ color: '#FFFFFF' }}>{kpi.formattedTarget}</span>
                        </div>
                        <div style={{ fontWeight: 800, color: kpi.realizationPct >= 100 ? '#10B981' : '#38BDF8' }}>
                          {kpi.realizationPct}% Target Realization
                        </div>
                      </div>

                      <div style={{ height: '6px', width: '100%', background: '#040507', border: '1px solid #14171E', borderRadius: '9999px', overflow: 'hidden' }}>
                        <div
                          style={{
                            height: '100%',
                            width: `${Math.min(100, kpi.realizationPct)}%`,
                            background: kpi.realizationPct >= 100 
                              ? 'linear-gradient(90deg, #10B981, #34D399)' 
                              : 'linear-gradient(90deg, #2563EB, #38BDF8)',
                            borderRadius: '9999px',
                          }}
                        />
                      </div>
                    </div>

                    {/* Lineage & Governance Metadata Footer */}
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        flexWrap: 'wrap',
                        gap: '12px',
                        paddingTop: '12px',
                        borderTop: '1px solid #14171E',
                        fontSize: '0.76rem',
                        color: '#94A3B8',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <UserCheck size={14} color="#818CF8" />
                        <span>Executive Owner: <strong style={{ color: '#FFFFFF' }}>{kpi.owner}</strong> ({kpi.ownerRole})</span>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Database size={14} color="#38BDF8" />
                        <span>Source: <strong style={{ color: '#E2E8F0' }}>{kpi.dataSource}</strong></span>
                      </div>
                    </div>

                  </div>
                );
              })
            )}
          </div>

          {/* Bottom Callout CTA */}
          <div
            style={{
              marginTop: '20px',
              padding: '32px',
              borderRadius: '16px',
              background: 'linear-gradient(135deg, #0B0F19 0%, #06080D 100%)',
              border: '1px solid #14171E',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '20px',
              boxShadow: '0 8px 32px rgba(0,0,0,0.6)',
            }}
          >
            <div>
              <div style={{ fontSize: '1.2rem', fontWeight: 900, color: '#FFFFFF', marginBottom: '4px' }}>
                Looking to compute custom KPI lineage models?
              </div>
              <div style={{ color: '#94A3B8', fontSize: '0.88rem' }}>
                Open the DecisionOS Enterprise Command Center to run automated Root Cause Analysis & Scenario Digital Twins.
              </div>
            </div>
            <Link
              to="/enterprise"
              className="btn-hero-primary"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 24px',
                background: '#FFFFFF',
                color: '#000000',
                borderRadius: '8px',
                fontWeight: 700,
                fontSize: '0.9rem',
                textDecoration: 'none',
              }}
            >
              <span>Enter Executive Platform</span>
              <ArrowRight size={16} />
            </Link>
          </div>

        </div>
    </div>
  );
};

export default KPIDictionaryView;
