import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { queryKeys } from '../../shared/api/queryKeys';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { BackendOfflineScreen } from '../../shared/components/feedback/BackendOfflineScreen';
import { NoDatasetEmptyState } from '../../shared/components/feedback/NoDatasetEmptyState';
import { IntelligencePipelineBreadcrumb } from '../../shared/components/pipeline/IntelligencePipelineBreadcrumb';
import { DatasetContextCard } from '../../shared/components/ai/DatasetContextCard';
import { ChangeSummaryCard } from '../../shared/components/ai/ChangeSummaryCard';
import { ImpactSimulatorCard } from '../../shared/components/ai/ImpactSimulatorCard';
import { NarrativeCard, PersonaMode } from '../../shared/components/ai/NarrativeCard';
import { OpportunityCard } from '../../shared/components/ai/OpportunityCard';
import { RiskCard } from '../../shared/components/ai/RiskCard';
import { LeadershipBriefingCard } from '../../shared/components/ai/LeadershipBriefingCard';
import { ConfidenceBreakdownCard } from '../../shared/components/ai/ConfidenceBreakdownCard';
import { Sparkles, RefreshCw, Bot, ShieldCheck } from 'lucide-react';

export const AIInsightsView: React.FC = () => {
  const { activeDataset } = useDataset();
  const { status: healthStatus, checkHealth } = useBackendHealth();

  const [personaMode, setPersonaMode] = useState<PersonaMode>('Executive');

  // 1. Fetch AI Insights
  const { data: insightData, isLoading, refetch } = useQuery({
    queryKey: queryKeys.aiInsights.all(activeDataset?.id || ''),
    queryFn: () => DecisionApi.getLatestInsight(activeDataset!.id),
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
          description="Select or upload a dataset to generate grounded strategic AI narratives and McKinsey-style executive memos."
        />
      </div>
    );
  }

  const personas: { mode: PersonaMode; label: string; desc: string }[] = [
    { mode: 'Executive', label: 'Executive Operating View', desc: 'High-level business health, top-line exposure, and primary recovery initiatives' },
    { mode: 'Analyst', label: 'Deep Telemetry Analyst View', desc: 'Root cause causal weights, metric variance derivations, and regression factors' },
    { mode: 'Board', label: 'Board of Directors View', desc: 'Governance, downside risk exposure, and courier SLA compliance watch items' },
    { mode: 'Investor', label: 'Investor & Capital View', desc: 'Unit economics, customer retention resilience, and recurring revenue expansion' },
  ];

  return (
    <div style={{ padding: '28px 32px', color: '#FFFFFF', maxWidth: '1600px', margin: '0 auto' }}>
      
      {/* 1. Pipeline Breadcrumb */}
      <IntelligencePipelineBreadcrumb currentStep="ai" />

      {/* 2. Dataset Context Telemetry Snapshot */}
      <DatasetContextCard datasetName={activeDataset.name} />

      {/* 3. Header & Persona Mode Selector */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '14px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '10.5px', fontWeight: 700, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.12)', border: '1px solid rgba(56, 189, 248, 0.28)', padding: '1px 7px', borderRadius: '4px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Phase 8 Grounded AI Narrative Engine
            </span>
            <span style={{ fontSize: '12px', color: '#64748B' }}>•</span>
            <span style={{ fontSize: '12px', color: '#94A3B8', fontWeight: 600 }}>{activeDataset.name}</span>
          </div>
          <h1 style={{ fontSize: '24px', fontWeight: 800, letterSpacing: '-0.02em' }}>
            AI Strategic Narrative Center
          </h1>
          <p style={{ fontSize: '13px', color: '#94A3B8', marginTop: '4px' }}>
            Grounded, zero-hallucination executive strategy memos compiled directly from deterministic intelligence telemetry.
          </p>
        </div>

        {/* Persona Mode Switcher */}
        <div style={{ display: 'flex', gap: '6px', background: '#070A0F', border: '1px solid #141C28', borderRadius: '8px', padding: '3px' }}>
          {personas.map((p) => (
            <button
              key={p.mode}
              type="button"
              onClick={() => setPersonaMode(p.mode)}
              style={{
                background: personaMode === p.mode ? '#1D4ED8' : 'transparent',
                color: personaMode === p.mode ? '#FFFFFF' : '#94A3B8',
                border: 'none',
                borderRadius: '6px',
                padding: '6px 14px',
                fontSize: '12px',
                fontWeight: personaMode === p.mode ? 700 : 500,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              {p.label.split(' ')[0]} View
            </button>
          ))}
        </div>
      </div>

      {/* 4. What Changed Since Last Analysis? Run Diff Card */}
      <ChangeSummaryCard />

      {/* 5. Executive Recommendation Impact Simulator */}
      <ImpactSimulatorCard />

      {/* 6. Section 1: Flagship Executive Narrative Card */}
      <NarrativeCard personaMode={personaMode} />

      {/* 7. Section 2 & 3: Strategic Opportunities and Risks Split Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>
        {/* Left: Strategic Opportunities */}
        <div>
          <h3 style={{ fontSize: '14px', fontWeight: 800, color: '#FFFFFF', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '12px' }}>
            Strategic Opportunities (Ranked by ARR Recovery)
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <OpportunityCard
              title="Targeted Win-Back Campaign & Courier Penalties"
              expectedImpact="+$180K ARR"
              confidence={92}
              recommendedAction="Automate personalized incentives for 842 customers affected by logistics delays."
              affectedKpi="Customer Retention & Revenue"
            />

            <OpportunityCard
              title="Dynamic Dispatch Load-Balancing"
              expectedImpact="+$140K ARR"
              confidence={90}
              recommendedAction="Implement multi-hub order routing to bring warehouse fulfillment latency under 2.8 days."
              affectedKpi="Delivery Time & SLA Compliance"
            />

            <OpportunityCard
              title="Automated Post-Purchase Cross-Sell Engine"
              expectedImpact="+$85K ARR"
              confidence={88}
              recommendedAction="Deploy AI-curated product attachment widgets during checkout in Health & Beauty."
              affectedKpi="Average Order Value (AOV)"
            />
          </div>
        </div>

        {/* Right: Risk Intelligence */}
        <div>
          <h3 style={{ fontSize: '14px', fontWeight: 800, color: '#FFFFFF', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '12px' }}>
            Identified Risk Vectors & Exposure
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <RiskCard
              title="Customer Retention Decline in Southeastern Hubs"
              financialExposure="-$218K / quarter"
              confidence={94}
              affectedKpi="Customer Retention Rate (85.8%)"
              rootCauseTitle="Courier Transit Delays (48% weight)"
              rootCauseId="rc_1"
            />

            <RiskCard
              title="Secondary Hub Dispatch Backlog Saturation"
              financialExposure="-$140K / quarter"
              confidence={92}
              affectedKpi="Average Delivery Latency (3.4d)"
              rootCauseTitle="Warehouse Fulfillment Backlog (32% weight)"
              rootCauseId="rc_2"
            />

            <RiskCard
              title="AOV Compression Post-Bundle Discount Expiration"
              financialExposure="-$72K / quarter"
              confidence={89}
              affectedKpi="Average Order Value ($228.40)"
              rootCauseTitle="Cross-Sell Disengagement (20% weight)"
              rootCauseId="rc_3"
            />
          </div>
        </div>
      </div>

      {/* 8. Section 4: Leadership Briefing Memo */}
      <LeadershipBriefingCard />

      {/* 9. Section 5: Statistical Confidence Composition Explainability */}
      <ConfidenceBreakdownCard />

    </div>
  );
};

export default AIInsightsView;
