import React, { useState } from 'react';
import { X, ChevronLeft, ChevronRight, Presentation, ShieldCheck, Download, Sparkles, Cpu, Target, FileText } from 'lucide-react';

export interface PresentationDeckViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  reportTitle?: string;
}

export const PresentationDeckViewerModal: React.FC<PresentationDeckViewerModalProps> = ({
  isOpen,
  onClose,
  reportTitle = 'DecisionOS Q4 Comprehensive Boardroom Governance Report',
}) => {
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);

  const slides = [
    {
      number: 1,
      type: 'TITLE',
      title: 'DecisionOS Strategic Boardroom Governance Deck',
      subtitle: 'Q4 Enterprise Portfolio Performance Review & 180-Day Strategic Directives',
      bullets: [
        'Deterministic Causal Recovery & Fiduciary Review',
        'Realized ARR Recovery: +$124,000 across 42 Monitoring Cycles',
        'Ratified Directives & Phased 180-Day Execution Roadmap',
      ],
      speakerNotes: 'Welcome members of the board. Today we review our verified portfolio recovery metrics and the ratified directives for Q4.',
      citations: [
        { source: 'KnowledgeGraphSnapshot V3', type: 'SNAPSHOT' },
        { source: 'PortfolioOptimizerEngine', type: 'OPTIMIZER' },
      ],
      metricPill: 'Verified Board Package',
    },
    {
      number: 2,
      type: 'HEALTH_KPI',
      title: 'Portfolio Health Lift: 74.0 → 85.0 (+11.0 pts)',
      subtitle: 'Macro Financial & Operational Performance Surge',
      bullets: [
        'Overall Portfolio Health improved by +11.0 points to 85.0/100',
        'Customer Retention stabilized at 84.2% (recovering from 79.5% low)',
        'Realized ARR Recovery achieved +$124,000 against $160K target (78% completion)',
      ],
      speakerNotes: 'Our recovery interventions produced measurable lift across health score and realized ARR without additional headcount.',
      citations: [
        { source: 'KPIEngine:CustomerRetention', type: 'KPI' },
        { source: 'OutcomeEngine:VerifiedARR', type: 'OUTCOME' },
      ],
      metricPill: '+$124K Realized ARR',
    },
    {
      number: 3,
      type: 'ROOT_CAUSE',
      title: 'Root Cause Resolution: Secondary Hub Dispatch Bottleneck',
      subtitle: 'RootCauseEngine #4 Causal Elimination',
      bullets: [
        'Root Cause #4 isolated transit delays to regional dispatch bottlenecks in Southeast',
        'Courier SLA compliance dropped to 78.4% prior to automated intervention',
        'Recommendation #1 resolved dispatch bottlenecks via automated load rebalancing',
      ],
      speakerNotes: 'RootCauseEngine mathematically proved transit delays stemmed from regional dispatch bottlenecks rather than customer churn intent.',
      citations: [
        { source: 'RootCauseEngine:HubBottleneck#4', type: 'ROOT_CAUSE' },
        { source: 'RecommendationEngine:CourierRebalance#1', type: 'RECOMMENDATION' },
      ],
      metricPill: 'Latency: 5.4d → 3.4d',
    },
    {
      number: 4,
      type: 'RECOVERY_PATH',
      title: 'Autonomous Recovery Path A Selected (94.0% Certainty)',
      subtitle: 'Decision Copilot Multi-Option Optimization',
      bullets: [
        'Path A (Retention First): +$124K ARR, +11.0 pts Health, 4.8x ROI (Selected)',
        'Path B (Growth First): +$98K ARR, +7.5 pts Health, 3.2x ROI',
        'Path C (Conservative): +$45K ARR, +3.2 pts Health, 2.1x ROI',
      ],
      speakerNotes: 'Decision Copilot evaluated three alternatives; Path A delivered the highest risk-adjusted ROI and fastest payback horizon.',
      citations: [
        { source: 'DecisionCopilot:PackageV3', type: 'DECISION_PACKAGE' },
        { source: 'CausalEngine:MultiOptionScore', type: 'CAUSAL' },
      ],
      metricPill: '4.8x ROI Multiplier',
    },
    {
      number: 5,
      type: 'SIMULATION',
      title: 'Digital Twin Simulation: Monte Carlo Run #12',
      subtitle: 'Deterministic Stress-Testing Under Volume Volatility',
      bullets: [
        '10,000 Monte Carlo simulation cycles confirmed 94% win probability',
        'Delivery latency bounded within 3.2d to 3.6d under +20% peak seasonal surge',
        'Zero downside capital risk observed under automated SLA penalty enforcement',
      ],
      speakerNotes: 'Digital twin simulations validated our assumptions under volatile seasonal volume swings.',
      citations: [
        { source: 'DigitalTwinEngine:Run#12', type: 'SIMULATION' },
        { source: 'MonteCarloEngine:Distribution', type: 'PROBABILITY' },
      ],
      metricPill: '94% Win Probability',
    },
    {
      number: 6,
      type: 'FORECAST',
      title: 'Rolling Recovery Forecast: $480K Annualized Run-Rate',
      subtitle: '88.4% Rolling 3-Cycle Forecast Accuracy',
      bullets: [
        'Rolling 3-cycle forecast accuracy achieved 88.4% (variance ±4.2%)',
        '180-day forecast projects $480,000 in cumulative recovered ARR',
        'Recovery velocity vector confirmed STABLE across four consecutive review periods',
      ],
      speakerNotes: 'Forecasting Engine indicates sustained ARR recovery velocity across upcoming quarters.',
      citations: [
        { source: 'ForecastEngine:ModelV3', type: 'FORECAST' },
        { source: 'ContinuousMonitoring:VarianceEnvelope', type: 'MONITORING' },
      ],
      metricPill: '88.4% Accuracy',
    },
    {
      number: 7,
      type: 'DIRECTIVES',
      title: 'Board Directives & Executive Ownership Matrix',
      subtitle: 'Accountability Tracking & Execution Mandates',
      bullets: [
        'Directive #1 (COO): Maintain 100% courier SLA penalty compliance ($124K ARR)',
        'Directive #2 (CFO): Reallocate $15,000 penalty surplus to northern expansion',
        'Directive #3 (VP CS): Complete 60-day customer win-back campaign ($82K ARR)',
      ],
      speakerNotes: 'These directives establish unambiguous fiduciary accountability across executive leaders.',
      citations: [
        { source: 'BoardDirectivesRegistry:Q4', type: 'DIRECTIVES' },
        { source: 'ExecutionCenter:INIT-2026-001', type: 'INITIATIVE' },
      ],
      metricPill: '95.2% Realization',
    },
    {
      number: 8,
      type: 'SIGN_OFF',
      title: 'Executive Fiduciary Sign-Off & Q&A',
      subtitle: 'Cryptographic SHA-256 Governance Verification',
      bullets: [
        'Governance Status: PUBLISHED & Formally Signed Off by CEO & Board Chair',
        'SHA-256 Seal: e3b0c44298fc1c... Verified via DecisionOS Governance Engine',
        '100% Citation Coverage Guarantee Across All 8 Deck Slides',
      ],
      speakerNotes: 'We now open the floor for board discussion and formal adoption of the 180-day recovery plan.',
      citations: [
        { source: 'ReportGovernanceAudit:Seal', type: 'AUDIT_SEAL' },
        { source: 'IntegrityVerificationEngine', type: 'VERIFICATION' },
      ],
      metricPill: '100% Verified Seal',
    },
  ];

  const currentSlide = slides[currentSlideIndex];

  const handleNext = () => {
    if (currentSlideIndex < slides.length - 1) {
      setCurrentSlideIndex(currentSlideIndex + 1);
    }
  };

  const handlePrev = () => {
    if (currentSlideIndex > 0) {
      setCurrentSlideIndex(currentSlideIndex - 1);
    }
  };

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.88)',
        backdropFilter: 'blur(10px)',
        zIndex: 300,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
        animation: 'fadeIn 0.15s ease',
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: '1080px',
          maxWidth: '96vw',
          maxHeight: '92vh',
          backgroundColor: '#090D14',
          border: '1px solid #1E293B',
          borderRadius: '16px',
          boxShadow: '0 25px 70px rgba(0,0,0,0.95)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Top Bar */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 24px', borderBottom: '1px solid #1E293B', background: '#070A0F' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Presentation size={18} color="#38BDF8" />
            <div>
              <span style={{ fontSize: '0.72rem', color: '#64748B', textTransform: 'uppercase', fontWeight: 800 }}>
                Boardroom Presentation Deck Viewer
              </span>
              <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#FFFFFF' }}>{reportTitle}</div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '0.8rem', color: '#94A3B8', fontWeight: 700 }}>
              Slide {currentSlide.number} of {slides.length}
            </span>
            <button
              onClick={onClose}
              style={{ background: 'rgba(30, 41, 59, 0.6)', border: '1px solid #334155', color: '#94A3B8', borderRadius: '6px', padding: '6px', cursor: 'pointer' }}
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Slide Canvas Area (16:9 Aspect Ratio Container) */}
        <div style={{ padding: '36px 48px', background: 'radial-gradient(ellipse at center, #0F172A 0%, #090D14 100%)', minHeight: '440px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span style={{ background: 'rgba(56, 189, 248, 0.15)', color: '#38BDF8', padding: '4px 12px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 800, textTransform: 'uppercase' }}>
                {currentSlide.type}
              </span>
              <span style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#10B981', padding: '4px 12px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 800 }}>
                ★ {currentSlide.metricPill}
              </span>
            </div>

            <h1 style={{ fontSize: '2rem', fontWeight: 900, color: '#FFFFFF', margin: '0 0 8px 0', letterSpacing: '-0.02em' }}>
              {currentSlide.title}
            </h1>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 500, color: '#94A3B8', margin: '0 0 28px 0' }}>
              {currentSlide.subtitle}
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {currentSlide.bullets.map((b, bIdx) => (
                <div key={bIdx} style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '1.05rem', color: '#F1F5F9', fontWeight: 600 }}>
                  <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#38BDF8' }} />
                  <span>{b}</span>
                </div>
              ))}
            </div>
          </div>

          {/* AI Citations Injection Callout */}
          <div style={{ marginTop: '30px', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid #1E293B', borderRadius: '10px', padding: '14px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={15} color="#A855F7" />
              <span style={{ fontSize: '0.78rem', color: '#A855F7', fontWeight: 800, textTransform: 'uppercase' }}>AI Verified Sources:</span>
              <div style={{ display: 'flex', gap: '8px', marginLeft: '6px' }}>
                {currentSlide.citations.map((c, cIdx) => (
                  <span key={cIdx} style={{ fontSize: '0.75rem', color: '#38BDF8', background: 'rgba(56, 189, 248, 0.12)', padding: '2px 8px', borderRadius: '4px', fontWeight: 600 }}>
                    • {c.source}
                  </span>
                ))}
              </div>
            </div>
            <span style={{ fontSize: '0.72rem', color: '#10B981', fontWeight: 700 }}>100% Grounded</span>
          </div>
        </div>

        {/* Speaker Notes Area */}
        <div style={{ padding: '14px 24px', background: '#070A0F', borderTop: '1px solid #1E293B', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1 }}>
            <FileText size={14} color="#64748B" />
            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 700, textTransform: 'uppercase' }}>Speaker Notes:</span>
            <span style={{ fontSize: '0.82rem', color: '#CBD5E1', fontStyle: 'italic', marginLeft: '4px' }}>
              "{currentSlide.speakerNotes}"
            </span>
          </div>

          {/* Carousel Navigation Controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              onClick={handlePrev}
              disabled={currentSlideIndex === 0}
              style={{
                padding: '6px 12px',
                background: currentSlideIndex === 0 ? 'rgba(30, 41, 59, 0.3)' : '#1E293B',
                border: 'none',
                borderRadius: '6px',
                color: currentSlideIndex === 0 ? '#475569' : '#FFFFFF',
                cursor: currentSlideIndex === 0 ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '0.8rem',
                fontWeight: 700,
              }}
            >
              <ChevronLeft size={14} />
              <span>Prev</span>
            </button>
            <button
              onClick={handleNext}
              disabled={currentSlideIndex === slides.length - 1}
              style={{
                padding: '6px 12px',
                background: currentSlideIndex === slides.length - 1 ? 'rgba(30, 41, 59, 0.3)' : '#0284C7',
                border: 'none',
                borderRadius: '6px',
                color: currentSlideIndex === slides.length - 1 ? '#475569' : '#FFFFFF',
                cursor: currentSlideIndex === slides.length - 1 ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '0.8rem',
                fontWeight: 700,
              }}
            >
              <span>Next</span>
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
