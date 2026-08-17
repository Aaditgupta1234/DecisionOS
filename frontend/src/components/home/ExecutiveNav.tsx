import React from 'react';
import { Link } from 'react-router-dom';
import { Activity, ArrowRight, ShieldCheck, Terminal, Cpu } from 'lucide-react';

export const ExecutiveNav: React.FC = () => {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-[#060709]/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo & Telemetry Status */}
        <div className="flex items-center gap-6">
          <Link to="/" className="flex items-center gap-2.5 text-white font-bold text-lg tracking-tight group">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 to-cyan-400 p-0.5 shadow-lg shadow-blue-500/20 group-hover:shadow-blue-500/40 transition-all">
              <div className="w-full h-full bg-[#0b0c0e] rounded-[6px] flex items-center justify-center">
                <Cpu className="w-4 h-4 text-blue-400" />
              </div>
            </div>
            <span>Decision<span className="text-blue-400">OS</span></span>
          </Link>

          {/* Real-time Status Badge */}
          <div className="hidden lg:flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>Deterministic Engines: 783/783 Active</span>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-7 text-sm font-medium text-gray-300">
          <a href="#why-decisionos" className="hover:text-white transition-colors">Why DecisionOS</a>
          <a href="#pipeline" className="hover:text-white transition-colors">Intelligence Pipeline</a>
          <a href="#imperatives" className="hover:text-white transition-colors">Core Pillars</a>
          <a href="#preview" className="hover:text-white transition-colors">Command Center</a>
          <a href="#dex-sandbox" className="hover:text-white transition-colors">DEX Terminal</a>
          <a href="#scale" className="hover:text-white transition-colors text-blue-400/90 font-semibold">Scale & Proof</a>
        </nav>

        {/* Action Button */}
        <div className="flex items-center gap-3">
          <Link
            to="/dashboard"
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs sm:text-sm font-semibold shadow-lg shadow-blue-600/25 border border-blue-400/30 transition-all hover:scale-[1.02]"
          >
            <span>Launch Command Center</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

      </div>
    </header>
  );
};
