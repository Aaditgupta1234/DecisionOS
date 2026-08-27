import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ArrowRight, 
  Database, 
  BarChart2, 
  Search, 
  GitMerge, 
  Target, 
  TrendingUp, 
  ArrowUpRight, 
  CheckCircle2, 
  Sparkles,
  Layers,
  Cpu
} from 'lucide-react';
import '../../styles/home.css';
import { MarketingNavbar } from '../../components/layout/MarketingNavbar';
import { 
  FadeUp, 
  FadeIn, 
  StaggerContainer, 
  StaggerItem, 
  AnimatedCounter, 
  MotionCard 
} from '../../design-system/motion';

export const HomeView: React.FC = () => {
  return (
    <div className="home-root">
      
      {/* 1. Top Navigation Bar with Dynamic Scroll Progress Line */}
      <MarketingNavbar activeTab="home" />

      {/* ======================================================================
          2. Hero Section with Spotlight, Pedestal & Stable Telemetry
          ====================================================================== */}
      <section className="hero-section" id="platform">
        <div className="page-container hero-grid">
          
          {/* LEFT: Headline & Value Narrative with Executive Stagger */}
          <div className="hero-left">
            <FadeUp delay={0.05}>
              <div className="hero-badge">
                DETERMINISTIC EXECUTIVE INTELLIGENCE
              </div>
            </FadeUp>

            <FadeUp delay={0.12}>
              <h1 className="hero-headline">
                Know What’s Happening.<br />
                Understand Why.<br />
                Decide What Comes Next.
              </h1>
            </FadeUp>

            <FadeUp delay={0.18}>
              <p className="hero-desc">
                DecisionOS identifies why business performance changed, isolates root causes through deterministic analysis, and calculates the highest-impact actions to take next.
              </p>
            </FadeUp>

            <FadeUp delay={0.24}>
              <div className="hero-btn-row">
                <Link to="/enterprise" className="btn-hero-primary executive-motion-btn">
                  <span>Start Analysis</span>
                  <ArrowRight size={16} className="btn-icon-wrapper right" />
                </Link>
                <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="btn-hero-secondary executive-motion-btn">
                  <span>API Docs</span>
                  <div className="btn-play-circle">
                    <ArrowUpRight size={12} style={{ color: '#FFFFFF', marginLeft: '1px' }} />
                  </div>
                </a>
              </div>
            </FadeUp>

            {/* Trust Strip Directly Beneath CTAs */}
            <FadeUp delay={0.28}>
              <div className="hero-trust-strip">
                <span className="strip-item">783+ Tests</span>
                <span className="strip-dot">•</span>
                <span className="strip-item">100+ APIs</span>
                <span className="strip-dot">•</span>
                <span className="strip-item">25+ Engines</span>
                <span className="strip-dot">•</span>
                <span className="strip-item">Production Certified</span>
                <span className="strip-dot">•</span>
                <span className="strip-item">Explainable AI</span>
              </div>
            </FadeUp>
          </div>

          {/* RIGHT: Spotlight Beam, 3D Glowing Pedestal & Orbiting Telemetry */}
          <div className="hero-right-stage">
            {/* Overhead Single-Tone Clean Cone Spotlight Beam */}
            <div className="stage-spotlight-cone" aria-hidden="true" />

            {/* High-Fidelity 3D Pedestal Stage with Illuminated LED Rim (Pure Steel 620px Widen) */}
            <div className="stage-pedestal-wrap">
              <svg width="620" height="110" viewBox="0 0 620 110" fill="none" xmlns="http://www.w3.org/2000/svg" className="pedestal-svg">
                <defs>
                  {/* Top Disc Ambient Spotlight Reflection (Softened Pure Neutral Steel) */}
                  <radialGradient id="pedTopSurface" cx="50%" cy="38%" r="58%">
                    <stop offset="0%" stopColor="#383838" />
                    <stop offset="25%" stopColor="#242424" />
                    <stop offset="55%" stopColor="#141414" />
                    <stop offset="85%" stopColor="#080808" />
                    <stop offset="100%" stopColor="#030303" />
                  </radialGradient>

                  {/* Cylinder Wall Vertical Shadow Falloff (Pure Neutral Steel) */}
                  <linearGradient id="pedCylinderVertical" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="#282828" />
                    <stop offset="20%" stopColor="#181818" />
                    <stop offset="60%" stopColor="#0C0C0C" />
                    <stop offset="100%" stopColor="#020202" />
                  </linearGradient>

                  {/* Cylinder Horizontal Center Sheen (Pure Neutral Steel) */}
                  <linearGradient id="pedCylinderSheen" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#040404" stopOpacity="0.9" />
                    <stop offset="30%" stopColor="#1E1E1E" stopOpacity="0.35" />
                    <stop offset="50%" stopColor="#323232" stopOpacity="0.2" />
                    <stop offset="70%" stopColor="#1E1E1E" stopOpacity="0.35" />
                    <stop offset="100%" stopColor="#040404" stopOpacity="0.9" />
                  </linearGradient>

                  {/* Brilliant Neon Glow Filter */}
                  <filter id="pureNeonGlow" x="-25%" y="-45%" width="150%" height="190%">
                    <feGaussianBlur stdDeviation="6" result="blur1" />
                    <feGaussianBlur stdDeviation="2" result="blur2" />
                    <feMerge>
                      <feMergeNode in="blur1" />
                      <feMergeNode in="blur2" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>

                  {/* Soft Ground Contact Shadow Filter */}
                  <filter id="pedContactShadow" x="-20%" y="-30%" width="140%" height="160%">
                    <feGaussianBlur stdDeviation="14" />
                  </filter>
                </defs>

                {/* 1. Deep Atmospheric Ground Shadow */}
                <ellipse cx="310" cy="85" rx="275" ry="22" fill="rgba(0,0,0,0.95)" filter="url(#pedContactShadow)" />
                <ellipse cx="310" cy="80" rx="235" ry="16" fill="rgba(0,0,0,0.9)" />

                {/* 2. 3D Cylinder Extruded Side Wall */}
                <path
                  d="M 40,36 A 270 34 0 0 0 580,36 L 580,68 A 270 34 0 0 1 40,68 Z"
                  fill="url(#pedCylinderVertical)"
                />
                <path
                  d="M 40,36 A 270 34 0 0 0 580,36 L 580,68 A 270 34 0 0 1 40,68 Z"
                  fill="url(#pedCylinderSheen)"
                />

                {/* 3. Bottom Edge Bevel Line */}
                <path
                  d="M 40,68 A 270 34 0 0 0 580,68"
                  stroke="#161616"
                  strokeWidth="1.5"
                />

                {/* 4. Top Disc Surface Platform */}
                <ellipse cx="310" cy="36" rx="270" ry="34" fill="url(#pedTopSurface)" />

                {/* 5. Inner Inset Ring Edge */}
                <ellipse cx="310" cy="36" rx="269" ry="33" stroke="#080808" strokeWidth="2" fill="none" />

                {/* 6. Glowing Neon LED Ring (Softened 20% for Face Focus) */}
                <ellipse
                  cx="310"
                  cy="36"
                  rx="270"
                  ry="34"
                  stroke="rgba(255, 255, 255, 0.40)"
                  strokeWidth="3.2"
                  fill="none"
                  filter="url(#pureNeonGlow)"
                />

                {/* 7. Solid Razor-Sharp Core Ring (Softened 20%) */}
                <ellipse
                  cx="310"
                  cy="36"
                  rx="270"
                  ry="34"
                  stroke="rgba(255, 255, 255, 0.80)"
                  strokeWidth="1.6"
                  fill="none"
                />
              </svg>
            </div>

            {/* CENTERPIECE: Dominant Standalone 3D Spline Robot on Pedestal */}
            <div className="dex-bot-standalone">
              <iframe 
                src="/dex-robot.html" 
                className="dex-spline-iframe"
                title="DEX 3D Interactive Robot"
                allow="autoplay; fullscreen"
                style={{ background: 'transparent' }}
              />
            </div>

            {/* DEX Subtle Product Identity Tag */}
            <div className="dex-identity-tag">
              <span className="dex-name">DEX</span>
              <span className="dex-dot">•</span>
              <span className="dex-role">DEX Analyst Core</span>
              <span className="dex-dot">•</span>
              <span className="dex-sub">Deterministic Strategic Intelligence</span>
            </div>

            {/* Stable Telemetry Card 1: Top-Left Business Health Score */}
            <MotionCard className="telemetry-card card-pos-top-left state-glow-active-kpi" interactive={true}>
              <div className="t-card-header-flex">
                <span className="t-card-label">HEALTH SCORE</span>
                <span className="t-status-pill">Excellent</span>
              </div>
              <div className="t-card-metric-row">
                <span className="t-val-lg">82</span>
                <span className="t-val-sub">/100</span>
              </div>
              <div className="t-delta-trend">
                <span>▲ +7.2 pts this quarter</span>
              </div>
              <div className="t-sparkline-wrap">
                <svg width="100%" height="12" viewBox="0 0 100 12" preserveAspectRatio="none">
                  <path d="M0,9 Q25,12 50,5 T100,2" fill="none" stroke="#FFFFFF" strokeWidth="1.6" />
                </svg>
              </div>
            </MotionCard>

            {/* Stable Telemetry Card 2: Top-Right Forecast Confidence */}
            <MotionCard className="telemetry-card card-pos-top-right" interactive={true}>
              <div className="t-card-header-flex">
                <span className="t-card-label">DEX CONFIDENCE</span>
                <div className="t-circle-gauge">
                  <svg width="22" height="22" viewBox="0 0 36 36">
                    <path
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="rgba(255, 255, 255, 0.15)"
                      strokeWidth="3.2"
                    />
                    <path
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="#FFFFFF"
                      strokeWidth="3.2"
                      strokeDasharray="92, 100"
                      strokeLinecap="round"
                    />
                  </svg>
                </div>
              </div>
              <div className="t-card-metric-row">
                <span className="t-val-lg">92%</span>
                <span className="t-status-sub-inline">Optimal</span>
              </div>
              <div className="t-confidence-sub">Trusted Analysis</div>
            </MotionCard>

            {/* Stable Telemetry Card 3: Bottom-Left Retention Risk */}
            <MotionCard className="telemetry-card card-pos-bottom-left state-glow-risk" interactive={true}>
              <div className="t-card-header-flex">
                <span className="t-card-label">RETENTION RISK</span>
                <span className="t-status-pill">High</span>
              </div>
              <div className="t-card-metric-row">
                <span className="t-val-lg">14.2%</span>
                <span className="t-val-sub">Churn</span>
              </div>
              <div className="t-confidence-sub">Customer Retention</div>
            </MotionCard>

            {/* Stable Telemetry Card 4: Bottom-Right Recommended Action */}
            <MotionCard className="telemetry-card card-pos-bottom-right" interactive={true}>
              <div className="t-card-header-flex">
                <span className="t-card-label">RECOMMENDED</span>
                <span className="t-status-pill">Active</span>
              </div>
              <div className="t-card-metric-row">
                <span className="t-val-lg">+$180K</span>
                <span className="t-val-sub">ARR</span>
              </div>
              <div className="t-confidence-sub">Win-Back Campaign</div>
            </MotionCard>

          </div>

        </div>
      </section>

      {/* ======================================================================
          3. Why DecisionOS (The Paradigm Shift Table)
          ====================================================================== */}
      <section className="section-comparison-wrap" id="comparison">
        <div className="page-container">
          
          <div className="section-heading-center">
            <div className="section-badge">THE PARADIGM SHIFT</div>
            <h2 className="section-title-main">Why DecisionOS</h2>
            <p className="section-subtitle-main">
              Traditional tools show charts. DecisionOS computes root causes and delivers prioritized action plans.
            </p>
          </div>

          <div className="comparison-table-wrap">
            <div className="comparison-table">
              {/* Header */}
              <div className="comp-row comp-header">
                <div className="comp-col comp-col-dim">Dimension</div>
                <div className="comp-col comp-col-trad">Traditional Dashboard</div>
                <div className="comp-col comp-col-bi">BI Platform</div>
                <div className="comp-col comp-col-decisionos">DecisionOS</div>
              </div>

              {/* Row 1: Core Question */}
              <div className="comp-row">
                <div className="comp-col comp-col-dim">Core Question</div>
                <div className="comp-col comp-col-trad">What happened?</div>
                <div className="comp-col comp-col-bi">Where did it trend?</div>
                <div className="comp-col comp-col-decisionos">
                  <CheckCircle2 size={16} className="comp-check" />
                  <span>Why did it happen?</span>
                </div>
              </div>

              {/* Row 2: Focus */}
              <div className="comp-row">
                <div className="comp-col comp-col-dim">Focus</div>
                <div className="comp-col comp-col-trad">Metrics</div>
                <div className="comp-col comp-col-bi">Analytics</div>
                <div className="comp-col comp-col-decisionos">
                  <CheckCircle2 size={16} className="comp-check" />
                  <span>Decisions</span>
                </div>
              </div>

              {/* Row 3: Output */}
              <div className="comp-row">
                <div className="comp-col comp-col-dim">Output</div>
                <div className="comp-col comp-col-trad">Charts</div>
                <div className="comp-col comp-col-bi">Reports</div>
                <div className="comp-col comp-col-decisionos">
                  <CheckCircle2 size={16} className="comp-check" />
                  <span>Actions</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* ======================================================================
          4. The Signature Pipeline Section (DecisionOS's Moat)
          ====================================================================== */}
      <section className="section-pipeline-wrap" id="pipeline">
        <div className="page-container">
          
          <div className="section-heading-center">
            <div className="section-badge">END-TO-END MOAT</div>
            <h2 className="section-title-main">The Signature Intelligence Pipeline</h2>
            <p className="section-subtitle-main">
              From raw business telemetry to autonomous executive briefings in 8 deterministic stages.
            </p>
          </div>

          <StaggerContainer className="pipeline-grid-container" staggerDelay={0.065}>
            
            {/* Stage 1: Data */}
            <StaggerItem>
              <MotionCard className="pipeline-card" interactive={true}>
                <div className="pipeline-card-step">
                  <span>01. INGESTION</span>
                  <span className="pipeline-dot" />
                </div>
                <div className="pipeline-card-icon">
                  <Database size={18} />
                </div>
                <div className="pipeline-card-title">Data</div>
                <div className="pipeline-card-desc">Unified multi-source ingestion & schema normalization across ERP and transactional databases.</div>
              </MotionCard>
            </StaggerItem>

            {/* Stage 2: KPIs */}
            <StaggerItem>
              <MotionCard className="pipeline-card" interactive={true}>
                <div className="pipeline-card-step">
                  <span>02. METRICS</span>
                  <span className="pipeline-dot" />
                </div>
                <div className="pipeline-card-icon">
                  <BarChart2 size={18} />
                </div>
                <div className="pipeline-card-title">KPIs</div>
                <div className="pipeline-card-desc">Deterministic performance computation with period-over-period delta attribution.</div>
              </MotionCard>
            </StaggerItem>

            {/* Stage 3: Diagnostics */}
            <StaggerItem>
              <MotionCard className="pipeline-card" interactive={true}>
                <div className="pipeline-card-step">
                  <span>03. ANOMALY</span>
                  <span className="pipeline-dot" />
                </div>
                <div className="pipeline-card-icon">
                  <Search size={18} />
                </div>
                <div className="pipeline-card-title">Diagnostics</div>
                <div className="pipeline-card-desc">Statistical anomaly scanning, threshold breaches, and volatility pattern detection.</div>
              </MotionCard>
            </StaggerItem>

            {/* Stage 4: Root Cause */}
            <StaggerItem>
              <MotionCard className="pipeline-card" interactive={true}>
                <div className="pipeline-card-step">
                  <span>04. ATTRIBUTION</span>
                  <span className="pipeline-dot" />
                </div>
                <div className="pipeline-card-icon">
                  <GitMerge size={18} />
                </div>
                <div className="pipeline-card-title">Root Cause</div>
                <div className="pipeline-card-desc">Multi-dimensional variance isolation pinpointing exact revenue and cost drivers.</div>
              </MotionCard>
            </StaggerItem>

            {/* Stage 5: Recommendations */}
            <StaggerItem>
              <MotionCard className="pipeline-card" interactive={true}>
                <div className="pipeline-card-step">
                  <span>05. ACTIONS</span>
                  <span className="pipeline-dot" />
                </div>
                <div className="pipeline-card-icon">
                  <Target size={18} />
                </div>
                <div className="pipeline-card-title">Recommendations</div>
                <div className="pipeline-card-desc">Prioritized corrective playbooks ranked by expected revenue impact and feasibility.</div>
              </MotionCard>
            </StaggerItem>

            {/* Stage 6: Forecasting */}
            <StaggerItem>
              <MotionCard className="pipeline-card" interactive={true}>
                <div className="pipeline-card-step">
                  <span>06. SIMULATION</span>
                  <span className="pipeline-dot" />
                </div>
                <div className="pipeline-card-icon">
                  <TrendingUp size={18} />
                </div>
                <div className="pipeline-card-title">Forecasting</div>
                <div className="pipeline-card-desc">Predictive modeling with confidence intervals and what-if scenario simulations.</div>
              </MotionCard>
            </StaggerItem>

            {/* Stage 7: Executive Intelligence */}
            <StaggerItem>
              <Link to="/kpi-dictionary" style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}>
                <MotionCard className="pipeline-card" interactive={true}>
                  <div className="pipeline-card-step">
                    <span>07. SYNTHESIS</span>
                    <span className="pipeline-dot" />
                  </div>
                  <div className="pipeline-card-icon">
                    <Layers size={18} />
                  </div>
                  <div className="pipeline-card-title">Executive Intelligence</div>
                  <div className="pipeline-card-desc">Natural language executive briefs and strategic decision summaries.</div>
                </MotionCard>
              </Link>
            </StaggerItem>

            {/* Stage 8: DEX Analyst */}
            <StaggerItem>
              <MotionCard className="pipeline-card pipeline-card-highlight" interactive={true}>
                <div className="pipeline-card-step">
                  <span style={{ color: '#FFFFFF' }}>08. AUTONOMOUS</span>
                  <Sparkles size={12} style={{ color: '#FFFFFF' }} />
                </div>
                <div className="pipeline-card-icon">
                  <Cpu size={20} />
                </div>
                <div className="pipeline-card-title" style={{ color: '#FFFFFF' }}>DEX Analyst</div>
                <div className="pipeline-card-desc" style={{ color: '#C5CCD6' }}>Your autonomous 24/7 AI decision analyst providing conversational deep dives.</div>
              </MotionCard>
            </StaggerItem>

          </StaggerContainer>

        </div>
      </section>

      {/* ======================================================================
          4. Executive Intelligence Overview (Command Center Cockpit)
          ====================================================================== */}
      <section className="section-overview-wrap" id="solutions">
        <div className="page-container">
          
          <FadeUp>
            <div className="section-heading-center">
              <div className="section-badge">DECISIONOS COMMAND CENTER</div>
              <h2 className="section-title-main">Executive Intelligence Overview</h2>
              <p className="section-subtitle-main">
                A real-time command center for data-driven leaders.
              </p>
            </div>
          </FadeUp>

          <div className="cockpit-container">
            
            {/* Top Stat / Summary Row with Animated Counters */}
            <div className="cockpit-top-row">
              
              {/* Stat 1: Total Revenue */}
              <MotionCard className="cockpit-stat-card" interactive={true}>
                <div className="c-stat-title">Total Revenue</div>
                <div className="c-stat-num">
                  <AnimatedCounter value={4.2} prefix="$" suffix="M" decimals={1} />
                </div>
                <div className="c-stat-delta delta-pos">
                  <span>+12.4%</span>
                  <span className="delta-sub">vs last period ↗</span>
                </div>
              </MotionCard>

              {/* Stat 2: Orders */}
              <MotionCard className="cockpit-stat-card" interactive={true}>
                <div className="c-stat-title">Orders</div>
                <div className="c-stat-num">
                  <AnimatedCounter value={18530} />
                </div>
                <div className="c-stat-delta delta-pos">
                  <span>+8.7%</span>
                  <span className="delta-sub">vs last period ↗</span>
                </div>
              </MotionCard>

              {/* Stat 3: Customers */}
              <MotionCard className="cockpit-stat-card" interactive={true}>
                <div className="c-stat-title">Customers</div>
                <div className="c-stat-num">
                  <AnimatedCounter value={6842} />
                </div>
                <div className="c-stat-delta delta-pos">
                  <span>+11.3%</span>
                  <span className="delta-sub">vs last period ↗</span>
                </div>
              </MotionCard>

              {/* Stat 4: Business Health Score (Flagship Wide Anchor) */}
              <MotionCard className="cockpit-stat-card cockpit-health-card state-glow-active-kpi" interactive={true}>
                <div className="c-stat-title-flex">
                  <span className="c-stat-title">Business Health Score</span>
                  <span className="badge-health-status">Excellent</span>
                </div>
                <div className="c-health-flex">
                  <div>
                    <div className="c-stat-num">
                      <AnimatedCounter value={82} durationMs={850} /> <span style={{ fontSize: '13px', color: '#727A86', fontWeight: 500 }}>/100</span>
                    </div>
                    <div className="c-health-track-info">
                      <div className="c-health-bar-wrap">
                        <div className="c-health-bar-fill" style={{ width: '82%' }} />
                      </div>
                      <span className="c-health-label">Optimal Performance</span>
                    </div>
                  </div>
                  <div className="c-ring-gauge state-glow-health">
                    <svg width="44" height="44" viewBox="0 0 36 36">
                      <path
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                        fill="none"
                        stroke="rgba(255, 255, 255, 0.10)"
                        strokeWidth="3.2"
                      />
                      <path
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                        fill="none"
                        stroke="#10B981"
                        strokeWidth="3.2"
                        strokeDasharray="82, 100"
                        strokeLinecap="round"
                      />
                    </svg>
                    <span className="gauge-center-text">82%</span>
                  </div>
                </div>
              </MotionCard>

              {/* Stat 5: Executive Summary Card (Structured DEX Synthesis) */}
              <MotionCard className="cockpit-summary-card" interactive={true}>
                <div className="c-sum-header">
                  <span>Executive Summary</span>
                  <span className="c-ai-badge">DEX Analyst</span>
                </div>
                <div className="c-sum-structured">
                  <div className="c-sum-lead">
                    Revenue grew <strong className="text-emerald">+12.4% (+$463K)</strong> driven primarily by:
                  </div>
                  <ul className="c-sum-bullets">
                    <li>• Returning customers <span className="text-emerald">(+6.2%)</span></li>
                    <li>• Higher average order value <span className="text-emerald">(+4.8%)</span></li>
                  </ul>
                  <div className="c-sum-risk">
                    <span className="risk-tag">Primary risk:</span> Retention declined <span className="text-crimson">4.3%</span>
                  </div>
                </div>
                <Link to="/reports" className="btn-sum-action">
                  View Full Report
                </Link>
              </MotionCard>

            </div>

            {/* Bottom Cockpit Main Grid: 2 Charts + Right Root Cause Panel */}
            <div className="cockpit-charts-grid">
              
              {/* Left Chart: Revenue Trend (12 Months) */}
              <div className="cockpit-chart-card">
                <div className="chart-head-flex">
                  <div>
                    <div className="chart-main-title">Revenue Trend</div>
                    <div className="chart-sub-tag">✓ Last 12 Months</div>
                  </div>
                  <div className="chart-badge-val">
                    <div className="badge-amount">$4.2M</div>
                    <div className="badge-date">Dec 2024</div>
                  </div>
                </div>

                <div className="chart-svg-area">
                  <div className="chart-y-axis">
                    <span>$5M</span>
                    <span>$4M</span>
                    <span>$3M</span>
                    <span>$2M</span>
                    <span>$1M</span>
                    <span>$0</span>
                  </div>
                  <div className="chart-canvas-box">
                    <svg width="100%" height="100%" viewBox="0 0 420 120" preserveAspectRatio="none">
                      {/* Grid lines */}
                      <line x1="0" y1="20" x2="420" y2="20" stroke="#1A1E26" strokeWidth="1" strokeDasharray="3 3" />
                      <line x1="0" y1="50" x2="420" y2="50" stroke="#1A1E26" strokeWidth="1" strokeDasharray="3 3" />
                      <line x1="0" y1="80" x2="420" y2="80" stroke="#1A1E26" strokeWidth="1" strokeDasharray="3 3" />
                      <line x1="0" y1="110" x2="420" y2="110" stroke="#1A1E26" strokeWidth="1" />
                      
                      {/* Revenue Smooth Curve */}
                      <path
                        d="M0,110 Q35,100 70,90 T140,75 T210,85 T280,60 T350,45 T420,25"
                        fill="none"
                        stroke="#FFFFFF"
                        strokeWidth="2.2"
                      />
                      <circle cx="420" cy="25" r="4" fill="#FFFFFF" />
                    </svg>
                  </div>
                </div>

                <div className="chart-x-axis">
                  <span>Jan</span><span>Feb</span><span>Mar</span><span>Apr</span>
                  <span>May</span><span>Jun</span><span>Jul</span><span>Aug</span>
                  <span>Sep</span><span>Oct</span><span>Nov</span><span>Dec</span>
                </div>
              </div>

              {/* Middle Chart: Forecast (Next 3 Months) */}
              <div className="cockpit-chart-card">
                <div className="chart-head-flex">
                  <div>
                    <div className="chart-main-title">Forecast <span style={{ color: '#727A86', fontWeight: '400', fontSize: '12px' }}>(Next 3 Months)</span></div>
                    <div className="chart-sub-tag">Projected Revenue</div>
                  </div>
                </div>

                <div className="forecast-metric-lead">
                  <span className="fc-amount">$4.8M</span>
                  <span className="fc-delta">+9.6% growth</span>
                </div>

                <div className="forecast-svg-area">
                  <svg width="100%" height="100%" viewBox="0 0 280 80" preserveAspectRatio="none">
                    <line x1="0" y1="75" x2="280" y2="75" stroke="#1A1E26" strokeWidth="1" />
                    <path
                      d="M0,65 Q90,55 185,30 T280,10"
                      fill="none"
                      stroke="#FFFFFF"
                      strokeWidth="2"
                    />
                    <circle cx="0" cy="65" r="3.5" fill="#FFFFFF" />
                    <circle cx="93" cy="50" r="3.5" fill="#FFFFFF" />
                    <circle cx="186" cy="30" r="3.5" fill="#FFFFFF" />
                    <circle cx="280" cy="10" r="3.5" fill="#FFFFFF" />
                  </svg>
                </div>

                <div className="forecast-x-axis">
                  <span>Dec</span><span>Jan</span><span>Feb</span><span>Mar</span>
                </div>
              </div>

              {/* Right Root Cause Panel (Deterministic Diagnosis) */}
              <div className="cockpit-root-cause-card">
                <div className="rc-tag-row">
                  <span className="rc-tag">Top Root Cause</span>
                  <span className="rc-conf-badge">91% Confidence</span>
                </div>
                <div className="rc-heading">Customer Retention Decline</div>
                <div className="rc-impact-row">
                  <span className="rc-impact-badge">Impact: High</span>
                  <span className="rc-loss-estimate">Est. Impact: -$218K / qtr</span>
                </div>
                <p className="rc-desc">
                  Deterministic attribution isolated checkout latency spikes (+420ms) and shipping delays across tier-1 carriers.
                </p>
                <Link to="/root-causes" className="btn-rc-action">
                  Explore Root Cause
                </Link>
              </div>

            </div>

          </div>

        </div>
      </section>

      {/* ======================================================================
          5. CTA Banner: Turn Data Into Decisions
          ====================================================================== */}
      <section className="section-cta-wrap" id="resources">
        <div className="page-container">
          
          <div className="cta-cockpit-banner">
            <div className="cta-left-part">
              <div className="cta-sparkle-box">
                <Sparkles size={28} className="cta-sparkle-svg" />
              </div>
              <div className="cta-text-content">
                <h3 className="cta-title">Turn Data Into Decisions</h3>
                <p className="cta-subtitle">
                  Understand performance, uncover root causes, forecast outcomes, and make smarter decisions with DecisionOS.
                </p>
              </div>
            </div>

            <div className="cta-right-btns">
              <Link to="/enterprise" className="btn-cta-primary">
                <span>Start Analysis</span>
                <ArrowRight size={15} />
              </Link>
              <a 
                href="http://localhost:8000/docs" 
                target="_blank" 
                rel="noreferrer"
                className="btn-cta-secondary"
                style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
              >
                <span>API Docs</span>
                <ArrowUpRight size={13} />
              </a>
            </div>
          </div>

        </div>
      </section>

      {/* ======================================================================
          6. Footer
          ====================================================================== */}
      <footer className="site-footer">
        <div className="page-container footer-flex">
          <div className="footer-left">
            <span className="footer-logo">DecisionOS</span>
            <span className="footer-copy">© 2025 DecisionOS. All rights reserved.</span>
          </div>

          <div className="footer-links">
            <span className="f-link">Privacy Policy</span>
            <span className="f-link">Terms of Service</span>
            <span className="f-link">Security</span>
            <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="f-link">API Documentation</a>
            <span className="f-link">System Status</span>
          </div>
        </div>
      </footer>

    </div>
  );
};

export default HomeView;
