import React from 'react';
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
  Activity
} from 'lucide-react';
import '../../styles/home.css';

export const HomeView: React.FC = () => {
  return (
    <div className="page-root">
      
      {/* ======================================================================
          1. Top Navigation Bar
          ====================================================================== */}
      <nav className="top-nav">
        <div className="page-container top-nav-inner">
          <Link to="/" className="nav-brand">
            <span className="nav-brand-text">DecisionOS</span>
          </Link>

          <div className="nav-links">
            <a href="#platform" className="nav-link">Platform</a>
            <a href="#intelligence" className="nav-link">Intelligence</a>
            <a href="#solutions" className="nav-link">Solutions</a>
            <a href="#resources" className="nav-link">Resources</a>
            <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="nav-link">Docs</a>
          </div>

          <Link to="/dashboard" className="btn-nav-access">
            Access Platform
          </Link>
        </div>
      </nav>

      {/* ======================================================================
          2. Hero Section with Spotlight, Pedestal & Symmetrical Telemetry
          ====================================================================== */}
      <section className="hero-section" id="platform">
        <div className="page-container hero-grid">
          
          {/* LEFT: Headline & Value Narrative */}
          <div className="hero-left">
            <div className="hero-badge">
              AI-NATIVE BUSINESS INTELLIGENCE
            </div>

            <h1 className="hero-headline">
              Know What’s<br />
              Happening.<br />
              Understand Why.<br />
              Decide What Comes<br />
              Next.
            </h1>

            <p className="hero-desc">
              DecisionOS transforms business data into explainable intelligence through KPI analysis, diagnostics, root cause discovery, forecasting, and AI-powered executive insights.
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

            {/* Trusted Strip */}
            <div className="hero-trust-block">
              <div className="trust-heading">TRUSTED BY ANALYTICAL LEADERS</div>
              <div className="trust-items">
                <div className="trust-chip">
                  <BarChart2 size={13} className="trust-icon" />
                  <span>KPI Intelligence</span>
                </div>
                <div className="trust-chip">
                  <GitMerge size={13} className="trust-icon" />
                  <span>Root Cause Analysis</span>
                </div>
                <div className="trust-chip">
                  <TrendingUp size={13} className="trust-icon" />
                  <span>Forecasting Engine</span>
                </div>
                <div className="trust-chip">
                  <Bot size={13} className="trust-icon" />
                  <span>AI Analyst</span>
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT: Spotlight Beam, 3D Glowing Pedestal & Orbiting Telemetry */}
          <div className="hero-right-stage">
            {/* High-Fidelity 3D Pedestal Stage with Illuminated LED Rim (Pure Vector/CSS) */}
            <div className="stage-pedestal-wrap">
              <svg width="480" height="130" viewBox="0 0 480 130" fill="none" xmlns="http://www.w3.org/2000/svg" className="pedestal-svg">
                <defs>
                  {/* Top Disc Ambient Spotlight Reflection */}
                  <radialGradient id="pedTopSurface" cx="50%" cy="38%" r="58%">
                    <stop offset="0%" stopColor="#555E70" />
                    <stop offset="25%" stopColor="#363E4B" />
                    <stop offset="55%" stopColor="#1B2028" />
                    <stop offset="85%" stopColor="#0E1015" />
                    <stop offset="100%" stopColor="#06070A" />
                  </radialGradient>

                  {/* Cylinder Wall Vertical Shadow Falloff */}
                  <linearGradient id="pedCylinderVertical" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="#2A303C" />
                    <stop offset="20%" stopColor="#181B22" />
                    <stop offset="60%" stopColor="#0B0D11" />
                    <stop offset="100%" stopColor="#020304" />
                  </linearGradient>

                  {/* Cylinder Horizontal Center Sheen */}
                  <linearGradient id="pedCylinderSheen" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#040507" stopOpacity="0.9" />
                    <stop offset="30%" stopColor="#1C212A" stopOpacity="0.5" />
                    <stop offset="50%" stopColor="#323A48" stopOpacity="0.3" />
                    <stop offset="70%" stopColor="#1C212A" stopOpacity="0.5" />
                    <stop offset="100%" stopColor="#040507" stopOpacity="0.9" />
                  </linearGradient>

                  {/* Brilliant Neon Glow Filter */}
                  <filter id="pureNeonGlow" x="-25%" y="-45%" width="150%" height="190%">
                    <feGaussianBlur stdDeviation="7.5" result="blur1" />
                    <feGaussianBlur stdDeviation="2.5" result="blur2" />
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
                <ellipse cx="240" cy="100" rx="215" ry="24" fill="rgba(0,0,0,0.95)" filter="url(#pedContactShadow)" />
                <ellipse cx="240" cy="94" rx="180" ry="18" fill="rgba(0,0,0,0.9)" />

                {/* 2. 3D Cylinder Extruded Side Wall */}
                <path
                  d="M 35,42 A 205 38 0 0 0 445,42 L 445,78 A 205 38 0 0 1 35,78 Z"
                  fill="url(#pedCylinderVertical)"
                />
                <path
                  d="M 35,42 A 205 38 0 0 0 445,42 L 445,78 A 205 38 0 0 1 35,78 Z"
                  fill="url(#pedCylinderSheen)"
                />

                {/* 3. Bottom Edge Bevel Line */}
                <path
                  d="M 35,78 A 205 38 0 0 0 445,78"
                  stroke="#161920"
                  strokeWidth="1.5"
                />

                {/* 4. Top Disc Surface Platform */}
                <ellipse cx="240" cy="42" rx="205" ry="38" fill="url(#pedTopSurface)" />

                {/* 5. Inner Inset Ring Edge */}
                <ellipse cx="240" cy="42" rx="204" ry="37" stroke="#080A0E" strokeWidth="2" fill="none" />

                {/* 6. Glowing Neon LED Ring (Outer Diffused Glow) */}
                <ellipse
                  cx="240"
                  cy="42"
                  rx="205"
                  ry="38"
                  stroke="rgba(255, 255, 255, 0.75)"
                  strokeWidth="4.5"
                  fill="none"
                  filter="url(#pureNeonGlow)"
                />

                {/* 7. Solid White Razor-Sharp Core Ring */}
                <ellipse
                  cx="240"
                  cy="42"
                  rx="205"
                  ry="38"
                  stroke="#FFFFFF"
                  strokeWidth="2.2"
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

            {/* Orbiting Telemetry Card 1: Top-Left Business Health Score */}
            <div className="telemetry-card card-pos-top-left">
              <div className="t-card-label">Business Health Score</div>
              <div className="t-card-metric-row">
                <span className="t-val-lg">82</span>
                <span className="t-val-sub">/100</span>
              </div>
              <div className="t-sparkline-wrap">
                <svg width="100%" height="20" viewBox="0 0 100 20" preserveAspectRatio="none">
                  <path d="M0,14 Q25,18 50,8 T100,5" fill="none" stroke="#FFFFFF" strokeWidth="1.8" />
                </svg>
              </div>
            </div>

            {/* Orbiting Telemetry Card 2: Top-Right Forecast Confidence */}
            <div className="telemetry-card card-pos-top-right">
              <div className="t-card-label">Forecast Confidence</div>
              <div className="t-forecast-row">
                <div>
                  <div className="t-val-lg">92%</div>
                  <div className="t-status-sub">High Confidence</div>
                </div>
                <div className="t-circle-gauge">
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
                      strokeDasharray="92, 100"
                    />
                  </svg>
                </div>
              </div>
            </div>

            {/* Orbiting Telemetry Card 3: Mid-Left Revenue Trend */}
            <div className="telemetry-card card-pos-mid-left">
              <div className="t-card-label">Revenue Trend</div>
              <div className="t-val-lg" style={{ color: '#FFFFFF' }}>+12%</div>
              <div className="t-status-sub">vs last period</div>
              <div className="t-mini-bars">
                <div className="bar" style={{ height: '40%' }} />
                <div className="bar" style={{ height: '60%' }} />
                <div className="bar" style={{ height: '35%' }} />
                <div className="bar" style={{ height: '80%' }} />
                <div className="bar" style={{ height: '100%' }} />
              </div>
            </div>

            {/* Orbiting Telemetry Card 4: Mid-Right Top Risk */}
            <div className="telemetry-card card-pos-mid-right">
              <div className="t-risk-header">
                <span className="t-card-label">Top Risk</span>
                <AlertTriangle size={12} className="t-risk-icon" />
              </div>
              <div className="t-risk-title">Customer Retention</div>
              <div className="t-risk-impact">High Impact</div>
            </div>

            {/* Orbiting Telemetry Card 5: Bottom-Right Recommended Action */}
            <div className="telemetry-card card-pos-bottom-right">
              <div className="t-card-label">Recommended Action</div>
              <div className="t-action-title">Win-Back Campaign</div>
              <div className="t-action-footer">
                <span>Priority: High</span>
                <ArrowUpRight size={13} style={{ color: '#FFFFFF' }} />
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* ======================================================================
          3. The Intelligence Pipeline Section
          ====================================================================== */}
      <section className="section-pipeline-wrap" id="intelligence">
        <div className="page-container">
          
          <div className="section-heading-center">
            <h2 className="section-title-main">The Intelligence Pipeline</h2>
            <p className="section-subtitle-main">
              A fully integrated analytical engine turning raw data into actionable executive decisions.
            </p>
          </div>

          <div className="pipeline-flow-row">
            
            {/* Step 1 */}
            <div className="flow-node">
              <div className="flow-icon-circle">
                <Database size={20} />
              </div>
              <div className="flow-title">Business Data</div>
              <div className="flow-sub">Collect & Integrate</div>
            </div>

            <div className="flow-arrow">→</div>

            {/* Step 2 */}
            <div className="flow-node">
              <div className="flow-icon-circle">
                <BarChart2 size={20} />
              </div>
              <div className="flow-title">KPIs</div>
              <div className="flow-sub">Measure Performance</div>
            </div>

            <div className="flow-arrow">→</div>

            {/* Step 3 */}
            <div className="flow-node">
              <div className="flow-icon-circle">
                <Search size={20} />
              </div>
              <div className="flow-title">Diagnostics</div>
              <div className="flow-sub">Detect Anomalies</div>
            </div>

            <div className="flow-arrow">→</div>

            {/* Step 4 */}
            <div className="flow-node">
              <div className="flow-icon-circle">
                <GitMerge size={20} />
              </div>
              <div className="flow-title">Root Causes</div>
              <div className="flow-sub">Find What Matters</div>
            </div>

            <div className="flow-arrow">→</div>

            {/* Step 5 */}
            <div className="flow-node">
              <div className="flow-icon-circle">
                <Target size={20} />
              </div>
              <div className="flow-title">Recommendations</div>
              <div className="flow-sub">Actionable Steps</div>
            </div>

            <div className="flow-arrow">→</div>

            {/* Step 6 */}
            <div className="flow-node">
              <div className="flow-icon-circle">
                <TrendingUp size={20} />
              </div>
              <div className="flow-title">Forecasts</div>
              <div className="flow-sub">Predict Outcomes</div>
            </div>

            <div className="flow-arrow">→</div>

            {/* Step 7 */}
            <div className="flow-node">
              <div className="flow-icon-circle">
                <FileText size={20} />
              </div>
              <div className="flow-title">Executive Intelligence</div>
              <div className="flow-sub">Strategic Insights</div>
            </div>

            <div className="flow-arrow">→</div>

            {/* Step 8 (DEX Highlight) */}
            <div className="flow-node flow-node-dex">
              <div className="flow-icon-circle flow-icon-dex">
                <Bot size={22} style={{ color: '#FFFFFF' }} />
              </div>
              <div className="flow-title" style={{ color: '#FFFFFF' }}>AI Analyst</div>
              <div className="flow-sub" style={{ color: '#E8E8E8', fontWeight: '600' }}>DEX</div>
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
