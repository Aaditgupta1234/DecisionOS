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
  Cpu, 
  AlertTriangle, 
  Sparkles,
  ArrowUpRight,
  ShieldCheck,
  CheckCircle2,
  Layers
} from 'lucide-react';
import '../../styles/home.css';

export const HomeView: React.FC = () => {
  return (
    <div className="page-root">
      
      {/* ======================================================================
          1. Top Navigation Bar (Linear / Palantir / Stripe aesthetic)
          ====================================================================== */}
      <nav className="top-nav">
        <div className="page-container top-nav-inner">
          <Link to="/" className="nav-brand">
            <div className="nav-brand-emblem">
              <Cpu size={15} color="#030406" />
            </div>
            <span>DecisionOS</span>
          </Link>

          <div className="nav-links">
            <a href="#why-fail" className="nav-link">Platform</a>
            <a href="#pipeline" className="nav-link">Intelligence</a>
            <a href="#overview" className="nav-link">Solutions</a>
            <a href="#resources" className="nav-link">Resources</a>
            <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="nav-link">Docs</a>
          </div>

          <Link to="/dashboard" className="btn-nav-access">
            Access Platform
          </Link>
        </div>
      </nav>

      {/* ======================================================================
          2. Hero Section (Strict 2-Column Composition)
          ====================================================================== */}
      <section className="hero-wrapper">
        <div className="page-container hero-grid">
          
          {/* LEFT COLUMN (45%): Executive Positioning & Story */}
          <div>
            <div className="hero-badge">
              EXECUTIVE BUSINESS ASSISTANT
            </div>

            <h1 className="hero-title">
              Know What’s<br />
              Happening.<br />
              Understand Why.<br />
              Decide What Comes<br />
              Next.
            </h1>

            {/* Differentiator Value Proposition */}
            <div className="hero-value-prop">
              Most platforms tell you what happened.<br />
              <strong>DecisionOS determines why it happened and calculates what to do next.</strong>
            </div>

            <p className="hero-desc">
              DecisionOS transforms business data into explainable intelligence through KPI evaluation, causal root-cause discovery, forecasting, and prioritized executive interventions.
            </p>

            <div className="hero-btn-group">
              <Link to="/dashboard" className="btn-start-analysis">
                <span>Start Analysis</span>
                <ArrowRight size={16} />
              </Link>
              <a href="#why-fail" className="btn-explore-flow">
                <span>Explore Decision Flow</span>
                <div style={{ width: '18px', height: '18px', borderRadius: '50%', background: '#ffffff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Play size={10} style={{ fill: '#030406', color: '#030406', marginLeft: '1px' }} />
                </div>
              </a>
            </div>

            <div className="hero-trust-bar">
              <div className="trust-title">
                TRUSTED BY ANALYTICAL LEADERS
              </div>
              <div className="trust-items">
                <div className="trust-item">
                  <BarChart2 size={13} style={{ color: '#8e8e93' }} />
                  <span>KPI Intelligence</span>
                </div>
                <div className="trust-item">
                  <GitMerge size={13} style={{ color: '#8e8e93' }} />
                  <span>Root Cause Analysis</span>
                </div>
                <div className="trust-item">
                  <TrendingUp size={13} style={{ color: '#8e8e93' }} />
                  <span>Forecasting Engine</span>
                </div>
                <div className="trust-item">
                  <Cpu size={13} style={{ color: '#8e8e93' }} />
                  <span>DEX Partner</span>
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN (55%): Vertical Axis (Spotlight -> DEX -> Pedestal) */}
          <div className="hero-stage">
            
            {/* 1. Overhead Spotlight Beam */}
            <div className="hero-spotlight" />

            {/* 2. 3D Illuminated Circular Pedestal Platform Beneath DEX */}
            <div className="stage-pedestal">
              <div className="pedestal-disc" />
            </div>

            {/* 3. Central Dominant DEX + 4 Symmetrical Telemetry Cards */}
            <div className="stage-cards-layout">
              
              {/* TOP-LEFT: Business Health Score */}
              <div className="stage-card card-business-health">
                <div style={{ fontSize: '11px', color: '#8e8e93', marginBottom: '4px' }}>
                  Business Health Score
                </div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '3px' }}>
                  <span style={{ fontSize: '22px', fontWeight: '800', color: '#ffffff' }}>82</span>
                  <span style={{ fontSize: '11px', color: '#52525b' }}>/ 100</span>
                </div>
                <div style={{ marginTop: '8px', height: '14px', width: '100%' }}>
                  <svg width="100%" height="100%" viewBox="0 0 80 14" preserveAspectRatio="none">
                    <path d="M0,10 Q20,12 40,6 T80,4" fill="none" stroke="#34d399" strokeWidth="1.5" />
                  </svg>
                </div>
              </div>

              {/* TOP-RIGHT: Forecast Confidence */}
              <div className="stage-card card-forecast-conf">
                <div style={{ fontSize: '11px', color: '#8e8e93', marginBottom: '4px' }}>
                  Forecast Confidence
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ fontSize: '22px', fontWeight: '800', color: '#ffffff' }}>92%</div>
                    <div style={{ fontSize: '10px', color: '#38bdf8', marginTop: '2px' }}>High Confidence</div>
                  </div>
                  <div style={{ width: '28px', height: '28px', borderRadius: '50%', border: '2.5px solid rgba(255,255,255,0.15)', borderTopColor: '#38bdf8', display: 'flex', alignItems: 'center', justifyContent: 'center' }} />
                </div>
              </div>

              {/* CENTERPIECE: Visually Dominant DEX Intelligence Partner */}
              <div className="card-dex-center">
                {/* Interactive 3D Spline Robot */}
                <div className="dex-spline-container">
                  <iframe 
                    src="https://my.spline.design/genkubgreetingrobot-5exzcKZ24el7lb1Perqf1bkP/" 
                    className="dex-spline-iframe"
                    title="DEX 3D Interactive Robot"
                  />
                </div>

                <div style={{ fontSize: '11px', fontFamily: 'monospace', letterSpacing: '0.12em', color: '#60a5fa', textTransform: 'uppercase', fontWeight: '700', marginBottom: '3px' }}>
                  Executive Intelligence Core
                </div>
                <div style={{ fontSize: '26px', fontWeight: '800', color: '#ffffff', letterSpacing: '-0.03em', marginBottom: '2px' }}>
                  DEX
                </div>
                <div style={{ fontSize: '12px', color: '#e5e7eb', fontWeight: '600' }}>
                  DecisionOS Executive Analyst
                </div>
                <div style={{ fontSize: '11px', color: '#9ca3af', marginTop: '3px' }}>
                  Your Executive Intelligence Partner
                </div>
                <div style={{ marginTop: '14px', paddingTop: '10px', borderTop: '1px solid rgba(255,255,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px', fontSize: '11px', fontFamily: 'monospace', color: '#34d399' }}>
                  <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#34d399', boxShadow: '0 0 6px #34d399' }} />
                  <span>Interactive 3D Core Active</span>
                </div>
              </div>

              {/* BOTTOM-LEFT: Top Operational Risk */}
              <div className="stage-card card-top-risk">
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '11px', color: '#8e8e93', marginBottom: '2px' }}>
                  <span>Top Operational Risk</span>
                  <AlertTriangle size={12} style={{ color: '#fbbf24' }} />
                </div>
                <div style={{ fontSize: '14px', fontWeight: '700', color: '#ffffff', marginTop: '2px' }}>
                  Customer Retention
                </div>
                <div style={{ fontSize: '10px', color: '#fbbf24', marginTop: '3px' }}>
                  ● High Revenue Exposure
                </div>
              </div>

              {/* BOTTOM-RIGHT: Recommended Action */}
              <div className="stage-card card-recommended-action">
                <div style={{ fontSize: '11px', color: '#8e8e93', marginBottom: '2px' }}>
                  Recommended Action
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ fontSize: '14px', fontWeight: '700', color: '#ffffff' }}>
                    Win-Back Campaign
                  </div>
                  <ArrowUpRight size={14} style={{ color: '#34d399' }} />
                </div>
                <div style={{ fontSize: '10px', color: '#34d399', marginTop: '3px' }}>
                  Priority: High Intervention
                </div>
              </div>

            </div>

          </div>

        </div>
      </section>

      {/* ======================================================================
          3. Section: Why Traditional Dashboards Fail (The 3-Way Differentiator)
          ====================================================================== */}
      <section id="why-fail" className="section-differentiator">
        <div className="page-container">
          
          <div className="section-header-center">
            <h2 className="section-title-lg">
              Why Traditional Dashboards Fail
            </h2>
            <p className="section-subtitle-sm">
              Most platforms report metrics. DecisionOS determines why things happen and calculates what to do next.
            </p>
          </div>

          <div className="differentiator-grid">
            
            {/* Card 1: Traditional Dashboard */}
            <div className="diff-card">
              <div>
                <div className="diff-tag">Legacy Approach</div>
                <h3 className="diff-title">Traditional Dashboard</h3>
                <p className="diff-desc">
                  Displays raw metrics and retroactive charts. Forces executives to manually guess what is happening across disparate data silos.
                </p>
              </div>
              <div className="diff-outcome" style={{ color: '#71717a' }}>
                → Reports Metrics: <span style={{ color: '#ffffff' }}>"Revenue dropped 18%"</span>
              </div>
            </div>

            {/* Card 2: BI Platform */}
            <div className="diff-card">
              <div>
                <div className="diff-tag">Analytical Approach</div>
                <h3 className="diff-title">BI Platform</h3>
                <p className="diff-desc">
                  Visualizes longitudinal trends and multi-dimensional slices, but leaves causality and root-cause analysis completely unresolved.
                </p>
              </div>
              <div className="diff-outcome" style={{ color: '#9ca3af' }}>
                → Reports Trends: <span style={{ color: '#ffffff' }}>"4-Quarter Decline Pattern"</span>
              </div>
            </div>

            {/* Card 3: DecisionOS */}
            <div className="diff-card active-diff">
              <div>
                <div className="diff-tag" style={{ color: '#60a5fa' }}>Executive Business Assistant</div>
                <h3 className="diff-title">DecisionOS</h3>
                <p className="diff-desc">
                  Continuously traces causal DAGs, isolates root causes from symptom noise, and calculates prioritized, risk-discounted executive interventions.
                </p>
              </div>
              <div className="diff-outcome" style={{ color: '#34d399' }}>
                → Drives Decisions: <span style={{ color: '#ffffff' }}>"Root Cause: ERP Sync $\to$ Deploy Fleet Pods (P1)"</span>
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* ======================================================================
          4. Section: The Intelligence Pipeline
          ====================================================================== */}
      <section id="pipeline" className="section-pipeline">
        <div className="page-container">
          
          <div className="section-header-center">
            <h2 className="section-title-lg">
              The Intelligence Pipeline
            </h2>
            <p className="section-subtitle-sm">
              A fully integrated deterministic engine turning raw telemetry into auditable executive decisions.
            </p>
          </div>

          <div className="pipeline-flex-row">
            
            {/* Step 1 */}
            <div className="pipeline-step-card">
              <div className="pipeline-icon-box">
                <Database size={18} />
              </div>
              <div className="pipeline-step-name">Business Data</div>
              <div className="pipeline-step-sub">Collect & Integrate</div>
            </div>

            <div className="pipeline-arrow">→</div>

            {/* Step 2 */}
            <div className="pipeline-step-card">
              <div className="pipeline-icon-box">
                <BarChart2 size={18} />
              </div>
              <div className="pipeline-step-name">KPIs</div>
              <div className="pipeline-step-sub">Measure Performance</div>
            </div>

            <div className="pipeline-arrow">→</div>

            {/* Step 3 */}
            <div className="pipeline-step-card">
              <div className="pipeline-icon-box">
                <Search size={18} />
              </div>
              <div className="pipeline-step-name">Diagnostics</div>
              <div className="pipeline-step-sub">Detect Anomalies</div>
            </div>

            <div className="pipeline-arrow">→</div>

            {/* Step 4 */}
            <div className="pipeline-step-card">
              <div className="pipeline-icon-box">
                <GitMerge size={18} />
              </div>
              <div className="pipeline-step-name">Root Causes</div>
              <div className="pipeline-step-sub">Find What Matters</div>
            </div>

            <div className="pipeline-arrow">→</div>

            {/* Step 5 */}
            <div className="pipeline-step-card">
              <div className="pipeline-icon-box">
                <Target size={18} />
              </div>
              <div className="pipeline-step-name">Recommendations</div>
              <div className="pipeline-step-sub">Actionable Steps</div>
            </div>

            <div className="pipeline-arrow">→</div>

            {/* Step 6 */}
            <div className="pipeline-step-card">
              <div className="pipeline-icon-box">
                <TrendingUp size={18} />
              </div>
              <div className="pipeline-step-name">Forecasts</div>
              <div className="pipeline-step-sub">Predict Outcomes</div>
            </div>

            <div className="pipeline-arrow">→</div>

            {/* Step 7 */}
            <div className="pipeline-step-card">
              <div className="pipeline-icon-box">
                <FileText size={18} />
              </div>
              <div className="pipeline-step-name">Executive Intel</div>
              <div className="pipeline-step-sub">Strategic Insights</div>
            </div>

            <div className="pipeline-arrow">→</div>

            {/* Step 8 (DEX Core Highlight) */}
            <div className="pipeline-step-card dex-highlight">
              <div className="pipeline-icon-box" style={{ background: 'rgba(46, 144, 255, 0.2)' }}>
                <Cpu size={18} style={{ color: '#2e90ff' }} />
              </div>
              <div className="pipeline-step-name" style={{ color: '#60a5fa' }}>DEX Core</div>
              <div className="pipeline-step-sub" style={{ color: '#ffffff', fontWeight: '600' }}>Executive Partner</div>
            </div>

          </div>

        </div>
      </section>

      {/* ======================================================================
          5. Section: Executive Intelligence Overview (Command Center Preview)
          ====================================================================== */}
      <section id="overview" className="section-dashboard">
        <div className="page-container">
          
          <div className="section-header-center">
            <h2 className="section-title-lg">
              Executive Intelligence Overview
            </h2>
            <p className="section-subtitle-sm">
              A real-time command center for data-driven leaders.
            </p>
          </div>

          <div className="dashboard-panel-container">
            
            {/* Top 4 KPI Metric Cards */}
            <div className="kpi-row-4cols">
              
              <div className="kpi-stat-box">
                <div className="kpi-stat-header">Total Revenue</div>
                <div className="kpi-stat-value">$4.2M</div>
                <div className="kpi-stat-delta">+12.4% vs last period</div>
              </div>

              <div className="kpi-stat-box">
                <div className="kpi-stat-header">Orders</div>
                <div className="kpi-stat-value">18,530</div>
                <div className="kpi-stat-delta">+8.7% vs last period ↗</div>
              </div>

              <div className="kpi-stat-box">
                <div className="kpi-stat-header">Customers</div>
                <div className="kpi-stat-value">6,842</div>
                <div className="kpi-stat-delta">+11.3% vs last period ↗</div>
              </div>

              <div className="kpi-stat-box">
                <div className="kpi-stat-header">Business Health Score</div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <div className="kpi-stat-value">82 <span style={{ fontSize: '13px', color: '#71717a' }}>/ 100</span></div>
                    <div style={{ fontSize: '11px', color: '#8e8e93', marginTop: '4px' }}>Good Performance</div>
                  </div>
                  <div style={{ width: '32px', height: '32px', borderRadius: '50%', border: '3px solid rgba(255,255,255,0.15)', borderTopColor: '#34d399' }} />
                </div>
              </div>

            </div>

            {/* Main Grid: Revenue Trend + Forecast Curve + Right Panel */}
            <div className="dash-main-grid">
              
              {/* Left Chart: Revenue Trend */}
              <div className="dash-chart-card">
                <div className="chart-header">
                  <div>
                    <div className="chart-title">Revenue Trend</div>
                    <div className="chart-subtitle">✓ Last 12 Months</div>
                  </div>
                  <div className="chart-value-tag">$4.2M <span style={{ fontSize: '10px', color: '#71717a' }}>Dec 2024</span></div>
                </div>

                <div style={{ height: '140px', width: '100%', paddingTop: '10px' }}>
                  <svg width="100%" height="100%" viewBox="0 0 320 90" preserveAspectRatio="none">
                    <path 
                      d="M0,75 Q30,70 60,65 T120,55 T180,45 T240,30 T320,15" 
                      fill="none" 
                      stroke="#2e90ff" 
                      strokeWidth="2" 
                    />
                    <circle cx="320" cy="15" r="3.5" fill="#2e90ff" />
                  </svg>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '9px', color: '#52525b', fontFamily: 'monospace', marginTop: '8px', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '6px' }}>
                  <span>Jan</span><span>Feb</span><span>Mar</span><span>Apr</span><span>May</span><span>Jun</span><span>Jul</span><span>Aug</span><span>Sep</span><span>Oct</span><span>Nov</span><span>Dec</span>
                </div>
              </div>

              {/* Middle Chart: Forecast (Next 3 Months) */}
              <div className="dash-chart-card">
                <div className="chart-header">
                  <div>
                    <div className="chart-title">Forecast (Next 3 Months)</div>
                    <div className="chart-subtitle">Projected Revenue</div>
                  </div>
                </div>

                <div style={{ fontSize: '26px', fontWeight: '800', color: '#ffffff', marginBottom: '2px' }}>
                  $4.8M
                </div>
                <div style={{ fontSize: '11px', color: '#34d399', marginBottom: '10px' }}>
                  +9.6% forward growth
                </div>

                <div style={{ height: '80px', width: '100%' }}>
                  <svg width="100%" height="100%" viewBox="0 0 320 60" preserveAspectRatio="none">
                    <path 
                      d="M0,50 Q80,40 160,25 T320,10" 
                      fill="none" 
                      stroke="#34d399" 
                      strokeWidth="2" 
                    />
                    <circle cx="0" cy="50" r="3" fill="#34d399" />
                    <circle cx="106" cy="35" r="3" fill="#34d399" />
                    <circle cx="213" cy="20" r="3" fill="#34d399" />
                    <circle cx="320" cy="10" r="3" fill="#34d399" />
                  </svg>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '9px', color: '#52525b', fontFamily: 'monospace', marginTop: '6px', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '6px' }}>
                  <span>Dec</span><span>Jan</span><span>Feb</span><span>Mar</span>
                </div>
              </div>

              {/* Right Stack: Executive Summary & Top Root Cause */}
              <div className="dash-side-stack">
                
                {/* Executive Summary */}
                <div className="side-info-card">
                  <div className="side-info-title">Executive Summary</div>
                  <p className="side-info-text">
                    Revenue increased 12.4% driven by higher AOV and returning customers. However, customer retention declined 4.3% due to increased churn in the last 30 days.
                  </p>
                  <Link to="/reports" className="btn-card-action">
                    View Full Report
                  </Link>
                </div>

                {/* Top Root Cause */}
                <div className="side-info-card">
                  <div style={{ fontSize: '10px', color: '#71717a', textTransform: 'uppercase', marginBottom: '2px' }}>Top Root Cause</div>
                  <div style={{ fontSize: '13px', fontWeight: '700', color: '#ffffff', marginBottom: '2px' }}>Customer Retention Decline</div>
                  <div style={{ fontSize: '10px', color: '#fbbf24', marginBottom: '6px' }}>Impact: High Exposure</div>
                  <p className="side-info-text">
                    Analysis shows churn increased due to late deliveries and reduced engagement in the last 30 days.
                  </p>
                  <Link to="/root-causes" className="btn-card-action">
                    Explore Root Cause
                  </Link>
                </div>

              </div>

            </div>

          </div>

        </div>
      </section>

      {/* ======================================================================
          6. Section: Turn Data Into Decisions (CTA Card)
          ====================================================================== */}
      <section className="section-cta">
        <div className="page-container">
          
          <div className="cta-banner-card">
            
            <div className="cta-left-content">
              <Sparkles className="cta-sparkle-icon" />
              <div>
                <h3 className="cta-heading">Turn Data Into Decisions</h3>
                <p className="cta-subtext">
                  Understand performance, uncover root causes, forecast outcomes, and make smarter decisions with DecisionOS.
                </p>
              </div>
            </div>

            <div className="cta-button-group">
              <Link to="/dashboard" className="btn-start-analysis">
                <span>Start Analysis</span>
                <ArrowRight size={15} />
              </Link>
              <button 
                onClick={() => alert("Demo request logged. Our enterprise team will reach out promptly.")}
                className="btn-explore-flow"
                style={{ cursor: 'pointer' }}
              >
                <span>Request Demo</span>
              </button>
            </div>

          </div>

        </div>
      </section>

      {/* ======================================================================
          7. Footer
          ====================================================================== */}
      <footer className="site-footer">
        <div className="page-container footer-inner">
          <div>
            <span className="footer-brand">DecisionOS</span>
            <span style={{ marginLeft: '16px' }}>© 2026 DecisionOS. All rights reserved.</span>
          </div>

          <div className="footer-links-row">
            <span className="footer-link">Privacy Policy</span>
            <span className="footer-link">Terms of Service</span>
            <span className="footer-link">Security</span>
            <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="footer-link">API Documentation</a>
            <span className="footer-link">System Status</span>
          </div>
        </div>
      </footer>

    </div>
  );
};

export default HomeView;
