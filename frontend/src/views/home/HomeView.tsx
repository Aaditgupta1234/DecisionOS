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
  Check
} from 'lucide-react';
import '../../styles/home.css';

export const HomeView: React.FC = () => {
  return (
    <div className="page-root">
      
      {/* ======================================================================
          1. Top Navigation Bar (Command Center Navigation)
          ====================================================================== */}
      <nav className="top-nav">
        <div className="page-container top-nav-inner">
          <Link to="/" className="nav-brand">
            <div className="nav-brand-emblem">
              <Cpu size={14} color="#FFFFFF" />
            </div>
            <span>DecisionOS</span>
          </Link>

          <div className="nav-links">
            <a href="#why-exists" className="nav-link">Platform</a>
            <a href="#pipeline" className="nav-link">Intelligence</a>
            <a href="#overview" className="nav-link">Capabilities</a>
            <a href="#scale" className="nav-link">Architecture</a>
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
          
          {/* LEFT COLUMN (46%): Executive Positioning & Story */}
          <div className="hero-left-column">
            <div className="hero-badge">
              EXECUTIVE BUSINESS ASSISTANT
            </div>

            <h1 className="hero-headline">
              Know What’s Happening.<br />
              Understand Why.<br />
              Decide What Comes Next.
            </h1>

            {/* Differentiator Value Proposition Block */}
            <div className="hero-value-prop">
              Most platforms tell you what happened.
              <strong>DecisionOS determines why it happened and calculates what to do next.</strong>
            </div>

            <p className="hero-desc">
              DecisionOS transforms business data into explainable intelligence through deterministic KPI evaluation, causal root-cause discovery, forecasting, and prioritized executive interventions.
            </p>

            <div className="hero-btn-group">
              <Link to="/dashboard" className="btn-start-analysis">
                <span>Start Analysis</span>
                <ArrowRight size={15} />
              </Link>
              <a href="#why-exists" className="btn-explore-flow">
                <span>Explore Decision Flow</span>
                <div style={{ width: '18px', height: '18px', borderRadius: '50%', background: '#FFFFFF', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Play size={10} style={{ fill: '#060709', color: '#060709', marginLeft: '1px' }} />
                </div>
              </a>
            </div>

            {/* Enterprise Trust Strip (Recruiter Gold) */}
            <div className="hero-trust-bar">
              <div className="trust-items-row">
                <div className="trust-item">
                  <span className="trust-dot">●</span>
                  <span>783+ Tests</span>
                </div>
                <div className="trust-item">
                  <span className="trust-dot">●</span>
                  <span>100+ APIs</span>
                </div>
                <div className="trust-item">
                  <span className="trust-dot">●</span>
                  <span>25+ Engines</span>
                </div>
                <div className="trust-item">
                  <span className="trust-dot">●</span>
                  <span>Deterministic</span>
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN (54%): Vertical Axis (Spotlight -> DEX -> Pedestal) */}
          <div className="hero-stage">
            
            {/* 1. Overhead White-Gray Spotlight Beam (18% Opacity) */}
            <div className="hero-spotlight" />

            {/* 2. 3D Metallic Graphite Pedestal Platform (500px) */}
            <div className="stage-pedestal">
              <div className="pedestal-disc" />
            </div>

            {/* 3. Central Standalone 3D Spline Robot + Symmetrical Telemetry Grid */}
            <div className="stage-cards-layout">
              
              {/* TOP-LEFT: Business Health Score */}
              <div className="stage-card card-business-health">
                <div style={{ fontSize: '11px', color: '#B5BAC4', marginBottom: '4px' }}>
                  Business Health Score
                </div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '3px' }}>
                  <span style={{ fontSize: '22px', fontWeight: '800', color: '#FFFFFF' }}>82</span>
                  <span style={{ fontSize: '11px', color: '#727A86' }}>/ 100</span>
                </div>
                <div style={{ marginTop: '8px', height: '14px', width: '100%' }}>
                  <svg width="100%" height="100%" viewBox="0 0 80 14" preserveAspectRatio="none">
                    <path d="M0,10 Q20,12 40,6 T80,4" fill="none" stroke="#B5BAC4" strokeWidth="1.5" />
                  </svg>
                </div>
              </div>

              {/* TOP-RIGHT: Forecast Confidence */}
              <div className="stage-card card-forecast-conf">
                <div style={{ fontSize: '11px', color: '#B5BAC4', marginBottom: '4px' }}>
                  Forecast Confidence
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ fontSize: '22px', fontWeight: '800', color: '#FFFFFF' }}>92%</div>
                    <div style={{ fontSize: '10px', color: '#B5BAC4', marginTop: '2px' }}>High Confidence</div>
                  </div>
                  <div style={{ width: '26px', height: '26px', borderRadius: '50%', border: '2px solid rgba(255,255,255,0.15)', borderTopColor: '#FFFFFF', display: 'flex', alignItems: 'center', justifyContent: 'center' }} />
                </div>
              </div>

              {/* CENTERPIECE: Dominant Standalone 3D Spline Robot on Pedestal */}
              <div className="dex-bot-standalone">
                <iframe 
                  src="https://my.spline.design/genkubgreetingrobot-5exzcKZ24el7lb1Perqf1bkP/" 
                  className="dex-spline-iframe"
                  title="DEX 3D Interactive Robot"
                />
              </div>

              {/* BOTTOM-LEFT: Top Operational Risk */}
              <div className="stage-card card-top-risk">
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '11px', color: '#B5BAC4', marginBottom: '2px' }}>
                  <span>Top Operational Risk</span>
                  <AlertTriangle size={12} style={{ color: '#E8E8E8' }} />
                </div>
                <div style={{ fontSize: '14px', fontWeight: '700', color: '#FFFFFF', marginTop: '2px' }}>
                  Customer Retention
                </div>
                <div style={{ fontSize: '10px', color: '#727A86', marginTop: '3px' }}>
                  ● High Revenue Exposure
                </div>
              </div>

              {/* BOTTOM-RIGHT: Recommended Action */}
              <div className="stage-card card-recommended-action">
                <div style={{ fontSize: '11px', color: '#B5BAC4', marginBottom: '2px' }}>
                  Recommended Action
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ fontSize: '14px', fontWeight: '700', color: '#FFFFFF' }}>
                    Win-Back Campaign
                  </div>
                  <ArrowUpRight size={14} style={{ color: '#FFFFFF' }} />
                </div>
                <div style={{ fontSize: '10px', color: '#B5BAC4', marginTop: '3px' }}>
                  Priority: High Intervention
                </div>
              </div>

            </div>

          </div>

        </div>
      </section>

      {/* ======================================================================
          3. Section: Why DecisionOS Exists (The Core Identity)
          ====================================================================== */}
      <section id="why-exists" className="section-identity">
        <div className="page-container">
          
          <div className="identity-header-block">
            <h2 className="identity-section-title">
              Why DecisionOS Exists
            </h2>
            <p className="identity-lead-text">
              Most business platforms stop at reporting. They tell executives what happened.<br />
              DecisionOS was built to answer the questions that matter:
            </p>
            <div className="identity-three-questions">
              <span>• What changed?</span>
              <span>• Why did it change?</span>
              <span>• What should we do next?</span>
            </div>
            <p className="identity-sub-statement">
              Every score, recommendation, forecast, and intervention is fully traceable through deterministic business logic.
            </p>
          </div>

          <div className="differentiator-grid">
            
            {/* Pillar 1: Traditional Dashboard */}
            <div className="diff-card">
              <div>
                <div className="diff-tag">Legacy Approach</div>
                <h3 className="diff-title">Traditional Dashboard</h3>
                <p className="diff-desc">
                  Displays raw metrics and retroactive charts. Forces executives to manually guess what is happening across disparate data silos.
                </p>
              </div>
              <div className="diff-outcome" style={{ color: '#727A86' }}>
                → Reports Metrics: <span style={{ color: '#FFFFFF' }}>"Revenue dropped 18%"</span>
              </div>
            </div>

            {/* Pillar 2: BI Platform */}
            <div className="diff-card">
              <div>
                <div className="diff-tag">Analytical Approach</div>
                <h3 className="diff-title">BI Platform</h3>
                <p className="diff-desc">
                  Visualizes longitudinal trends and multi-dimensional slices, but leaves causality and root-cause analysis completely unresolved.
                </p>
              </div>
              <div className="diff-outcome" style={{ color: '#B5BAC4' }}>
                → Reports Trends: <span style={{ color: '#FFFFFF' }}>"4-Quarter Decline Pattern"</span>
              </div>
            </div>

            {/* Pillar 3: DecisionOS */}
            <div className="diff-card active-diff">
              <div>
                <div className="diff-tag" style={{ color: '#FFFFFF' }}>Executive Operating System</div>
                <h3 className="diff-title">DecisionOS</h3>
                <p className="diff-desc">
                  Continuously traces causal DAGs, isolates root causes from symptom noise, and calculates prioritized, risk-discounted executive interventions.
                </p>
              </div>
              <div className="diff-outcome" style={{ color: '#FFFFFF' }}>
                → Guides Decisions: <span style={{ color: '#E8E8E8' }}>"Root Cause: ERP Sync $\to$ Deploy Fleet Pods (P1)"</span>
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
              <div className="pipeline-icon-box" style={{ background: '#1A1E26' }}>
                <Cpu size={18} style={{ color: '#FFFFFF' }} />
              </div>
              <div className="pipeline-step-name" style={{ color: '#FFFFFF' }}>DEX Core</div>
              <div className="pipeline-step-sub" style={{ color: '#E8E8E8', fontWeight: '600' }}>Executive Partner</div>
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
                    <div className="kpi-stat-value">82 <span style={{ fontSize: '13px', color: '#727A86' }}>/ 100</span></div>
                    <div style={{ fontSize: '11px', color: '#B5BAC4', marginTop: '4px' }}>Good Performance</div>
                  </div>
                  <div style={{ width: '28px', height: '28px', borderRadius: '50%', border: '2.5px solid rgba(255,255,255,0.15)', borderTopColor: '#FFFFFF' }} />
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
                  <div className="chart-value-tag">$4.2M <span style={{ fontSize: '10px', color: '#727A86' }}>Dec 2024</span></div>
                </div>

                <div style={{ height: '140px', width: '100%', paddingTop: '10px' }}>
                  <svg width="100%" height="100%" viewBox="0 0 320 90" preserveAspectRatio="none">
                    <path 
                      d="M0,75 Q30,70 60,65 T120,55 T180,45 T240,30 T320,15" 
                      fill="none" 
                      stroke="#FFFFFF" 
                      strokeWidth="2" 
                    />
                    <circle cx="320" cy="15" r="3.5" fill="#FFFFFF" />
                  </svg>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '9px', color: '#727A86', fontFamily: 'monospace', marginTop: '8px', borderTop: '1px solid #22262E', paddingTop: '6px' }}>
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

                <div style={{ fontSize: '26px', fontWeight: '800', color: '#FFFFFF', marginBottom: '2px' }}>
                  $4.8M
                </div>
                <div style={{ fontSize: '11px', color: '#B5BAC4', marginBottom: '10px' }}>
                  +9.6% forward growth
                </div>

                <div style={{ height: '80px', width: '100%' }}>
                  <svg width="100%" height="100%" viewBox="0 0 320 60" preserveAspectRatio="none">
                    <path 
                      d="M0,50 Q80,40 160,25 T320,10" 
                      fill="none" 
                      stroke="#FFFFFF" 
                      strokeWidth="2" 
                    />
                    <circle cx="0" cy="50" r="3" fill="#FFFFFF" />
                    <circle cx="106" cy="35" r="3" fill="#FFFFFF" />
                    <circle cx="213" cy="20" r="3" fill="#FFFFFF" />
                    <circle cx="320" cy="10" r="3" fill="#FFFFFF" />
                  </svg>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '9px', color: '#727A86', fontFamily: 'monospace', marginTop: '6px', borderTop: '1px solid #22262E', paddingTop: '6px' }}>
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
                  <div style={{ fontSize: '10px', color: '#727A86', textTransform: 'uppercase', marginBottom: '2px' }}>Top Root Cause</div>
                  <div style={{ fontSize: '13px', fontWeight: '700', color: '#FFFFFF', marginBottom: '2px' }}>Customer Retention Decline</div>
                  <div style={{ fontSize: '10px', color: '#B5BAC4', marginBottom: '6px' }}>Impact: High Exposure</div>
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
          6. Section: Enterprise System Scale (Recruiter Metrics Grid)
          ====================================================================== */}
      <section id="scale" className="section-scale">
        <div className="page-container">
          
          <div className="section-header-center">
            <h2 className="section-title-lg">
              Enterprise System Scale
            </h2>
            <p className="section-subtitle-sm">
              Engineered with enterprise rigor, multi-tenant isolation, and complete deterministic auditability.
            </p>
          </div>

          <div className="scale-metric-grid">
            
            <div className="scale-card">
              <div className="scale-value-huge">783+</div>
              <div className="scale-label-title">Automated Tests</div>
              <div className="scale-sub-desc">100% Pass Rate (Unit, Integration & API)</div>
            </div>

            <div className="scale-card">
              <div className="scale-value-huge">100+</div>
              <div className="scale-label-title">REST APIs</div>
              <div className="scale-sub-desc">High-Concurrency Asynchronous FastAPI</div>
            </div>

            <div className="scale-card">
              <div className="scale-value-huge">25+</div>
              <div className="scale-label-title">Intelligence Engines</div>
              <div className="scale-sub-desc">Deterministic Mathematical Analytics</div>
            </div>

            <div className="scale-card">
              <div className="scale-value-huge">40+</div>
              <div className="scale-label-title">Domain Models</div>
              <div className="scale-sub-desc">SQLAlchemy 2.0 Normalized Architecture</div>
            </div>

            <div className="scale-card">
              <div className="scale-value-huge">Phases 0–13</div>
              <div className="scale-label-title">Delivered Architecture</div>
              <div className="scale-sub-desc">Production Governance & Operational Monitoring</div>
            </div>

            <div className="scale-card">
              <div className="scale-value-huge">100%</div>
              <div className="scale-label-title">Deterministic Intelligence</div>
              <div className="scale-sub-desc">Zero AI Hallucination or Calculation Drift</div>
            </div>

          </div>

        </div>
      </section>

      {/* ======================================================================
          7. Section: Turn Data Into Decisions (CTA Banner)
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
          8. Footer
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
