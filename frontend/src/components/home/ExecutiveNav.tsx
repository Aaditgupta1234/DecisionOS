import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Cpu } from 'lucide-react';

export const ExecutiveNav: React.FC = () => {
  return (
    <header className="exec-navbar">
      <div className="exec-navbar-container">
        
        {/* Brand Logo */}
        <Link to="/" className="exec-brand-logo">
          <div className="exec-brand-icon">
            <Cpu className="w-4 h-4" />
          </div>
          <span>Decision<span style={{ color: '#2e90ff' }}>OS</span></span>
        </Link>

        {/* Center Navigation Links */}
        <nav className="exec-nav-menu">
          <a href="#why-decisionos" className="exec-nav-item">Platform</a>
          <a href="#pipeline" className="exec-nav-item">Pipeline</a>
          <a href="#imperatives" className="exec-nav-item">Capabilities</a>
          <a href="#preview" className="exec-nav-item">Command Center</a>
          <a href="#dex-sandbox" className="exec-nav-item">DEX Terminal</a>
          <a href="#scale" className="exec-nav-item">Scale</a>
        </nav>

        {/* Action Button */}
        <div>
          <Link to="/dashboard" className="btn-access-platform">
            <span>Access Platform</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

      </div>
    </header>
  );
};
