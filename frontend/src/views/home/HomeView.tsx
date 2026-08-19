import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  ArrowRight, 
  Play, 
  Database, 
  BarChart2, 
  Search, 
  GitMerge, 
  Target, 
  TrendingUp, 
  FileText, 
  Bot, 
  AlertTriangle, 
  Sparkles, 
  ArrowUpRight,
  TrendingDown,
  Layers,
  Cpu,
  ShieldCheck,
  Activity,
  CheckCircle2,
  Zap,
  ArrowDown
} from 'lucide-react';
import '../../styles/home.css';

export const HomeView: React.FC = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0);

  useEffect(() => {
    let ticking = false;

    const handleScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          const scrollPos = 
            window.scrollY || 
            document.documentElement.scrollTop || 
            document.body.scrollTop || 
            0;
          
          const totalHeight = 
            document.documentElement.scrollHeight - document.documentElement.clientHeight;
          
          const progress = totalHeight > 0 ? (scrollPos / totalHeight) * 100 : 0;

          setIsScrolled(scrollPos > 10);
          setScrollProgress(Math.min(Math.max(progress, 0), 100));
          ticking = false;
        });
        ticking = true;
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true, capture: true });
    document.addEventListener('scroll', handleScroll, { passive: true, capture: true });
    handleScroll();

    return () => {
      window.removeEventListener('scroll', handleScroll, true);
      document.removeEventListener('scroll', handleScroll, true);
    };
  }, []);

  return (
    <div className="page-root">
      
      {/* ======================================================================
          1. Top Navigation Bar with Dynamic Scroll Progress Line
          ====================================================================== */}
      <header className={`top-nav-wrapper ${isScrolled ? 'is-scrolled' : ''}`}>
        {/* Dynamic Scroll Progress Line that increases in length on scroll */}
        <div 
          className="nav-scroll-progress-line" 
          style={{ transform: `scaleX(${scrollProgress / 100})` }}
          aria-hidden="true" 
        />

        <nav className="top-nav">
          <div className="page-container top-nav-inner">
            <Link to="/" className="nav-brand">
              <span className="nav-brand-text">DecisionOS</span>
            </Link>

            <div className="nav-links">
              <a href="#comparison" className="nav-link">Why DecisionOS</a>
              <a href="#pipeline" className="nav-link">Signature Pipeline</a>
              <a href="#intelligence" className="nav-link">Intelligence</a>
              <a href="#solutions" className="nav-link">Solutions</a>
              <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="nav-link">Docs</a>
            </div>

            <Link to="/dashboard" className="btn-nav-access">
              Access Platform
            </Link>
          </div>
        </nav>
      </header>

      {/* ======================================================================
          2. Hero Section with Spotlight, Pedestal & Symmetrical Telemetry
          ====================================================================== */}
      <section className="hero-section" id="platform">
        <div className="page-container hero-grid">
          
          {/* LEFT: Headline & Value Narrative */}
          <div className="hero-left">
            <div className="hero-badge">
              DETERMINISTIC EXECUTIVE INTELLIGENCE
            </div>

            <h1 className="hero-headline">
              Know What’s Happening.<br />
              Understand Why.<br />
              Decide What Comes Next.
            </h1>

            <p className="hero-desc">
              DecisionOS identifies why business performance changed, isolates root causes through deterministic analysis, and calculates the highest-impact actions to take next.
            </p>

            <div className="hero-btn-row">
              <Link to="/dashboard" className="btn-hero-primary">
                <span>Start Analysis</span>
                <ArrowRight size={16} />
              </Link>
              <a href="#intelligence" className="btn-hero-secondary">
                <span>Watch Demo</span>
                <div className="btn-play-circle">
                  <Play size={10} style={{ fill: '#FFFFFF', marginLeft: '1px' }} />
                </div>
              </a>
            </div>

            {/* Trust Strip Directly Beneath CTAs */}
            <div className="hero-trust-strip">
              <span className="strip-item">783+ Tests</span>
              <span className="strip-dot">•</span>
              <span className="strip-item">100+ APIs</span>
              <span className="strip-dot">•</span>
              <span className="strip-item">25+ Engines</span>
              <span className="strip-dot">•</span>
              <span className="strip-item">14 Development Phases</span>
              <span className="strip-dot">•</span>
              <span className="strip-item">Deterministic Intelligence</span>
            </div>
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
              <span className="dex-role">Decision Execution Engine</span>
              <span className="dex-dot">•</span>
              <span className="dex-sub">Deterministic Strategic Intelligence Core</span>
            </div>

            {/* Orbiting Telemetry Card 1: Top-Left Business Health Score */}
            <div className="telemetry-card card-pos-top-left">
              <div className="t-card-label">HEALTH SCORE</div>
              <div className="t-card-metric-row">
                <span className="t-val-lg">82</span>
                <span className="t-val-sub">/100</span>
              </div>
              <div className="t-sparkline-wrap">
                <svg width="100%" height="14" viewBox="0 0 100 14" preserveAspectRatio="none">
                  <path d="M0,10 Q25,14 50,6 T100,3" fill="none" stroke="#FFFFFF" strokeWidth="1.5" />
                </svg>
              </div>
            </div>

            {/* Orbiting Telemetry Card 2: Top-Right Forecast Confidence */}
            <div className="telemetry-card card-pos-top-right">
              <div className="t-card-label">CONFIDENCE</div>
              <div className="t-forecast-row">
                <div>
                  <div className="t-val-lg">92%</div>
                  <div className="t-status-sub">Optimal</div>
                </div>
                <div className="t-circle-gauge">
                  <svg width="26" height="26" viewBox="0 0 36 36">
                    <path
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="rgba(255, 255, 255, 0.15)"
                      strokeWidth="3"
                    />
                    <path
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="#FFFFFF"
                      strokeWidth="3"
                      strokeDasharray="92, 100"
                    />
                  </svg>
                </div>
              </div>
            </div>

            {/* Orbiting Telemetry Card 3: Bottom-Left Top Risk (Compact Badge) */}
            <div className="telemetry-card card-pos-bottom-left">
              <div className="t-risk-header">
                <span className="t-card-label">TOP RISK</span>
                <span className="t-risk-badge">
                  <AlertTriangle size={10} className="t-risk-icon" />
                  <span>High</span>
                </span>
              </div>
              <div className="t-risk-title">Customer Retention</div>
              <div className="t-card-subtext">Exposure: 14.2% Churn</div>
            </div>

            {/* Orbiting Telemetry Card 4: Bottom-Right Recommended Action (Compact Badge) */}
            <div className="telemetry-card card-pos-bottom-right">
              <div className="t-action-header">
                <span className="t-card-label">RECOMMENDED</span>
                <span className="t-action-pill">High Priority</span>
              </div>
              <div className="t-action-title">Win-Back Campaign</div>
              <div className="t-action-footer">
                <span>+$180k ARR Target</span>
                <ArrowUpRight size={12} style={{ color: '#FFFFFF' }} />
              </div>
            </div>

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

          <div className="pipeline-grid-container">
            
            {/* Stage 1: Data */}
            <div className="pipeline-card">
              <div className="pipeline-card-step">
                <span>01. INGESTION</span>
                <span className="pipeline-dot" />
              </div>
              <div className="pipeline-card-icon">
                <Database size={18} />
              </div>
              <div className="pipeline-card-title">Data</div>
              <div className="pipeline-card-desc">Unified multi-source ingestion & schema normalization across ERP and transactional databases.</div>
            </div>

            {/* Stage 2: KPIs */}
            <div className="pipeline-card">
              <div className="pipeline-card-step">
                <span>02. METRICS</span>
                <span className="pipeline-dot" />
              </div>
              <div className="pipeline-card-icon">
                <BarChart2 size={18} />
              </div>
              <div className="pipeline-card-title">KPIs</div>
              <div className="pipeline-card-desc">Deterministic performance computation with period-over-period delta attribution.</div>
            </div>

            {/* Stage 3: Diagnostics */}
            <div className="pipeline-card">
              <div className="pipeline-card-step">
                <span>03. ANOMALY</span>
                <span className="pipeline-dot" />
              </div>
              <div className="pipeline-card-icon">
                <Search size={18} />
              </div>
              <div className="pipeline-card-title">Diagnostics</div>
              <div className="pipeline-card-desc">Statistical anomaly scanning, threshold breaches, and volatility pattern detection.</div>
            </div>

            {/* Stage 4: Root Cause */}
            <div className="pipeline-card">
              <div className="pipeline-card-step">
                <span>04. ATTRIBUTION</span>
                <span className="pipeline-dot" />
              </div>
              <div className="pipeline-card-icon">
                <GitMerge size={18} />
              </div>
              <div className="pipeline-card-title">Root Cause</div>
              <div className="pipeline-card-desc">Multi-dimensional variance isolation pinpointing exact revenue and cost drivers.</div>
            </div>

            {/* Stage 5: Recommendations */}
            <div className="pipeline-card">
              <div className="pipeline-card-step">
                <span>05. ACTIONS</span>
                <span className="pipeline-dot" />
              </div>
              <div className="pipeline-card-icon">
                <Target size={18} />
              </div>
              <div className="pipeline-card-title">Recommendations</div>
              <div className="pipeline-card-desc">Prioritized corrective playbooks ranked by expected revenue impact and feasibility.</div>
            </div>

            {/* Stage 6: Forecasting */}
            <div className="pipeline-card">
              <div className="pipeline-card-step">
                <span>06. SIMULATION</span>
                <span className="pipeline-dot" />
              </div>
              <div className="pipeline-card-icon">
                <TrendingUp size={18} />
              </div>
              <div className="pipeline-card-title">Forecasting</div>
              <div className="pipeline-card-desc">Predictive modeling with confidence intervals and what-if scenario simulations.</div>
            </div>

            {/* Stage 7: Executive Intelligence */}
            <div className="pipeline-card">
              <div className="pipeline-card-step">
                <span>07. SYNTHESIS</span>
                <span className="pipeline-dot" />
              </div>
              <div className="pipeline-card-icon">
                <FileText size={18} />
              </div>
              <div className="pipeline-card-title">Executive Intelligence</div>
              <div className="pipeline-card-desc">Natural language executive briefs and strategic decision summaries.</div>
            </div>

            {/* Stage 8: DEX */}
            <div className="pipeline-card pipeline-card-highlight">
              <div className="pipeline-card-step">
                <span style={{ color: '#FFFFFF' }}>08. AUTONOMOUS</span>
                <Sparkles size={12} style={{ color: '#FFFFFF' }} />
              </div>
              <div className="pipeline-card-icon">
                <Bot size={20} />
              </div>
              <div className="pipeline-card-title" style={{ color: '#FFFFFF' }}>DEX</div>
              <div className="pipeline-card-desc" style={{ color: '#C5CCD6' }}>Your autonomous 24/7 AI decision analyst providing conversational deep dives.</div>
            </div>

          </div>

        </div>
      </section>

      {/* ======================================================================
          4. Executive Intelligence Overview (Command Center Cockpit)
          ====================================================================== */}
      <section className="section-overview-wrap" id="solutions">
        <div className="page-container">
          
          <div className="section-heading-center">
            <h2 className="section-title-main">Executive Intelligence Overview</h2>
            <p className="section-subtitle-main">
              A real-time command center for data-driven leaders.
            </p>
          </div>

          <div className="cockpit-container">
            
            {/* Top 5 Stat / Summary Row */}
            <div className="cockpit-top-row">
              
              {/* Stat 1: Total Revenue */}
              <div className="cockpit-stat-card">
                <div className="c-stat-title">Total Revenue</div>
                <div className="c-stat-num">$4.2M</div>
                <div className="c-stat-delta">+12.4% vs last period</div>
              </div>

              {/* Stat 2: Orders */}
              <div className="cockpit-stat-card">
                <div className="c-stat-title">Orders</div>
                <div className="c-stat-num">18,530</div>
                <div className="c-stat-delta delta-pos">+8.7% vs last period ↗</div>
              </div>

              {/* Stat 3: Customers */}
              <div className="cockpit-stat-card">
                <div className="c-stat-title">Customers</div>
                <div className="c-stat-num">6,842</div>
                <div className="c-stat-delta delta-pos">+11.3% vs last period ↗</div>
              </div>

              {/* Stat 4: Business Health Score */}
              <div className="cockpit-stat-card">
                <div className="c-stat-title">Business Health Score</div>
                <div className="c-health-flex">
                  <div>
                    <div className="c-stat-num">82 <span style={{ fontSize: '13px', color: '#727A86' }}>/100</span></div>
                    <div className="c-stat-delta" style={{ color: '#B5BAC4' }}>Good Performance</div>
                  </div>
                  <div className="c-ring-gauge">
                    <svg width="34" height="34" viewBox="0 0 36 36">
                      <path
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                        fill="none"
                        stroke="rgba(255, 255, 255, 0.15)"
                        strokeWidth="3"
                      />
                      <path
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                        fill="none"
                        stroke="#FFFFFF"
                        strokeWidth="3"
                        strokeDasharray="82, 100"
                      />
                    </svg>
                  </div>
                </div>
              </div>

              {/* Stat 5: Executive Summary Card */}
              <div className="cockpit-summary-card">
                <div className="c-sum-header">Executive Summary</div>
                <p className="c-sum-text">
                  Revenue increased 12.4% driven by higher AOV and returning customers. However, customer retention declined 4.3% due to increased churn in the last 30 days.
                </p>
                <Link to="/reports" className="btn-sum-action">
                  View Full Report
                </Link>
              </div>

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

              {/* Right Root Cause Panel */}
              <div className="cockpit-root-cause-card">
                <div className="rc-tag">Top Root Cause</div>
                <div className="rc-heading">Customer Retention Decline</div>
                <div className="rc-impact-badge">Impact: High</div>
                <p className="rc-desc">
                  Analysis shows churn increased due to late deliveries and reduced engagement in the last 30 days.
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
              <Link to="/dashboard" className="btn-cta-primary">
                <span>Start Analysis</span>
                <ArrowRight size={15} />
              </Link>
              <button 
                onClick={() => alert("Briefing request sent. Our team will contact you shortly.")} 
                className="btn-cta-secondary"
              >
                <span>Request Demo</span>
              </button>
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
