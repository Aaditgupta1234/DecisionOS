import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Cpu, ShieldCheck, Terminal, BookOpen } from 'lucide-react';

export const ExecutiveCtaFooter: React.FC = () => {
  return (
    <footer className="w-full bg-[#040507] border-t border-white/10 pt-20 pb-12 px-4 sm:px-6 lg:px-8 z-10 relative">
      <div className="max-w-7xl mx-auto">
        
        {/* Large Action Banner */}
        <div className="glass-panel-elevated p-8 sm:p-12 border-blue-500/30 text-center relative overflow-hidden mb-20 shadow-2xl shadow-blue-500/10">
          <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-96 h-48 bg-blue-500/20 rounded-full blur-3xl pointer-events-none" />
          
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/15 border border-blue-400/30 text-blue-300 text-xs font-semibold uppercase tracking-wider mb-4">
            <Cpu className="w-3.5 h-3.5" />
            <span>Executive Business Assistant</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight max-w-3xl mx-auto mb-4">
            Command Your Business with Deterministic Intelligence
          </h2>

          <p className="text-gray-300 max-w-xl mx-auto mb-8 text-sm sm:text-base leading-relaxed">
            Move beyond static dashboards. Experience automated root-cause diagnosis, expected ROI optimization, and explainable executive decision support.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4">
            <Link to="/dashboard" className="btn-primary-command">
              <span>Launch Command Center</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <a 
              href="http://localhost:8000/docs" 
              target="_blank" 
              rel="noreferrer"
              className="btn-secondary-command"
            >
              <BookOpen className="w-4 h-4 text-blue-400" />
              <span>Review FastAPI Docs</span>
            </a>
          </div>
        </div>

        {/* Footer Navigation Columns */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 pb-12 border-b border-white/10 text-xs">
          
          <div>
            <div className="flex items-center gap-2 text-white font-bold text-base mb-4">
              <Cpu className="w-4 h-4 text-blue-400" />
              <span>DecisionOS</span>
            </div>
            <p className="text-gray-400 leading-relaxed mb-4">
              The deterministic executive intelligence and business assistant platform.
            </p>
            <div className="text-emerald-400 font-mono text-[11px] flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              <span>System: All Engines Operational</span>
            </div>
          </div>

          <div>
            <div className="font-bold text-white uppercase tracking-wider mb-4 text-[11px]">
              Platform Architecture
            </div>
            <ul className="space-y-2.5 text-gray-400">
              <li><Link to="/dashboard" className="hover:text-white transition-colors">Command Center</Link></li>
              <li><Link to="/metrics" className="hover:text-white transition-colors">KPI Engine</Link></li>
              <li><Link to="/diagnostics" className="hover:text-white transition-colors">Diagnostic Finding Rules</Link></li>
              <li><Link to="/root-causes" className="hover:text-white transition-colors">Causal Root Causes DAG</Link></li>
              <li><Link to="/recommendations" className="hover:text-white transition-colors">Executive Recommendations</Link></li>
            </ul>
          </div>

          <div>
            <div className="font-bold text-white uppercase tracking-wider mb-4 text-[11px]">
              Governance & Analytics
            </div>
            <ul className="space-y-2.5 text-gray-400">
              <li><Link to="/strategy" className="hover:text-white transition-colors">Strategic Portfolio Analytics</Link></li>
              <li><Link to="/reports" className="hover:text-white transition-colors">Lossless State Replay</Link></li>
              <li><Link to="/scenarios" className="hover:text-white transition-colors">Scenario Simulator</Link></li>
              <li><Link to="/forecasts" className="hover:text-white transition-colors">Rolling Time-Series</Link></li>
              <li><Link to="/settings/organization" className="hover:text-white transition-colors">Multi-Tenant RBAC</Link></li>
            </ul>
          </div>

          <div>
            <div className="font-bold text-white uppercase tracking-wider mb-4 text-[11px]">
              Rigor & Security
            </div>
            <ul className="space-y-2.5 text-gray-400">
              <li className="flex items-center gap-1.5 text-gray-300">
                <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
                <span>Zero AI Hallucination</span>
              </li>
              <li><span>100% Deterministic Math</span></li>
              <li><span>SHA-256 State Integrity</span></li>
              <li><span>783+ Pytest Automated Tests</span></li>
              <li><span>MIT Open Source License</span></li>
            </ul>
          </div>

        </div>

        {/* Copyright & Sub-links */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between text-xs text-gray-500 gap-4">
          <div>
            © 2026 DecisionOS Platform. All rights reserved.
          </div>
          <div className="flex gap-6">
            <span className="hover:text-gray-400 transition-colors">Privacy Policy</span>
            <span className="hover:text-gray-400 transition-colors">Terms of Service</span>
            <span className="hover:text-gray-400 transition-colors">Security Standards</span>
            <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="hover:text-gray-400 transition-colors">API Docs</a>
          </div>
        </div>

      </div>
    </footer>
  );
};
