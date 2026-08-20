import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Database, 
  FileText, 
  PlayCircle, 
  Scale, 
  PieChart, 
  DollarSign, 
  ShieldAlert, 
  Bot, 
  Layers, 
  Key, 
  ShieldCheck, 
  Activity, 
  Sparkles, 
  ArrowRight,
  TrendingUp,
  Cpu,
  BookOpen
} from 'lucide-react';
import { MarketingNavbar } from '../../components/layout/MarketingNavbar';
import '../../styles/home.css';

export const PlatformShowcaseView: React.FC = () => {
  const modules = [
    {
      category: 'DATA & INGESTION',
      title: 'Enterprise Data Hub',
      desc: 'Universal CSV ingestion, automated column datatype inference, and live schema validation.',
      path: '/enterprise-data',
      icon: Database,
      badge: 'DATA HUB',
    },
    {
      category: 'DATA & INGESTION',
      title: 'KPI Dictionary & Lineage',
      desc: '32 deterministic metric formulas, mathematical provenance lineage, and verified owners.',
      path: '/kpi-dictionary',
      icon: BookOpen,
      badge: 'KPI DICTIONARY',
    },
    {
      category: 'EXECUTIVE & BOARD',
      title: 'Executive Boardroom',
      desc: 'Presentation-ready quarterly briefings, CEO sign-off ledger, and board report generation.',
      path: '/boardroom',
      icon: FileText,
      badge: 'BOARDROOM',
    },
    {
      category: 'EXECUTIVE & BOARD',
      title: 'AI Decision Copilot',
      desc: 'Institutional memory recall and explainable natural language decision queries.',
      path: '/decision-copilot',
      icon: Bot,
      badge: 'COPILOT',
    },
    {
      category: 'STRATEGY & SIMULATION',
      title: 'Digital Twin & Scenarios',
      desc: 'Dynamic enterprise simulation dials, stress-test forecasting, and Monte Carlo revenue modeling.',
      path: '/digital-twin',
      icon: PlayCircle,
      badge: 'DIGITAL TWIN',
    },
    {
      category: 'STRATEGY & SIMULATION',
      title: 'Strategy Execution & Value',
      desc: 'Strategic initiatives, target milestones, and quarterly value realization attribution.',
      path: '/strategy-execution',
      icon: Activity,
      badge: 'STRATEGY',
    },
    {
      category: 'PORTFOLIO & CAPITAL',
      title: 'Multi-Portfolio Rollup',
      desc: 'Hierarchical multi-entity explorer from Global Group to Region, Division, and BU.',
      path: '/portfolio-rollup',
      icon: Layers,
      badge: 'PORTFOLIO',
    },
    {
      category: 'PORTFOLIO & CAPITAL',
      title: 'Capital Allocation Studio',
      desc: 'Mathematical ROI curve optimization and $1M capital budget deployment simulator.',
      path: '/capital-allocation',
      icon: DollarSign,
      badge: 'CAPITAL',
    },
    {
      category: 'GOVERNANCE & TRUST',
      title: 'Decision Governance Registry',
      desc: 'Immutable decision registry, pre-execution policy rules, and cryptographic audit hashes.',
      path: '/governance',
      icon: Scale,
      badge: 'GOVERNANCE',
    },
    {
      category: 'GOVERNANCE & TRUST',
      title: 'Risk Concentration Radar',
      desc: 'Customer ARR and geographic revenue concentration risk detector with automated triggers.',
      path: '/risk-concentration',
      icon: ShieldAlert,
      badge: 'RISK RADAR',
    },
    {
      category: 'AUTONOMOUS & INFRA',
      title: 'Autonomous Agents Hub',
      desc: '6 specialized agents collaborating in a multi-agent Directed Acyclic Graph (DAG).',
      path: '/agents',
      icon: Cpu,
      badge: 'AGENTS',
    },
    {
      category: 'AUTONOMOUS & INFRA',
      title: 'Enterprise API Platform',
      desc: 'Developer REST gateway, rate limits, API keys, and automated OpenAPI documentation.',
      path: '/api-platform',
      icon: Key,
      badge: 'API GATEWAY',
    },
  ];

  return (
    <div className="home-root" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#000000' }}>
      
      {/* Top Navbar */}
      <MarketingNavbar activeTab="platform" />

      {/* Main Showcase Grid */}
      <main
        style={{
          flex: 1,
          paddingTop: '80px',
          paddingBottom: '80px',
          backgroundImage: 'radial-gradient(circle at 50% 0%, rgba(255, 255, 255, 0.05) 0%, transparent 65%)',
        }}
      >
        <div className="page-container" style={{ maxWidth: '1280px', margin: '0 auto', padding: '0 28px', display: 'flex', flexDirection: 'column', gap: '28px' }}>
          
          {/* Header with Subtle Connected Enterprise Architecture Blueprint */}
          <div style={{ position: 'relative', textAlign: 'center', maxWidth: '880px', margin: '0 auto', width: '100%', padding: '10px 0 0 0' }}>
            
            {/* Subtle Radial Cyan Intelligence Glow & Core Beacon ◉ */}
            <div
              style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                width: '640px',
                height: '240px',
                pointerEvents: 'none',
                zIndex: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
              aria-hidden="true"
            >
              {/* Soft Ambient Cyan Intelligence Radial Glow */}
              <div
                style={{
                  position: 'absolute',
                  width: '520px',
                  height: '200px',
                  borderRadius: '50%',
                  background: 'radial-gradient(ellipse at center, rgba(56, 189, 248, 0.12) 0%, rgba(56, 189, 248, 0.03) 45%, transparent 72%)',
                  filter: 'blur(32px)',
                }}
              />

              {/* Central Intelligence Core Beacon ◉ */}
              <div
                style={{
                  position: 'absolute',
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  border: '1px solid rgba(56, 189, 248, 0.22)',
                  background: 'radial-gradient(circle, rgba(56, 189, 248, 0.14) 0%, transparent 70%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 0 24px rgba(56, 189, 248, 0.2)',
                  opacity: 0.65,
                }}
              >
                <div
                  style={{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    background: '#38BDF8',
                    boxShadow: '0 0 10px #38BDF8',
                  }}
                />
              </div>
            </div>

            {/* Foreground Content */}
            <div style={{ position: 'relative', zIndex: 1 }}>
              <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  background: 'rgba(255, 255, 255, 0.04)',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  color: '#C5CCD6',
                  borderRadius: '9999px',
                  padding: '4px 14px',
                  fontSize: '11px',
                  fontWeight: 700,
                  letterSpacing: '0.12em',
                  textTransform: 'uppercase',
                  marginBottom: '10px',
                }}
              >
                <Sparkles size={13} color="#FFFFFF" />
                <span>ENTERPRISE OPERATING SYSTEM CAPABILITIES</span>
              </div>

              <h1 style={{ fontSize: '2.8rem', fontWeight: 900, color: '#FFFFFF', letterSpacing: '-0.03em', margin: '0 0 8px 0', lineHeight: 1.15 }}>
                The Full DecisionOS Platform
              </h1>

              <p style={{ color: '#8E99A8', fontSize: '1rem', lineHeight: 1.55, margin: 0 }}>
                Explore every connected module powering the world's most advanced deterministic executive intelligence platform.
              </p>
            </div>
          </div>

          {/* Module Cards Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '18px' }}>
            {modules.map((mod, i) => {
              const IconComponent = mod.icon;

              return (
                <Link
                  key={i}
                  to={mod.path}
                  style={{
                    background: '#080A0E',
                    border: '1px solid #161A22',
                    borderRadius: '14px',
                    padding: '24px',
                    textDecoration: 'none',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    gap: '16px',
                    boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
                    transition: 'all 0.2s ease',
                    position: 'relative',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = '#2D333F';
                    e.currentTarget.style.background = '#0C0F14';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 12px 30px rgba(0, 0, 0, 0.8)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = '#161A22';
                    e.currentTarget.style.background = '#080A0E';
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 4px 20px rgba(0,0,0,0.5)';
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
                      <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: '#11141B', border: '1px solid #1E232E', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#FFFFFF' }}>
                        <IconComponent size={19} />
                      </div>
                      <span style={{ fontSize: '0.66rem', fontWeight: 700, padding: '3px 8px', borderRadius: '4px', background: '#0F172A', color: '#CBD5E1', border: '1px solid #334155', letterSpacing: '0.06em' }}>
                        {mod.badge}
                      </span>
                    </div>

                    <div style={{ fontSize: '0.72rem', color: '#616B78', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '4px' }}>
                      {mod.category}
                    </div>

                    <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#FFFFFF', letterSpacing: '-0.02em', marginBottom: '6px' }}>
                      {mod.title}
                    </div>

                    <p style={{ color: '#8E99A8', fontSize: '0.86rem', lineHeight: 1.5, margin: 0 }}>
                      {mod.desc}
                    </p>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem', fontWeight: 700, color: '#E2E8F0', paddingTop: '12px', borderTop: '1px solid #14171E' }}>
                    <span>Launch Module</span>
                    <ArrowRight size={14} />
                  </div>
                </Link>
              );
            })}
          </div>

          {/* Bottom Callout */}
          <div
            style={{
              padding: '32px',
              borderRadius: '16px',
              background: 'linear-gradient(135deg, #090C12 0%, #040508 100%)',
              border: '1px solid #1E232F',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '20px',
            }}
          >
            <div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#FFFFFF' }}>
                Ready to experience the unified operating system?
              </div>
              <div style={{ color: '#8E99A8', fontSize: '0.88rem', marginTop: '3px' }}>
                Jump directly into the Enterprise Command Center with live telemetry and scenario digital twins.
              </div>
            </div>

            <Link
              to="/enterprise"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 24px',
                background: '#FFFFFF',
                color: '#000000',
                borderRadius: '24px',
                fontWeight: 700,
                fontSize: '0.9rem',
                textDecoration: 'none',
                boxShadow: '0 2px 10px rgba(255, 255, 255, 0.15)',
                transition: 'all 0.2s ease',
              }}
            >
              <span>Launch Platform</span>
              <ArrowRight size={16} />
            </Link>
          </div>

        </div>
      </main>

      {/* Footer */}
      <footer className="site-footer">
        <div className="page-container footer-flex" style={{ maxWidth: '1280px', margin: '0 auto', padding: '0 28px' }}>
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

export default PlatformShowcaseView;

