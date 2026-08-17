import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  TrendingUp, 
  ArrowUpRight, 
  Activity, 
  ShieldCheck, 
  Users, 
  ShoppingBag, 
  DollarSign, 
  ArrowRight,
  Sparkles,
  Cpu
} from 'lucide-react';

export const ExecutiveCommandCenterPreview: React.FC = () => {
  const [activeTimeframe, setActiveTimeframe] = useState<'12M' | '6M' | '30D'>('12M');

  return (
    <section id="preview" className="py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto z-10 relative">
      
      {/* Section Header */}
      <div className="text-center max-w-3xl mx-auto mb-14">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-400/20 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-3">
          Executive Workspace
        </div>
        <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Executive Command Center Overview
        </h2>
        <p className="mt-3 text-base sm:text-lg text-gray-400">
          A real-time command center engineered for data-driven executive leadership.
        </p>
      </div>

      {/* Main Terminal Container */}
      <div className="glass-panel-elevated p-6 sm:p-8 border-white/10 bg-[#0a0c10]/90 shadow-2xl relative">
        
        {/* Terminal Header Bar */}
        <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-6">
          <div className="flex items-center gap-3">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-red-500/80" />
              <div className="w-3 h-3 rounded-full bg-amber-500/80" />
              <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
            </div>
            <span className="text-xs font-mono text-gray-400 pl-2">
              DecisionOS Terminal // Production Instance
            </span>
          </div>

          <div className="flex items-center gap-2">
            {(['12M', '6M', '30D'] as const).map(tf => (
              <button
                key={tf}
                onClick={() => setActiveTimeframe(tf)}
                className={`px-2.5 py-1 rounded text-xs font-mono transition-all ${
                  activeTimeframe === tf 
                    ? 'bg-blue-600 text-white font-bold' 
                    : 'bg-white/5 text-gray-400 hover:text-white'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>

        {/* 4 Metric Cards Strip */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          
          <div className="glass-panel p-4 bg-black/40 border-white/5">
            <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
              <span>Total Revenue</span>
              <DollarSign className="w-3.5 h-3.5 text-blue-400" />
            </div>
            <div className="text-xl sm:text-2xl font-bold text-white tracking-tight">$4.2M</div>
            <div className="mt-1 text-[11px] text-emerald-400 font-medium">
              +12.4% vs last period
            </div>
          </div>

          <div className="glass-panel p-4 bg-black/40 border-white/5">
            <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
              <span>Total Orders</span>
              <ShoppingBag className="w-3.5 h-3.5 text-cyan-400" />
            </div>
            <div className="text-xl sm:text-2xl font-bold text-white tracking-tight">18,530</div>
            <div className="mt-1 text-[11px] text-emerald-400 font-medium">
              +8.7% vs last period
            </div>
          </div>

          <div className="glass-panel p-4 bg-black/40 border-white/5">
            <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
              <span>Active Customers</span>
              <Users className="w-3.5 h-3.5 text-purple-400" />
            </div>
            <div className="text-xl sm:text-2xl font-bold text-white tracking-tight">6,842</div>
            <div className="mt-1 text-[11px] text-emerald-400 font-medium">
              +11.3% vs last period
            </div>
          </div>

          <div className="glass-panel p-4 bg-black/40 border-white/5">
            <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
              <span>Business Health</span>
              <Activity className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-xl sm:text-2xl font-bold text-white tracking-tight">82</span>
              <span className="text-xs text-gray-400">/ 100</span>
            </div>
            <div className="mt-1 text-[11px] text-emerald-400 font-medium">
              Good Performance
            </div>
          </div>

        </div>

        {/* Middle & Right Content: Trends & DEX Briefing */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Charts Column (2 Cols) */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Historical Revenue Chart */}
            <div className="glass-panel p-5 bg-black/40 border-white/5">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <div className="text-xs font-semibold text-gray-300">Revenue Trend (Historical)</div>
                  <div className="text-[11px] text-gray-500">12-Month Performance Curve</div>
                </div>
                <div className="text-sm font-bold text-white font-mono">$4.2M Dec 2024</div>
              </div>

              {/* Vector SVG Area Chart */}
              <div className="h-36 w-full pt-2">
                <svg className="w-full h-full overflow-visible" viewBox="0 0 500 100" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="gradRev" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stopColor="#2e90ff" stopOpacity="0.35" />
                      <stop offset="100%" stopColor="#2e90ff" stopOpacity="0.0" />
                    </linearGradient>
                  </defs>
                  <path 
                    d="M 0,80 Q 50,70 100,75 T 200,60 T 300,50 T 400,30 T 500,20 L 500,100 L 0,100 Z" 
                    fill="url(#gradRev)" 
                  />
                  <path 
                    d="M 0,80 Q 50,70 100,75 T 200,60 T 300,50 T 400,30 T 500,20" 
                    fill="none" 
                    stroke="#2e90ff" 
                    strokeWidth="2.5" 
                  />
                  <circle cx="500" cy="20" r="4" fill="#2e90ff" className="animate-pulse" />
                </svg>
              </div>
              <div className="flex justify-between text-[10px] text-gray-500 font-mono mt-2 pt-2 border-t border-white/5">
                <span>Jan</span><span>Mar</span><span>May</span><span>Jul</span><span>Sep</span><span>Nov</span><span>Dec</span>
              </div>
            </div>

            {/* Forecast Projection Chart */}
            <div className="glass-panel p-5 bg-black/40 border-white/5">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <div className="text-xs font-semibold text-gray-300">Deterministic Forecast Projection</div>
                  <div className="text-[11px] text-gray-500">Next 3-Month Forward Curve</div>
                </div>
                <div className="text-sm font-bold text-emerald-400 font-mono">$4.8M (+9.6%)</div>
              </div>

              {/* Vector SVG Area Chart Forecast */}
              <div className="h-28 w-full pt-1">
                <svg className="w-full h-full overflow-visible" viewBox="0 0 500 80" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="gradForecast" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stopColor="#4edea3" stopOpacity="0.3" />
                      <stop offset="100%" stopColor="#4edea3" stopOpacity="0.0" />
                    </linearGradient>
                  </defs>
                  <path 
                    d="M 0,65 Q 125,50 250,35 T 500,15 L 500,80 L 0,80 Z" 
                    fill="url(#gradForecast)" 
                  />
                  <path 
                    d="M 0,65 Q 125,50 250,35 T 500,15" 
                    fill="none" 
                    stroke="#4edea3" 
                    strokeWidth="2.5" 
                    strokeDasharray="4 4"
                  />
                  <circle cx="500" cy="15" r="4" fill="#4edea3" />
                </svg>
              </div>
              <div className="flex justify-between text-[10px] text-gray-500 font-mono mt-2 pt-1 border-t border-white/5">
                <span>Current Dec</span><span>Jan (Projected)</span><span>Feb (Projected)</span><span>Mar (Projected)</span>
              </div>
            </div>

          </div>

          {/* Right Column: DEX Briefing & Root Cause Drawer */}
          <div className="space-y-6">
            
            {/* DEX Executive Summary */}
            <div className="glass-panel p-5 bg-[#12141a] border-blue-500/30">
              <div className="flex items-center gap-2 mb-3 text-blue-400 text-xs font-bold uppercase tracking-wider">
                <Cpu className="w-4 h-4" />
                <span>Executive Summary</span>
              </div>
              <p className="text-xs text-gray-300 leading-relaxed mb-4">
                Revenue increased 12.4% driven by higher AOV and returning customer cohorts. However, fulfillment latency elevated customer churn risk by 4.3% in the last 30 days.
              </p>
              <Link 
                to="/reports" 
                className="w-full py-2 px-3 rounded-lg bg-blue-600/20 hover:bg-blue-600/30 border border-blue-400/30 text-blue-300 text-xs font-semibold flex items-center justify-center gap-1.5 transition-all"
              >
                <span>View Full Executive Report</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {/* Top Root Cause Drawer */}
            <div className="glass-panel p-5 bg-black/40 border-white/5">
              <div className="text-[11px] font-mono text-red-400 font-semibold uppercase mb-1">
                Top Root Cause Isolated
              </div>
              <div className="text-sm font-bold text-white mb-2">
                Customer Retention Decline
              </div>
              <p className="text-xs text-gray-400 leading-relaxed mb-4">
                Causal analysis shows churn increased due to late carrier dispatch schedules and reduced fulfillment engagement in the last 30 days.
              </p>
              <Link 
                to="/root-causes"
                className="w-full py-2 px-3 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 text-xs font-medium flex items-center justify-center gap-1.5 transition-all"
              >
                <span>Explore Causal Root Causes</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

          </div>

        </div>

      </div>

    </section>
  );
};
