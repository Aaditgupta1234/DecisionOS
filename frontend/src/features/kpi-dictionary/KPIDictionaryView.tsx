import React, { useState } from 'react';
import { Link } from 'react-router-dom';
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
  ArrowRight
} from 'lucide-react';
import { MarketingNavbar } from '../../components/layout/MarketingNavbar';
import '../../styles/home.css';

interface MetricItem {
  id: string;
  metricName: string;
  category: 'REVENUE' | 'RETENTION' | 'GROWTH' | 'OPERATIONS' | 'GOVERNANCE' | 'MARGIN';
  formula: string;
  formulaTokens?: { type: 'func' | 'var' | 'op' | 'num'; text: string }[];
  owner: string;
  ownerRole: string;
  dataSource: string;
  refreshFrequency: 'REALTIME' | 'HOURLY' | 'DAILY' | 'STREAMING';
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
  const [searchTerm, setSearchTerm] = useState('');
  const [activeCategory, setActiveCategory] = useState<string>('ALL');
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const kpis: MetricItem[] = [
    {
      id: 'kpi-01',
      metricName: 'Annual Recurring Revenue (ARR)',
      category: 'REVENUE',
      formula: 'SUM(Active Subscription Contracts * 12) + Net Expansion Revenue',
      formulaTokens: [
        { type: 'func', text: 'SUM' },
        { type: 'op', text: '(' },
        { type: 'var', text: 'Active_Subscription_Contracts' },
        { type: 'op', text: '*' },
        { type: 'num', text: '12' },
        { type: 'op', text: ')' },
        { type: 'op', text: '+' },
        { type: 'var', text: 'Net_Expansion_Revenue' },
      ],
      owner: 'Sarah Jenkins',
      ownerRole: 'VP Strategic Finance (CFO)',
      dataSource: 'Stripe Billing API & Salesforce CRM Telemetry',
      refreshFrequency: 'REALTIME',
      unit: '$ USD',
      targetValue: 14000000,
      currentValue: 12400000,
      formattedTarget: '$14.0M',
      formattedCurrent: '$12.4M',
      realizationPct: 88.6,
      description: 'Normalized annual run-rate of recurring contracted software subscription revenue across all active enterprise cohorts.',
      version: 'v2.4',
      isBoardMetric: true,
      provenanceLineage: 'Stripe_Events → Kafka_Ingest → Snowflake_DWH → DecisionOS_Lineage_Engine',
    },
    {
      id: 'kpi-02',
      metricName: 'Net Revenue Retention (NRR)',
      category: 'RETENTION',
      formula: '((Starting ARR + Expansions - Contractions - Churn) / Starting ARR) * 100',
      formulaTokens: [
        { type: 'op', text: '((' },
        { type: 'var', text: 'Starting_ARR' },
        { type: 'op', text: '+' },
        { type: 'var', text: 'Expansions' },
        { type: 'op', text: '-' },
        { type: 'var', text: 'Contractions' },
        { type: 'op', text: '-' },
        { type: 'var', text: 'Churn' },
        { type: 'op', text: ')' },
        { type: 'op', text: '/' },
        { type: 'var', text: 'Starting_ARR' },
        { type: 'op', text: ')' },
        { type: 'op', text: '*' },
        { type: 'num', text: '100' },
      ],
      owner: 'Marcus Vance',
      ownerRole: 'Chief Customer Officer (CCO)',
      dataSource: 'ERP Subscription Ledger & Customer Health Graph',
      refreshFrequency: 'DAILY',
      unit: '%',
      targetValue: 115.0,
      currentValue: 118.4,
      formattedTarget: '115.0%',
      formattedCurrent: '118.4%',
      realizationPct: 102.9,
      description: 'Percentage of recurring revenue retained from existing customers over a trailing 12-month window including upsells and renewals.',
      version: 'v3.0',
      isBoardMetric: true,
      provenanceLineage: 'Salesforce_Contracts → NetSuite_GL → DecisionOS_Calculus_Core',
    },
    {
      id: 'kpi-03',
      metricName: 'Customer Retention Rate',
      category: 'RETENTION',
      formula: '((Active Customers End - Acquired Customers) / Active Customers Start) * 100',
      formulaTokens: [
        { type: 'op', text: '((' },
        { type: 'var', text: 'Active_Customers_End' },
        { type: 'op', text: '-' },
        { type: 'var', text: 'Acquired_Customers' },
        { type: 'op', text: ')' },
        { type: 'op', text: '/' },
        { type: 'var', text: 'Active_Customers_Start' },
        { type: 'op', text: ')' },
        { type: 'op', text: '*' },
        { type: 'num', text: '100' },
      ],
      owner: 'Elena Rostova',
      ownerRole: 'Head of Customer Success',
      dataSource: 'Telemetry Event Stream & Data Warehouse',
      refreshFrequency: 'DAILY',
      unit: '%',
      targetValue: 91.0,
      currentValue: 84.2,
      formattedTarget: '91.0%',
      formattedCurrent: '84.2%',
      realizationPct: 92.5,
      description: 'Trailing 90-day active customer account retention across all tiered enterprise distribution corridors.',
      version: 'v3.1',
      isBoardMetric: true,
      provenanceLineage: 'Segment_Telemetry → BigQuery_Raw → DecisionOS_Retention_Model',
    },
    {
      id: 'kpi-04',
      metricName: 'Customer Acquisition Cost (CAC)',
      category: 'GROWTH',
      formula: '(Total Sales & Marketing Spend) / (Total New Customers Acquired)',
      formulaTokens: [
        { type: 'op', text: '(' },
        { type: 'var', text: 'Total_Sales_Marketing_Spend' },
        { type: 'op', text: ')' },
        { type: 'op', text: '/' },
        { type: 'op', text: '(' },
        { type: 'var', text: 'Total_New_Customers_Acquired' },
        { type: 'op', text: ')' },
      ],
      owner: 'David Chen',
      ownerRole: 'Chief Marketing Officer (CMO)',
      dataSource: 'Google Ads, Meta Ads, Hubspot & LinkedIn Marketing API',
      refreshFrequency: 'DAILY',
      unit: '$ USD',
      targetValue: 4200,
      currentValue: 3850,
      formattedTarget: '$4,200',
      formattedCurrent: '$3,850',
      realizationPct: 109.1,
      description: 'Fully-loaded expenditure required to convert an enterprise account, factoring in ad spend, BDR commissions, and onboarding overhead.',
      version: 'v2.1',
      isBoardMetric: true,
      provenanceLineage: 'Ad_Networks → Hubspot_Attribution → DecisionOS_CAC_Engine',
    },
    {
      id: 'kpi-05',
      metricName: 'Gross Margin Efficiency',
      category: 'MARGIN',
      formula: '((Total GAAP Revenue - Total Cost of Goods Sold) / Total GAAP Revenue) * 100',
      formulaTokens: [
        { type: 'op', text: '((' },
        { type: 'var', text: 'Total_GAAP_Revenue' },
        { type: 'op', text: '-' },
        { type: 'var', text: 'Total_COGS' },
        { type: 'op', text: ')' },
        { type: 'op', text: '/' },
        { type: 'var', text: 'Total_GAAP_Revenue' },
        { type: 'op', text: ')' },
        { type: 'op', text: '*' },
        { type: 'num', text: '100' },
      ],
      owner: 'Alexander Wright',
      ownerRole: 'VP Financial Planning & Analysis',
      dataSource: 'NetSuite General Ledger & AWS Cost Explorer API',
      refreshFrequency: 'DAILY',
      unit: '%',
      targetValue: 78.0,
      currentValue: 81.4,
      formattedTarget: '78.0%',
      formattedCurrent: '81.4%',
      realizationPct: 104.3,
      description: 'Direct profitability threshold after cloud compute infrastructure, carrier transport fees, and direct fulfillment labor costs.',
      version: 'v4.0',
      isBoardMetric: true,
      provenanceLineage: 'AWS_Billing_Curated → NetSuite_COGS → DecisionOS_Margin_Matrix',
    },
    {
      id: 'kpi-06',
      metricName: 'Courier Delivery Latency',
      category: 'OPERATIONS',
      formula: 'AVG(Delivery Timestamp - Ingestion Timestamp) in Business Days',
      formulaTokens: [
        { type: 'func', text: 'AVG' },
        { type: 'op', text: '(' },
        { type: 'var', text: 'Delivery_Timestamp' },
        { type: 'op', text: '-' },
        { type: 'var', text: 'Ingestion_Timestamp' },
        { type: 'op', text: ')' },
        { type: 'var', text: '[Business_Days]' },
      ],
      owner: 'Rajesh Patel',
      ownerRole: 'VP Global Logistics Operations',
      dataSource: 'Regional Carrier Telemetry Hub (FedEx, UPS, DHL APIs)',
      refreshFrequency: 'HOURLY',
      unit: 'Days',
      targetValue: 3.0,
      currentValue: 3.4,
      formattedTarget: '3.0 Days',
      formattedCurrent: '3.4 Days',
      realizationPct: 88.2,
      description: 'End-to-end parcel routing transit latency from automated fulfillment dispatch to verified customer drop-off scan.',
      version: 'v1.8',
      isBoardMetric: false,
      provenanceLineage: 'Carrier_EDI_Streams → Logistics_Kafka → DecisionOS_Transit_Engine',
    },
    {
      id: 'kpi-07',
      metricName: 'Automated Decision Precision',
      category: 'GOVERNANCE',
      formula: '(Accurate Automated Actions / Total Prescribed Interventions) * 100',
      formulaTokens: [
        { type: 'op', text: '(' },
        { type: 'var', text: 'Accurate_Automated_Actions' },
        { type: 'op', text: '/' },
        { type: 'var', text: 'Total_Prescribed_Interventions' },
        { type: 'op', text: ')' },
        { type: 'op', text: '*' },
        { type: 'num', text: '100' },
      ],
      owner: 'Dr. Evelyn Reed',
      ownerRole: 'Chief AI Ethics & Governance Officer',
      dataSource: 'DecisionOS Continuous Feedback & Audit Log Ledger',
      refreshFrequency: 'STREAMING',
      unit: '%',
      targetValue: 99.0,
      currentValue: 99.4,
      formattedTarget: '99.0%',
      formattedCurrent: '99.4%',
      realizationPct: 100.4,
      description: 'Empirical decision accuracy validated by post-execution outcome telemetry and deterministic audit verification gates.',
      version: 'v5.2',
      isBoardMetric: true,
      provenanceLineage: 'Audit_Vault → Governance_Policy_Engine → DecisionOS_Trust_Registry',
    },
  ];

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
                32 <span style={{ fontSize: '1.2rem', color: '#64748B', fontWeight: 600 }}>KPIs</span>
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
                12 <span style={{ fontSize: '1.2rem', color: '#78350F', fontWeight: 600 }}>KPIs</span>
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
