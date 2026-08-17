import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ArrowRight, 
  Play, 
  Activity, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle2, 
  Cpu, 
  BarChart3, 
  GitMerge, 
  ShieldCheck
} from 'lucide-react';

export const HeroCommandStage: React.FC = () => {
  return (
    <section className="hero-section-wrapper">
      
      <div className="hero-2col-layout">
        
        {/* ====================================================================
            LEFT COLUMN (44%): Messaging, Tagline & Action CTAs
            ==================================================================== */}
        <div className="hero-left-column">
          
          {/* Pill Badge */}
          <div className="hero-badge-pill">
            <Cpu className="w-3.5 h-3.5" style={{ color: '#2e90ff' }} />
            <span>Executive Business Assistant</span>
          </div>

          {/* Tagline Headline */}
          <h1 className="hero-headline">
            Know What’s Happening.<br />
            Understand Why.<br />
            Decide What Comes Next.
          </h1>

          {/* Description Paragraph */}
          <p className="hero-description">
            DecisionOS transforms business data into deterministic intelligence through KPI analysis, diagnostics, causal root cause discovery, forecasting, and explainable executive insights.
          </p>

          {/* Primary Action Buttons */}
          <div className="hero-cta-group">
            <Link to="/dashboard" className="btn-primary-hero">
              <span>Start Analysis</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <a href="#pipeline" className="btn-secondary-hero">
              <Play className="w-3.5 h-3.5" style={{ fill: '#ffffff' }} />
              <span>Watch Demo</span>
            </a>
          </div>

          {/* Trust Strip */}
          <div className="hero-trust-strip">
            <div className="trust-label">
              Trusted by Analytical Leaders
            </div>
            <div className="trust-badges-grid">
              <div className="trust-badge-item">
                <BarChart3 className="w-3.5 h-3.5" style={{ color: '#2e90ff' }} />
                <span>KPI Intelligence</span>
              </div>
              <div className="trust-badge-item">
                <GitMerge className="w-3.5 h-3.5" style={{ color: '#4edea3' }} />
                <span>Root Cause Analysis</span>
              </div>
              <div className="trust-badge-item">
                <TrendingUp className="w-3.5 h-3.5" style={{ color: '#c084fc' }} />
                <span>Forecasting</span>
              </div>
              <div className="trust-badge-item">
                <Cpu className="w-3.5 h-3.5" style={{ color: '#38bdf8' }} />
                <span>DEX Partner</span>
              </div>
            </div>
          </div>

        </div>

        {/* ====================================================================
            RIGHT COLUMN (56%): Dedicated Cinematic DEX Command Center Scene
            ==================================================================== */}
        <div className="hero-right-scene">
          
          <div className="dex-stage-wrapper">
            
            {/* 1. Single Overhead Spotlight Beam Centered on DEX */}
            <div className="stage-spotlight-beam" />

            {/* 2. Large Illuminated Circular Command Platform Beneath DEX */}
            <div className="stage-circular-platform">
              <div className="platform-outer-ring" />
              <div className="platform-core-glow" />
            </div>

            {/* 3. Symmetrical 3-Column Radial Grid (6 Intelligence Cards Around DEX) */}
            <div className="scene-layout-grid">
              
              {/* LEFT STACK (3 Cards) */}
              <div className="scene-left-stack">
                
                {/* 1. Business Health Score */}
                <div className="intelligence-card">
                  <div className="card-header-row">
                    <span>Business Health Score</span>
                    <Activity className="w-3.5 h-3.5" style={{ color: '#4edea3' }} />
                  </div>
                  <div className="card-value-lg">
                    82 <span style={{ fontSize: '11px', color: '#6b7280' }}>/ 100</span>
                  </div>
                  <div className="card-substatus" style={{ color: '#4edea3' }}>
                    ● Stable Performance
                  </div>
                </div>

                {/* 2. Revenue Growth */}
                <div className="intelligence-card">
                  <div className="card-header-row">
                    <span>Revenue Trend</span>
                    <TrendingUp className="w-3.5 h-3.5" style={{ color: '#2e90ff' }} />
                  </div>
                  <div className="card-value-lg">
                    +12%
                  </div>
                  <div className="card-substatus" style={{ color: '#9ca3af' }}>
                    vs. last period
                  </div>
                </div>

                {/* 3. Operational Health */}
                <div className="intelligence-card">
                  <div className="card-header-row">
                    <span>Operational Health</span>
                    <ShieldCheck className="w-3.5 h-3.5" style={{ color: '#38bdf8' }} />
                  </div>
                  <div className="card-value-lg">
                    91 <span style={{ fontSize: '11px', color: '#6b7280' }}>/ 100</span>
                  </div>
                  <div className="card-substatus" style={{ color: '#38bdf8' }}>
                    ● 783/783 Probes Green
                  </div>
                </div>

              </div>

              {/* CENTER: Visually Dominant DEX Card */}
              <div className="dex-centerpiece-card">
                <div className="dex-halo-avatar">
                  <Cpu className="w-8 h-8" style={{ color: '#ffffff' }} />
                </div>
                <div className="dex-tag-badge">
                  Executive Analyst
                </div>
                <h2 className="dex-title-name">
                  DEX
                </h2>
                <div className="dex-sub-desc">
                  DecisionOS Executive Analyst
                </div>
                <div className="dex-partner-label">
                  Your Executive Intelligence Partner
                </div>
                <div className="dex-status-pill">
                  <span className="pulse-dot" />
                  <span>Telemetry Active</span>
                </div>
              </div>

              {/* RIGHT STACK (3 Cards) */}
              <div className="scene-right-stack">
                
                {/* 4. Forecast Confidence */}
                <div className="intelligence-card">
                  <div className="card-header-row">
                    <span>Forecast Confidence</span>
                    <CheckCircle2 className="w-3.5 h-3.5" style={{ color: '#2e90ff' }} />
                  </div>
                  <div className="card-value-lg">
                    92%
                  </div>
                  <div className="card-substatus" style={{ color: '#2e90ff' }}>
                    High Confidence
                  </div>
                </div>

                {/* 5. Top Risk */}
                <div className="intelligence-card">
                  <div className="card-header-row">
                    <span>Top Risk</span>
                    <AlertTriangle className="w-3.5 h-3.5" style={{ color: '#fbbf24' }} />
                  </div>
                  <div style={{ fontSize: '14px', fontWeight: '700', color: '#ffffff', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    Customer Retention
                  </div>
                  <div className="card-substatus" style={{ color: '#fbbf24' }}>
                    High Revenue Impact
                  </div>
                </div>

                {/* 6. Recommended Action */}
                <div className="intelligence-card">
                  <div className="card-header-row">
                    <span>Recommended Action</span>
                    <TrendingUp className="w-3.5 h-3.5" style={{ color: '#4edea3' }} />
                  </div>
                  <div style={{ fontSize: '14px', fontWeight: '700', color: '#ffffff', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    Win-Back Campaign
                  </div>
                  <div className="card-substatus" style={{ color: '#4edea3' }}>
                    Priority: High
                  </div>
                </div>

              </div>

            </div>

          </div>

        </div>

      </div>

    </section>
  );
};
