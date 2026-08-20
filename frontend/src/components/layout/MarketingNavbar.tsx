import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import '../../styles/home.css';

interface MarketingNavbarProps {
  activeTab?: string;
}

export const MarketingNavbar: React.FC<MarketingNavbarProps> = ({ activeTab }) => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0);
  const location = useLocation();

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

  const isCurrentIntelligence = location.pathname === '/kpi-dictionary' || activeTab === 'intelligence';

  return (
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
            <Link to="/#comparison" className="nav-link">
              Why DecisionOS
            </Link>
            <Link to="/#pipeline" className="nav-link">
              Signature Pipeline
            </Link>
            <Link
              to="/kpi-dictionary"
              className={`nav-link ${isCurrentIntelligence ? 'nav-link-active' : ''}`}
              style={{
                color: isCurrentIntelligence ? '#FFFFFF' : undefined,
                fontWeight: isCurrentIntelligence ? 700 : undefined,
                position: 'relative',
              }}
            >
              <span>Intelligence</span>
              {isCurrentIntelligence && (
                <span
                  style={{
                    position: 'absolute',
                    bottom: '-6px',
                    left: 0,
                    right: 0,
                    height: '2px',
                    background: '#38BDF8',
                    borderRadius: '2px',
                    boxShadow: '0 0 8px rgba(56, 189, 248, 0.8)',
                  }}
                />
              )}
            </Link>
            <Link to="/#solutions" className="nav-link">
              Solutions
            </Link>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="nav-link"
            >
              Docs
            </a>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Link to="/enterprise" className="btn-nav-access">
              Access Platform
            </Link>
          </div>
        </div>
      </nav>
    </header>
  );
};
export default MarketingNavbar;
