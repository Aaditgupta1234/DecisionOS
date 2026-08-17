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
  Check,
  Layers,
  Activity,
  Workflow
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
              DETERMINISTIC EXECUTIVE INTELLIGENCE
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
              DecisionOS transforms business telemetry into explainable intelligence through deterministic KPI evaluation, causal root-cause discovery, forecasting, and prioritized executive interventions.
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

            <div className="hero-traceability-subtext">
              No LLM hallucinations. 100% deterministic decision logic.
            </div>

            {/* Recruiter Trust Strip (Gold Standard) */}
            <div className="hero-trust-bar">
              <div className="trust-items-row">
                <div className="trust-item">
                  <span className="trust-dot">●</span>
                  <span>783+ Tests</span>
                </div>
                <div className="trust-item">
                  <span className="trust-dot">●</span>
                  <span>100+ REST APIs</span>
                </div>
                <div className="trust-item">
                  <span className="trust-dot">●</span>
                  <span>25+ Engines</span>
                </div>
                <div className="trust-item">
                  <span className="trust-dot">●</span>
                  <span>40+ Models</span>
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
            
            {/* 1. Overhead White-Gray Spotlight Beam (16% Opacity) */}
            <div className="hero-spotlight" />

            {/* 2. 3D Metallic Graphite Pedestal Platform (560px) */}
            <div className="stage-pedestal">
              <div className="pedestal-disc" />
            </div>

            {/* 3. Central Standalone 3D Spline Robot + Symmetrical Telemetry Grid */}
            <div className="stage-cards-layout">
              
              {/* TOP-LEFT: Business Health Score */}
              <div className="stage-card card-business-health">
                <div style={{ fontSize: '11px', color: '#B5BAC4', marginBottom: '2px' }}>
                  Business Health Score
                </div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '3px' }}>
                  <span className="metric-value-huge">82</span>
                  <span style={{ fontSize: '13px', color: '#727A86' }}>/ 100</span>
                </div>
                <div style={{ marginTop: '6px', height: '14px', width: '100%' }}>
                  <svg width="100%" height="100%" viewBox="0 0 80 14" preserveAspectRatio="none">
                    <path d="M0,10 Q20,12 40,6 T80,4" fill="none" stroke="#B5BAC4" strokeWidth="1.5" />
                  </svg>
                </div>
              </div>

              {/* TOP-RIGHT: Forecast Confidence */}
              <div className="stage-card card-forecast-conf">
                <div style={{ fontSize: '11px', color: '#B5BAC4', marginBottom: '2px' }}>
                  Forecast Confidence
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <div className="metric-value-huge">92%</div>
                    <div style={{ fontSize: '10px', color: '#B5BAC4', marginTop: '3px' }}>High Confidence</div>
                  </div>
                  <div style={{ width: '28px', height: '28px', borderRadius: '50%', border: '2px solid rgba(255,255,255,0.15)', borderTopColor: '#FFFFFF', display: 'flex', alignItems: 'center', justifyContent: 'center' }} />
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
                <div style={{ fontSize: '15px', fontWeight: '700', color: '#FFFFFF', marginTop: '2px' }}>
                  Customer Retention
                </div>
                <div style={{ fontSize: '10px', color: '#727A86', marginTop: '3px' }}>
                  ● -4.3% Revenue Drag
                </div>
              </div>

              {/* BOTTOM-RIGHT: Recommended Action */}
              <div className="stage-card card-recommended-action">
                <div style={{ fontSize: '11px', color: '#B5BAC4', marginBottom: '2px' }}>
                  Recommended Action
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ fontSize: '15px', fontWeight: '700', color: '#FFFFFF' }}>
                    Win-Back Campaign
                  </div>
                  <ArrowUpRight size={14} style={{ color: '#FFFFFF' }} />
                </div>
                <div style={{ fontSize: '10px', color: '#B5BAC4', marginTop: '3px' }}>
                  Impact: +$320k Recovery
                </div>
              </div>

            </div>

          </div>

        </div>
      </section>

      {/* ======================================================================
          3. Section: Why DecisionOS Exists (The Core Identity Showdown)
          ====================================================================== */}
      <section id="why-exists" className="section-identity">
        <div className="page-container">
          
          <div className="identity-header-block">
            <h2 className="identity-section-title">
              Why DecisionOS Exists
            </h2>
            <p className="identity-lead-text">
              Most business analytics platforms stop at reporting. They tell executives what happened.<br />
              DecisionOS was built to answer the questions that determine business survival:
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
                  Displays raw retroactive charts and static numbers. Forces leadership to manually guess root causes across fragmented silos.
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
                  Visualizes longitudinal trends and multi-dimensional slices, but leaves causal drivers and actionable solutions unresolved.
                </p>
              </div>
              <div className="diff-outcome" style={{ color: '#B5BAC4' }}>
                → Reports Trends: <span style={{ color: '#FFFFFF' }}>"4-Quarter Decline Pattern"</span>
              </div>
            </div>

            {/* Pillar 3: DecisionOS */}
            <div className="diff-card active-diff">
              <div>
                <div className="diff-tag" style={{ color: '#FFFFFF' }}>Executive Decision OS</div>
                <h3 className="diff-title">DecisionOS</h3>
                <p className="diff-desc">
                  Continuously traces causal DAGs, isolates root causes from symptom noise, and calculates prioritized, risk-discounted executive interventions.
                </p>
              </div>
              <div className="diff-outcome" style={{ color: '#FFFFFF' }}>
                → Guides Decisions: <span style={{ color: '#E8E8E8' }}>"Root Cause: ERP Sync $\to$ Win-Back Campaign (+$320k)"</span>
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* ======================================================================
          4. Section: The Signature Intelligence Pipeline (Visual Moat)
          ====================================================================== */}
      <section id="pipeline" className="section-pipeline">
        <div className="page-container">
          
          <div className="section-header-center">
            <h2 className="section-title-lg">
              The Signature Intelligence Pipeline
            </h2>
            <p className="section-subtitle-sm">
              An 8-stage deterministic operating system transforming raw enterprise telemetry into audited executive decisions.
            </p>
          </div>

          <div className="pipeline-flex-row">
            
            {/* Step 01 */}
            <div className="pipeline-step-card">
              <div className="pipeline-step-num">01</div>
              <div className="pipeline-icon-box">
                <Database size={18} />
              </div>
              <div className="pipeline-step-name">Business Data</div>
              <div className="pipeline-step-sub">ERP, SQL & CSV Ingestion</div>
              <div className="pipeline-latency-tag">&lt; 14ms</div>
            </div>

            <div className="pipeline-arrow">→</div>

            {/* Step 02 */}
            <div className="pipeline-step-card">
              <div className="pipeline-step-num">02</div>
              <div className="pipeline-icon-box">
                <BarChart2 size={18} />
              </div>
              <div className="pipeline-step-name">KPI Engine</div>
              <div className="pipeline-step-sub">Health & Variance Scoring</div>
              <div className="pipeline-latency-tag">82/100</div>
            </div>

            <div className="pipeline-arrow">→</div>

            {/* Step 03 */}
            <div className="pipeline-step-card">
              <div className="pipeline-icon-box">
                <Search size={18} />
              </div>
              <div className="pipeline-step-name">Diagnostics</div>
              <div className="pipeline-step-sub">Statistical Anomalies</div>
              <div className="pipeline-latency-tag">Z-Score 2.4</div>
            </div>

            <div className="pipeline-arrow">→</div>

            {/* Step 04 */}
            <div className="pipeline-step-card">
              <div className="pipeline-step-num">04</div>
              <div className="pipeline-icon-box">
                <GitMerge size={18} />
              </div>
              <div className="pipeline-step-name">Root Causes</div>
              <div className="pipeline-step-sub">Causal DAG Discovery</div>
              <div className="pipeline-latency-tag">94% Conf.</div>
            </div>

            <div className="pipeline-arrow">→</div>

            {/* Step 05 */}
            <div className="pipeline-step-card">
              <div className="pipeline-step-num">05</div>
              <div className="pipeline-icon-box">
                <Target size={18} />
              </div>
              <div className="pipeline-step-name">Interventions</div>
              <div className="pipeline-step-sub">ROI Ranked Actions</div>
              <div className="pipeline-latency-tag">P1 Priority</div>
            </div>

            <div className="pipeline-arrow">→</div>

            {/* Step 06 */}
            <div className="pipeline-step-card">
              <div className="pipeline-step-num">06</div>
              <div className="pipeline-icon-box">
                <TrendingUp size={18} />
              </div>
              <div className="pipeline-step-name">Forecasting</div>
              <div className="pipeline-step-sub">3-Month Forward Curves</div>
              <div className="pipeline-latency-tag">+9.6% Growth</div>
            </div>

            <div className="pipeline-arrow">→</div>

            {/* Step 07 */}
            <div className="pipeline-step-card">
              <div className="pipeline-step-num">07</div>
              <div className="pipeline-icon-box">
                <FileText size={18} />
              </div>
              <div className="pipeline-step-name">Executive Intel</div>
              <div className="pipeline-step-sub">Board Syntheses</div>
              <div className="pipeline-latency-tag">Audited</div>
            </div>

            <div className="pipeline-arrow">→</div>

            {/* Step 08 (DEX Core Highlight) */}
            <div className="pipeline-step-card dex-highlight">
              <div className="pipeline-step-num" style={{ color: '#FFFFFF' }}>08</div>
              <div className="pipeline-icon-box" style={{ background: '#1A1E26' }}>
                <Cpu size={18} style={{ color: '#FFFFFF' }} />
              </div>
              <div className="pipeline-step-name" style={{ color: '#FFFFFF' }}>DEX Core</div>
              <div className="pipeline-step-sub" style={{ color: '#E8E8E8', fontWeight: '600' }}>Decision Partner</div>
              <div className="pipeline-latency-tag" style={{ background: 'rgba(255,255,255,0.15)', color: '#FFFFFF' }}>Active</div>
            </div>

          </div>

        </div>
      </section>

      {/* ======================================================================
          5. Section: Executive Intelligence Overview (Real Causal Cockpit)
          ====================================================================== */}
      <section id="overview" className="section-dashboard">
        <div className="page-container">
          
          <div className="section-header-center">
            <h2 className="section-title-lg">
              Executive Command Center Preview
            </h2>
            <p className="section-subtitle-sm">
              Traceable relationships from top-level metric shifts down to isolated causal drivers and calculated ROI recovery.
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
                <div className="kpi-stat-header">Orders Completed</div>
                <div className="kpi-stat-value">18,530</div>
                <div className="kpi-stat-delta">+8.7% vs last period ↗</div>
              </div>

              <div className="kpi-stat-box">
                <div className="kpi-stat-header">Active Customers</div>
                <div className="kpi-stat-value">6,842</div>
                <div className="kpi-stat-delta">+11.3% vs last period ↗</div>
              </div>

              <div className="kpi-stat-box">
                <div className="kpi-stat-header">Business Health Score</div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <div className="kpi-stat-value">82 <span style={{ fontSize: '13px', color: '#727A86' }}>/ 100</span></div>
                    <div style={{ fontSize: '11px', color: '#B5BAC4', marginTop: '4px' }}>Optimal Performance</div>
                  </div>
                  <div style={{ width: '28px', height: '28px', borderRadius: '50%', border: '2.5px solid rgba(255,255,255,0.15)', borderTopColor: '#FFFFFF' }} />
                </div>
              </div>

            </div>

            {/* Main Grid: Revenue Trajectory + Forecast Projection + Right Causal Stack */}
            <div className="dash-main-grid">
              
              {/* Left Chart: Revenue Trend */}
              <div className="dash-chart-card">
                <div className="chart-header">
                  <div>
                    <div className="chart-title">Revenue Trajectory</div>
                    <div className="chart-subtitle">✓ 12-Month Audited Curve</div>
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
                    <div className="chart-title">Forward Projection</div>
                    <div className="chart-subtitle">92% Confidence Horizon</div>
                  </div>
                </div>

                <div style={{ fontSize: '26px', fontWeight: '800', color: '#FFFFFF', marginBottom: '2px' }}>
                  $4.8M
                </div>
                <div style={{ fontSize: '11px', color: '#B5BAC4', marginBottom: '10px' }}>
                  +9.6% forward projection
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

              {/* Right Stack: Causal Driver & ROI Recovery Plan */}
              <div className="dash-side-stack">
                
                {/* Isolated Root Cause */}
                <div className="side-info-card">
                  <div style={{ fontSize: '10px', color: '#727A86', textTransform: 'uppercase', marginBottom: '2px', fontFamily: 'monospace' }}>
                    Isolated Root Cause
                  </div>
                  <div style={{ fontSize: '14px', fontWeight: '700', color: '#FFFFFF', marginBottom: '2px' }}>
                    Retention Churn Drag (-4.3%)
                  </div>
                  <div style={{ fontSize: '11px', color: '#B5BAC4', marginBottom: '6px' }}>
                    Primary Driver: Fulfillment Latency & ERP Sync
                  </div>
                  <p className="side-info-text">
                    Algorithmic causal DAG isolated fulfillment delays causing 72% of recent retention drop.
                  </p>
                  <Link to="/root-causes" className="btn-card-action">
                    Explore Causal Graph
                  </Link>
                </div>

                {/* Priority Intervention Plan */}
                <div className="side-info-card">
                  <div style={{ fontSize: '10px', color: '#727A86', textTransform: 'uppercase', marginBottom: '2px', fontFamily: 'monospace' }}>
                    Calculated Intervention (P1)
                  </div>
                  <div style={{ fontSize: '14px', fontWeight: '700', color: '#FFFFFF', marginBottom: '2px' }}>
                    Win-Back Retention Campaign
                  </div>
                  <div style={{ fontSize: '11px', color: '#34D399', fontWeight: '600', marginBottom: '8px' }}>
                    Projected Recovery: +$320,000 ARR
                  </div>
                  <Link to="/recommendations" className="btn-card-action">
                    Deploy Intervention Plan
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
              <div className="scale-sub-desc">Zero LLM Hallucinations or Calculation Drift</div>
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
                  Understand performance, uncover causal root causes, forecast outcomes, and execute verified leadership interventions.
                </p>
                <div className="cta-guarantee-tag">
                  ✓ No LLM hallucinations · 100% deterministic decision logic · Fully auditable
                </div>
              </div>
            </div>

            <div className="cta-button-group">
              <Link to="/dashboard" className="btn-start-analysis">
                <span>Start Analysis</span>
                <ArrowRight size={15} />
              </Link>
              <button 
                onClick={() => alert("Enterprise briefing scheduled. Our engineering team will contact you directly.")}
                className="btn-explore-flow"
                style={{ cursor: 'pointer' }}
              >
                <span>Request Briefing</span>
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
