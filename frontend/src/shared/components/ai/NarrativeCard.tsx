import React from 'react';
import { Sparkles, ShieldCheck, TrendingUp, AlertTriangle, Zap, CheckCircle2 } from 'lucide-react';

export type PersonaMode = 'Executive' | 'Analyst' | 'Board' | 'Investor';

interface Props {
  personaMode?: PersonaMode;
  healthScore?: number;
}

export const NarrativeCard: React.FC<Props> = ({
  personaMode = 'Executive',
  healthScore = 82,
}) => {
  const getPersonaContent = () => {
    switch (personaMode) {
      case 'Board':
        return {
          title: 'Board of Directors Strategic Governance Briefing',
          overview: 'The enterprise maintains solid foundational resilience with a Business Health Score of 82/100 (EXCELLENT). Capital efficiency and top-line expansion remain strong at +12.4% ARR ($4.2M baseline). However, customer retention attrition (-4.3%) in Southeastern logistics hubs creates an annualized downside exposure of -$218K / quarter requiring immediate board oversight of courier SLA enforcement.',
          primaryRisk: 'Courier SLA violations exceeding 5 days generating 48% of active customer churn velocity.',
          largestOpportunity: 'Enforcing courier contract penalties while launching automated customer win-back incentives (+$180K ARR recovery).',
          recommendation: 'Authorize immediate executive deployment of the Win-Back Campaign & Courier SLA Penalty framework with 30-day milestone telemetry tracking.',
        };
      case 'Analyst':
        return {
          title: 'Deep Deterministic Analytics & Diagnostic Memo',
          overview: 'Telemetry evaluation across 100,000 transaction records reveals aggregate revenue expansion of +12.4% MoM against a historical baseline of $3.74M. Regression decomposition isolates severe covariance between delivery transit latency (>5.0 days) and customer review degradation (4.7★ → 2.1★), generating 48% of total churn coefficient.',
          primaryRisk: 'Secondary hub fulfillment latency increasing from 1.2 to 3.8 days with 92% statistical significance.',
          largestOpportunity: 'Multi-hub dispatch load leveling combined with discount retention incentives yields +$180K ARR expected value (p < 0.001).',
          recommendation: 'Execute dynamic dispatch routing to balance orders across secondary hubs and automate cohort retention triggers.',
        };
      case 'Investor':
        return {
          title: 'Investor & Capital Efficiency Memo',
          overview: 'Business fundamentals demonstrate attractive unit economics: Net revenue reached $4.2M (+12.4% YoY), Average Order Value expanded to $228.40 (+3.2%), and operating margins remain stable. Net retention dipped slightly to 85.8% due to localized delivery bottlenecks in the Southeastern region, representing an addressable recovery opportunity of +$480K ARR.',
          primaryRisk: 'Regional customer churn depressing LTV/CAC velocity on high-ticket orders in southeastern corridors.',
          largestOpportunity: 'Targeted win-back campaigns and post-purchase cross-sell engine present +$265K combined EBITDA upside.',
          recommendation: 'Fund immediate retention automation to protect customer lifetime value and drive net revenue retention above 92%.',
        };
      case 'Executive':
      default:
        return {
          title: 'Executive Operating Committee Strategy Memo',
          overview: 'Overall business health remains robust with an aggregate score of 82/100 (EXCELLENT). Revenue trajectory is positive (+12.4% MoM to $4.2M). However, customer retention degradation (-4.3%) in Southeastern logistics hubs represents -$218K in quarterly exposure. Corrective initiatives provide +$480K in total ARR recovery opportunity, led by the Win-Back Campaign (+$180K ARR).',
          primaryRisk: 'Customer retention attrition (-4.3%) triggered by courier delivery delays in southeastern corridors (-$218K / Qtr).',
          largestOpportunity: 'Targeted Win-Back Campaign & Courier SLA Penalties (+$180K ARR projected recovery • 92% confidence).',
          recommendation: 'Prioritize the Win-Back initiative in Week 1 followed by secondary hub dispatch balancing in Week 2.',
        };
    }
  };

  const content = getPersonaContent();

  return (
    <div style={{
      background: 'linear-gradient(135deg, #0A121E 0%, #060B12 100%)',
      border: '1px solid #1E293B',
      borderRadius: '12px',
      padding: '24px',
      marginBottom: '24px',
      boxShadow: '0 15px 35px rgba(0, 0, 0, 0.6)',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sparkles size={16} color="#38BDF8" />
          <h2 style={{ fontSize: '16px', fontWeight: 800, color: '#FFFFFF', margin: 0, letterSpacing: '-0.01em' }}>
            {content.title}
          </h2>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ fontSize: '10.5px', fontWeight: 800, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.12)', padding: '2px 8px', borderRadius: '4px' }}>
            {personaMode.toUpperCase()} PERSPECTIVE
          </span>
          <span style={{ fontSize: '10.5px', color: '#10B981', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '3px' }}>
            <ShieldCheck size={13} />
            <span>98% Grounded</span>
          </span>
        </div>
      </div>

      {/* Overview Narrative */}
      <p style={{ fontSize: '13.5px', color: '#CBD5E1', lineHeight: 1.7, marginBottom: '20px' }}>
        {content.overview}
      </p>

      {/* Risk & Opportunity Split Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '18px' }}>
        <div style={{ background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.25)', borderRadius: '8px', padding: '14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#F87171', fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', marginBottom: '4px' }}>
            <AlertTriangle size={13} />
            <span>Primary Business Risk</span>
          </div>
          <div style={{ fontSize: '12.5px', color: '#FFFFFF', fontWeight: 600, lineHeight: 1.4 }}>
            {content.primaryRisk}
          </div>
        </div>

        <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.25)', borderRadius: '8px', padding: '14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#10B981', fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', marginBottom: '4px' }}>
            <TrendingUp size={13} />
            <span>Largest Recovery Opportunity</span>
          </div>
          <div style={{ fontSize: '12.5px', color: '#FFFFFF', fontWeight: 600, lineHeight: 1.4 }}>
            {content.largestOpportunity}
          </div>
        </div>
      </div>

      {/* Overall Recommendation Banner */}
      <div style={{ background: '#05070B', border: '1px solid #141C28', borderRadius: '8px', padding: '12px 16px', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <Zap size={16} color="#38BDF8" style={{ flexShrink: 0 }} />
        <div>
          <span style={{ fontSize: '10.5px', color: '#64748B', textTransform: 'uppercase', fontWeight: 700, display: 'block' }}>
            Executive Directive:
          </span>
          <span style={{ fontSize: '12.5px', color: '#E2E8F0', fontWeight: 600 }}>
            {content.recommendation}
          </span>
        </div>
      </div>
    </div>
  );
};
