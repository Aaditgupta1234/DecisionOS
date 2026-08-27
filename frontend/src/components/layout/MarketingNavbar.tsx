import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../features/auth/AuthContext';
import { 
  User, 
  LogOut, 
  ChevronDown, 
  LayoutDashboard, 
  Database, 
  Shield, 
  Sparkles, 
  PlayCircle, 
  Scale, 
  DollarSign, 
  ShieldAlert, 
  Bot, 
  Key, 
  Layers, 
  Activity, 
  BookOpen, 
  FileText,
  Cpu,
  ArrowRight,
  MessageSquare
} from 'lucide-react';
import '../../styles/home.css';

interface MarketingNavbarProps {
  activeTab?: string;
}

export const MarketingNavbar: React.FC<MarketingNavbarProps> = ({ activeTab }) => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0);
  const [isScrolling, setIsScrolling] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isMegaMenuOpen, setIsMegaMenuOpen] = useState(false);
  
  const userMenuRef = useRef<HTMLDivElement>(null);
  const megaMenuRef = useRef<HTMLDivElement>(null);
  const scrollTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const location = useLocation();
  const { isAuthenticated, user, logout } = useAuth();

  useEffect(() => {
    let ticking = false;

    const handleScroll = () => {
      // Set scrolling state active and reset the idle timer
      setIsScrolling(true);
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
      scrollTimeoutRef.current = setTimeout(() => {
        setIsScrolling(false);
      }, 280);

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

    // Close menus on outside click
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setIsUserMenuOpen(false);
      }
      if (megaMenuRef.current && !megaMenuRef.current.contains(event.target as Node)) {
        setIsMegaMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      window.removeEventListener('scroll', handleScroll, true);
      document.removeEventListener('scroll', handleScroll, true);
      document.removeEventListener('mousedown', handleClickOutside);
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current);
      }
    };
  }, []);

  const isHome = location.pathname === '/' || activeTab === 'home';
  const isPlatform = location.pathname === '/platform' || activeTab === 'platform';
  const isChat = location.pathname === '/chat' || activeTab === 'chat';

  // Compute initials & display name
  const displayName = user?.full_name || (user?.email ? user.email.split('@')[0] : 'Executive');
  const userInitial = displayName.charAt(0).toUpperCase() || 'U';

  return (
    <header className={`top-nav-wrapper ${isScrolled ? 'is-scrolled' : ''}`}>
      {/* Dynamic Scroll Progress Line (fades when scrolling stops) */}
      <div
        className={`nav-scroll-progress-line ${isScrolling ? 'is-scrolling' : 'is-idle'}`}
        style={{ transform: `scaleX(${scrollProgress / 100})` }}
        aria-hidden="true"
      />

      <nav className="top-nav">
        <div className="page-container top-nav-inner">
          
          {/* 1. Brand */}
          <Link to="/" className="nav-brand">
            <span className="nav-brand-text">DecisionOS</span>
          </Link>

          {/* 2. Simplified & Powerful Nav Links */}
          <div className="nav-links">
            <Link
              to="/"
              className={`nav-link ${isHome ? 'nav-link-active' : ''}`}
              style={{
                color: isHome ? '#FFFFFF' : undefined,
                fontWeight: isHome ? 700 : undefined,
              }}
            >
              Home
            </Link>

            {/* Platform with Interactive Mega Menu on Hover */}
            <div 
              style={{ position: 'relative', height: '100%', display: 'flex', alignItems: 'center' }} 
              ref={megaMenuRef}
              onMouseEnter={() => setIsMegaMenuOpen(true)}
              onMouseLeave={() => setIsMegaMenuOpen(false)}
            >
              <Link
                to="/platform"
                className={`nav-link ${isPlatform ? 'nav-link-active' : ''}`}
                style={{
                  color: isPlatform || isMegaMenuOpen ? '#FFFFFF' : undefined,
                  fontWeight: isPlatform ? 700 : undefined,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  textDecoration: 'none',
                }}
              >
                <span>Platform</span>
                <ChevronDown size={13} style={{ transform: isMegaMenuOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.15s ease' }} />
              </Link>

              {/* Platform Mega Menu Dropdown */}
              {isMegaMenuOpen && (
                <div
                  style={{
                    position: 'absolute',
                    top: 'calc(100% - 6px)',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    width: '860px',
                    background: '#080A0F',
                    border: '1px solid #14171E',
                    borderRadius: '16px',
                    padding: '24px',
                    zIndex: 200,
                    boxShadow: '0 24px 60px rgba(0,0,0,0.95)',
                    display: 'grid',
                    gridTemplateColumns: 'repeat(4, 1fr)',
                    gap: '20px',
                  }}
                >
                  {/* Column 1: Data & Intelligence */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <div style={{ fontSize: '0.68rem', fontWeight: 800, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.08em', paddingBottom: '6px', borderBottom: '1px solid #14171E' }}>
                      DATA & INTELLIGENCE
                    </div>
                    <Link to="/enterprise-data" onClick={() => setIsMegaMenuOpen(false)} className="mega-menu-item" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 8px', borderRadius: '6px', color: '#E2E8F0', textDecoration: 'none', fontSize: '0.8rem', fontWeight: 600 }}>
                      <Database size={13} color="#10B981" />
                      <span>Data Hub</span>
                    </Link>
                    <Link to="/kpi-dictionary" onClick={() => setIsMegaMenuOpen(false)} className="mega-menu-item" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 8px', borderRadius: '6px', color: '#E2E8F0', textDecoration: 'none', fontSize: '0.8rem', fontWeight: 600 }}>
                      <BookOpen size={13} color="#F59E0B" />
                      <span>KPI Dictionary</span>
                    </Link>
                    <Link to="/chat" onClick={() => setIsMegaMenuOpen(false)} className="mega-menu-item" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 8px', borderRadius: '6px', color: '#E2E8F0', textDecoration: 'none', fontSize: '0.8rem', fontWeight: 600 }}>
                      <MessageSquare size={13} color="#38BDF8" />
                      <span>AI Business Analyst</span>
                    </Link>
                    <Link to="/boardroom" onClick={() => setIsMegaMenuOpen(false)} className="mega-menu-item" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 8px', borderRadius: '6px', color: '#E2E8F0', textDecoration: 'none', fontSize: '0.8rem', fontWeight: 600 }}>
                      <FileText size={13} color="#F59E0B" />
                      <span>Executive Boardroom</span>
                    </Link>
                    <Link to="/decision-copilot" onClick={() => setIsMegaMenuOpen(false)} className="mega-menu-item" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 8px', borderRadius: '6px', color: '#E2E8F0', textDecoration: 'none', fontSize: '0.8rem', fontWeight: 600 }}>
                      <Bot size={13} color="#38BDF8" />
                      <span>AI Decision Copilot</span>
                    </Link>
                  </div>

                  {/* Column 2: Strategy & Execution */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <div style={{ fontSize: '0.68rem', fontWeight: 800, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.08em', paddingBottom: '6px', borderBottom: '1px solid #14171E' }}>
                      STRATEGY & EXECUTION
                    </div>
                    <Link to="/digital-twin" onClick={() => setIsMegaMenuOpen(false)} className="mega-menu-item" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 8px', borderRadius: '6px', color: '#E2E8F0', textDecoration: 'none', fontSize: '0.8rem', fontWeight: 600 }}>
                      <PlayCircle size={13} color="#A855F7" />
                      <span>Digital Twin</span>
                    </Link>
                    <Link to="/strategy-execution" onClick={() => setIsMegaMenuOpen(false)} className="mega-menu-item" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 8px', borderRadius: '6px', color: '#E2E8F0', textDecoration: 'none', fontSize: '0.8rem', fontWeight: 600 }}>
                      <Activity size={13} color="#10B981" />
                      <span>Strategic Initiatives</span>
                    </Link>
                    <Link to="/operating-system" onClick={() => setIsMegaMenuOpen(false)} className="mega-menu-item" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 8px', borderRadius: '6px', color: '#E2E8F0', textDecoration: 'none', fontSize: '0.8rem', fontWeight: 600 }}>
                      <Cpu size={13} color="#38BDF8" />
                      <span>Operating System</span>
                    </Link>
                    <Link to="/operating-system" onClick={() => setIsMegaMenuOpen(false)} className="mega-menu-item" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 8px', borderRadius: '6px', color: '#E2E8F0', textDecoration: 'none', fontSize: '0.8rem', fontWeight: 600 }}>
                      <Sparkles size={13} color="#A855F7" />
                      <span>Playbooks</span>
                    </Link>
                  </div>

                  {/* Column 3: Governance & Risk */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <div style={{ fontSize: '0.68rem', fontWeight: 800, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.08em', paddingBottom: '6px', borderBottom: '1px solid #14171E' }}>
                      GOVERNANCE & RISK
                    </div>
                    <Link to="/governance" onClick={() => setIsMegaMenuOpen(false)} className="mega-menu-item" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 8px', borderRadius: '6px', color: '#E2E8F0', textDecoration: 'none', fontSize: '0.8rem', fontWeight: 600 }}>
                      <Scale size={13} color="#10B981" />
                      <span>Governance Center</span>
                    </Link>
                    <Link to="/risk-concentration" onClick={() => setIsMegaMenuOpen(false)} className="mega-menu-item" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 8px', borderRadius: '6px', color: '#E2E8F0', textDecoration: 'none', fontSize: '0.8rem', fontWeight: 600 }}>
                      <ShieldAlert size={13} color="#EF4444" />
                      <span>Risk Concentration</span>
                    </Link>
                    <Link to="/ai-governance" onClick={() => setIsMegaMenuOpen(false)} className="mega-menu-item" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 8px', borderRadius: '6px', color: '#E2E8F0', textDecoration: 'none', fontSize: '0.8rem', fontWeight: 600 }}>
                      <Bot size={13} color="#A855F7" />
                      <span>AI Governance</span>
                    </Link>
                    <Link to="/security-center" onClick={() => setIsMegaMenuOpen(false)} className="mega-menu-item" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 8px', borderRadius: '6px', color: '#E2E8F0', textDecoration: 'none', fontSize: '0.8rem', fontWeight: 600 }}>
                      <Shield size={13} color="#10B981" />
                      <span>Security Center</span>
                    </Link>
                  </div>

                  {/* Column 4: Enterprise Architecture */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <div style={{ fontSize: '0.68rem', fontWeight: 800, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.08em', paddingBottom: '6px', borderBottom: '1px solid #14171E' }}>
                      ENTERPRISE
                    </div>
                    <Link to="/portfolio-rollup" onClick={() => setIsMegaMenuOpen(false)} className="mega-menu-item" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 8px', borderRadius: '6px', color: '#E2E8F0', textDecoration: 'none', fontSize: '0.8rem', fontWeight: 600 }}>
                      <Layers size={13} color="#38BDF8" />
                      <span>Portfolio Rollup</span>
                    </Link>
                    <Link to="/capital-allocation" onClick={() => setIsMegaMenuOpen(false)} className="mega-menu-item" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 8px', borderRadius: '6px', color: '#E2E8F0', textDecoration: 'none', fontSize: '0.8rem', fontWeight: 600 }}>
                      <DollarSign size={13} color="#A855F7" />
                      <span>Capital Allocation</span>
                    </Link>
                    <Link to="/agents" onClick={() => setIsMegaMenuOpen(false)} className="mega-menu-item" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 8px', borderRadius: '6px', color: '#E2E8F0', textDecoration: 'none', fontSize: '0.8rem', fontWeight: 600 }}>
                      <Bot size={13} color="#818CF8" />
                      <span>Agent Hub</span>
                    </Link>
                    <Link to="/api-platform" onClick={() => setIsMegaMenuOpen(false)} className="mega-menu-item" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 8px', borderRadius: '6px', color: '#E2E8F0', textDecoration: 'none', fontSize: '0.8rem', fontWeight: 600 }}>
                      <Key size={13} color="#F59E0B" />
                      <span>API Platform</span>
                    </Link>
                  </div>

                </div>
              )}
            </div>

            {/* DEX Analyst Option in Main Nav */}
            <Link
              to="/chat"
              className={`nav-link ${isChat ? 'nav-link-active' : ''}`}
              style={{
                color: isChat ? '#FFFFFF' : undefined,
                fontWeight: isChat ? 700 : undefined,
              }}
            >
              DEX Analyst
            </Link>

            {/* Launch Platform Link in Main Nav */}
            <Link
              to="/enterprise"
              className="nav-link"
            >
              Launch Platform
            </Link>
          </div>

          {/* 3. Right Action Area */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {isAuthenticated ? (
              /* Profile Pill with Seamless Subtle Styling */
              <div style={{ position: 'relative' }} ref={userMenuRef}>
                <button
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    borderRadius: '9999px',
                    padding: '4px 14px 4px 6px',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                    boxShadow: 'none',
                  }}
                >
                  {/* Profile Picture / Avatar */}
                  <div
                    style={{
                      width: '28px',
                      height: '28px',
                      borderRadius: '50%',
                      background: 'linear-gradient(135deg, #0284C7 0%, #2563EB 50%, #7C3AED 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#FFFFFF',
                      fontSize: '12px',
                      fontWeight: 800,
                      position: 'relative',
                    }}
                  >
                    {userInitial}
                  </div>

                  {/* User Name - Balanced, clean, non-blooming */}
                  <span 
                    style={{ 
                      fontSize: '0.84rem', 
                      fontWeight: 600, 
                      color: '#E2E8F0', 
                      lineHeight: 1,
                      letterSpacing: '0.01em',
                      textShadow: 'none',
                    }}
                  >
                    {displayName}
                  </span>

                  <ChevronDown size={13} color="#94A3B8" style={{ marginLeft: '2px', transform: isUserMenuOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.15s ease' }} />
                </button>

                {/* Profile Dropdown */}
                {isUserMenuOpen && (
                  <div
                    style={{
                      position: 'absolute',
                      top: 'calc(100% + 8px)',
                      right: 0,
                      width: '240px',
                      background: '#080A0F',
                      border: '1px solid #14171E',
                      borderRadius: '12px',
                      padding: '8px',
                      zIndex: 250,
                      boxShadow: '0 20px 40px rgba(0,0,0,0.85)',
                    }}
                  >
                    <div style={{ padding: '8px 10px 10px 10px', borderBottom: '1px solid #14171E' }}>
                      <div style={{ fontSize: '0.86rem', fontWeight: 800, color: '#FFFFFF' }}>
                        {displayName}
                      </div>
                      <div style={{ fontSize: '0.74rem', color: '#64748B', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {user?.email || 'executive@decisionos.ai'}
                      </div>
                      <div style={{ marginTop: '6px', display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.66rem', fontWeight: 800, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.1)', padding: '2px 6px', borderRadius: '4px', border: '1px solid rgba(56, 189, 248, 0.25)' }}>
                        <Shield size={10} />
                        <span>{user?.role || 'ENTERPRISE EXECUTIVE'}</span>
                      </div>
                    </div>

                    <div style={{ padding: '6px 0', display: 'flex', flexDirection: 'column', gap: '2px' }}>
                      <Link
                        to="/enterprise"
                        onClick={() => setIsUserMenuOpen(false)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          padding: '8px 10px',
                          borderRadius: '6px',
                          color: '#E2E8F0',
                          fontSize: '0.8rem',
                          fontWeight: 700,
                          textDecoration: 'none',
                        }}
                      >
                        <LayoutDashboard size={14} color="#38BDF8" />
                        <span>Command Center</span>
                      </Link>

                      <Link
                        to="/enterprise-data"
                        onClick={() => setIsUserMenuOpen(false)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          padding: '8px 10px',
                          borderRadius: '6px',
                          color: '#E2E8F0',
                          fontSize: '0.8rem',
                          fontWeight: 700,
                          textDecoration: 'none',
                        }}
                      >
                        <Database size={14} color="#10B981" />
                        <span>Enterprise Data Hub</span>
                      </Link>
                    </div>

                    <div style={{ borderTop: '1px solid #14171E', paddingTop: '6px' }}>
                      <button
                        onClick={() => {
                          logout();
                          setIsUserMenuOpen(false);
                        }}
                        style={{
                          width: '100%',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          padding: '8px 10px',
                          background: 'transparent',
                          border: 'none',
                          color: '#EF4444',
                          fontSize: '0.78rem',
                          fontWeight: 700,
                          cursor: 'pointer',
                          borderRadius: '6px',
                          textAlign: 'left',
                        }}
                      >
                        <LogOut size={13} />
                        <span>Sign Out</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <Link to="/login" className="btn-nav-access" style={{ textDecoration: 'none' }}>
                Launch Platform
              </Link>
            )}
          </div>

        </div>
      </nav>
    </header>
  );
};

export default MarketingNavbar;
