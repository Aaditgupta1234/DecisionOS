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
  ShieldAlert
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
            DecisionOS
          </Link>

          <div className="nav-links">
            <a href="#pipeline" className="nav-link">Platform</a>
            <a href="#overview" className="nav-link">Intelligence</a>
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
          2. Hero Section (2-Column Layout)
          ====================================================================== */}
      <section className="hero-wrapper">
        <div className="page-container hero-grid">
          
          {/* Left Hero Column */}
          <div>
            <div className="hero-badge">
              AI-NATIVE BUSINESS INTELLIGENCE
            </div>

            <h1 className="hero-title">
              Know What’s<br />
              Happening.<br />
              Understand Why.<br />
              Decide What Comes<br />
              Next.
            </h1>

            <p className="hero-desc">
              DecisionOS transforms business data into explainable intelligence through KPI analysis, diagnostics, root cause discovery, forecasting, and AI-powered executive insights.
            </p>

            <div className="hero-btn-group">
              <Link to="/dashboard" className="btn-start-analysis">
                <span>Start Analysis</span>
                <ArrowRight size={16} />
              </Link>
              <a href="#pipeline" className="btn-watch-demo">
                <span>Watch Demo</span>
                <div style={{ width: '18px', height: '18px', borderRadius: '50%', background: '#ffffff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Play size={10} style={{ fill: '#000000', color: '#000000', marginLeft: '1px' }} />
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
                  <Bot size={13} style={{ color: '#8e8e93' }} />
                  <span>AI Analyst</span>
                </div>
              </div>
            </div>
          </div>

          {/* Right Hero Stage with Spotlight & Floating Cards */}
          <div className="hero-stage">
            
            {/* Overhead Spotlight */}
            <div className="hero-spotlight" />

            {/* 3D Glowing Circular Pedestal Platform */}
            <div className="stage-pedestal">
              <div className="pedestal-disc" />
            </div>

            {/* 6 Structured Floating Cards */}
            <div className="stage-cards-layout">
              
              {/* 1. Business Health Score */}
              <div className="stage-card card-business-health">
                <div style={{ fontSize: '11px', color: '#8e8e93', marginBottom: '4px' }}>
                  Business Health Score
                </div>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: '3px' }}>
                  <span style={{ fontSize: '20px', fontWeight: '700', color: '#ffffff' }}>82</span>
                  <span style={{ fontSize: '11px', color: '#52525b' }}>/ 100</span>
                </div>
                {/* Mini SVG sparkline */}
                <div style={{ marginTop: '8px', height: '14px', width: '100%' }}>
                  <svg width="100%" height="100%" viewBox="0 0 80 14" preserveAspectRatio="none">
                    <path d="M0,10 Q20,12 40,6 T80,4" fill="none" stroke="#71717a" strokeWidth="1.5" />
                  </svg>
                </div>
              </div>

              {/* 2. Forecast Confidence */}
              <div className="stage-card card-forecast-conf">
                <div style={{ fontSize: '11px', color: '#8e8e93', marginBottom: '4px' }}>
                  Forecast Confidence
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ fontSize: '20px', fontWeight: '700', color: '#ffffff' }}>92%</div>
                    <div style={{ fontSize: '10px', color: '#71717a', marginTop: '2px' }}>High Confidence</div>
                  </div>
                  {/* Gauge ring */}
                  <div style={{ width: '28px', height: '28px', borderRadius: '50%', border: '2.5px solid rgba(255,255,255,0.15)', borderTopColor: '#ffffff', display: 'flex', alignItems: 'center', justifyContent: 'center' }} />
                </div>
              </div>

              {/* 3. Revenue Trend */}
              <div className="stage-card card-revenue-trend">
                <div style={{ fontSize: '11px', color: '#8e8e93', marginBottom: '2px' }}>
                  Revenue Trend
                </div>
                <div style={{ fontSize: '18px', fontWeight: '700', color: '#ffffff' }}>
                  +12%
                </div>
                <div style={{ fontSize: '10px', color: '#71717a', marginBottom: '8px' }}>
                  vs last period
                </div>
                {/* Mini bar chart */}
                <div style={{ display: 'flex', alignItems: 'flex-end', gap: '3px', height: '14px' }}>
                  <div style={{ width: '6px', height: '6px', background: '#3f3f46', borderRadius: '1px' }} />
                  <div style={{ width: '6px', height: '9px', background: '#3f3f46', borderRadius: '1px' }} />
                  <div style={{ width: '6px', height: '5px', background: '#3f3f46', borderRadius: '1px' }} />
                  <div style={{ width: '6px', height: '11px', background: '#3f3f46', borderRadius: '1px' }} />
                  <div style={{ width: '6px', height: '14px', background: '#ffffff', borderRadius: '1px' }} />
                </div>
              </div>

              {/* 4. Center AI Analyst DEX Card */}
              <div className="stage-card card-dex-center">
                <div style={{ width: '48px', height: '48px', borderRadius: '10px', background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 10px' }}>
                  <Bot size={26} style={{ color: '#ffffff' }} />
                </div>
                <div style={{ fontSize: '11px', color: '#8e8e93', marginBottom: '2px' }}>
                  DecisionOS AI Analyst
                </div>
                <div style={{ fontSize: '24px', fontWeight: '800', color: '#ffffff', letterSpacing: '-0.02em', marginBottom: '4px' }}>
                  DEX
                </div>
                <div style={{ fontSize: '10px', color: '#71717a' }}>
                  Your Executive Intelligence Partner
                </div>
              </div>

              {/* 5. Top Risk */}
              <div className="stage-card card-top-risk">
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '11px', color: '#8e8e93', marginBottom: '2px' }}>
                  <span>Top Risk</span>
                  <AlertTriangle size={12} style={{ color: '#71717a' }} />
                </div>
                <div style={{ fontSize: '13px', fontWeight: '700', color: '#ffffff', marginTop: '2px' }}>
                  Customer Retention
                </div>
                <div style={{ fontSize: '10px', color: '#71717a', marginTop: '3px' }}>
                  High Impact
                </div>
              </div>

              {/* 6. Recommended Action */}
              <div className="stage-card card-recommended-action">
                <div style={{ fontSize: '11px', color: '#8e8e93', marginBottom: '2px' }}>
                  Recommended Action
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ fontSize: '13px', fontWeight: '700', color: '#ffffff' }}>
                    Win-Back Campaign
                  </div>
                  <ArrowUpRight size={14} style={{ color: '#8e8e93' }} />
                </div>
                <div style={{ fontSize: '10px', color: '#71717a', marginTop: '3px' }}>
                  Priority: High
                </div>
              </div>

            </div>

          </div>

        </div>
      </section>

      {/* ======================================================================
          3. Section: The Intelligence Pipeline
          ====================================================================== */}
      <section id="pipeline" className="section-pipeline">
        <div className="page-container">
          
          <div className="section-header-center">
            <h2 className="section-title-lg">
              The Intelligence Pipeline
            </h2>
            <p className="section-subtitle-sm">
              A fully integrated analytical engine turning raw data into actionable executive decisions.
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
              <div className="pipeline-step-name">Executive Intelligence</div>
              <div className="pipeline-step-sub">Strategic Insights</div>
            </div>

            <div className="pipeline-arrow">→</div>

            {/* Step 8 (DEX Highlight) */}
            <div className="pipeline-step-card dex-highlight">
              <div className="pipeline-icon-box" style={{ background: 'rgba(255,255,255,0.12)' }}>
                <Bot size={18} />
              </div>
              <div className="pipeline-step-name">AI Analyst</div>
              <div className="pipeline-step-sub" style={{ color: '#ffffff', fontWeight: '600' }}>DEX</div>
            </div>

          </div>

        </div>
      </section>

      {/* ======================================================================
          4. Section: Executive Intelligence Overview (Dashboard Preview)
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
                  <div style={{ width: '32px', height: '32px', borderRadius: '50%', border: '3px solid rgba(255,255,255,0.15)', borderTopColor: '#ffffff' }} />
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
                      stroke="#8e8e93" 
                      strokeWidth="2" 
                    />
                    <circle cx="320" cy="15" r="3.5" fill="#ffffff" />
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

                <div style={{ fontSize: '24px', fontWeight: '800', color: '#ffffff', marginBottom: '2px' }}>
                  $4.8M
                </div>
                <div style={{ fontSize: '11px', color: '#8e8e93', marginBottom: '10px' }}>
                  +9.6% growth
                </div>

                <div style={{ height: '80px', width: '100%' }}>
                  <svg width="100%" height="100%" viewBox="0 0 320 60" preserveAspectRatio="none">
                    <path 
                      d="M0,50 Q80,40 160,25 T320,10" 
                      fill="none" 
                      stroke="#ffffff" 
                      strokeWidth="2" 
                    />
                    <circle cx="0" cy="50" r="3" fill="#ffffff" />
                    <circle cx="106" cy="35" r="3" fill="#ffffff" />
                    <circle cx="213" cy="20" r="3" fill="#ffffff" />
                    <circle cx="320" cy="10" r="3" fill="#ffffff" />
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
                  <div style={{ fontSize: '12px', fontWeight: '700', color: '#ffffff', marginBottom: '2px' }}>Customer Retention Decline</div>
                  <div style={{ fontSize: '10px', color: '#a1a1aa', marginBottom: '6px' }}>Impact: High</div>
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
          5. Section: Turn Data Into Decisions (CTA Card)
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
                className="btn-watch-demo"
                style={{ cursor: 'pointer' }}
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
        <div className="page-container footer-inner">
          <div>
            <span className="footer-brand">DecisionOS</span>
            <span style={{ marginLeft: '16px' }}>© 2025 DecisionOS. All rights reserved.</span>
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
