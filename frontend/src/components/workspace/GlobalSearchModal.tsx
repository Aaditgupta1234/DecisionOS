import React, { useState, useEffect } from 'react';
import { Search, X, ArrowRight, CornerDownLeft, Database, Target, AlertTriangle, CheckCircle2, GitBranch, Cpu, Sparkles } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export interface GlobalSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const GlobalSearchModal: React.FC<GlobalSearchModalProps> = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const items = [
    { title: 'Secondary Hub Dispatch Bottleneck', type: 'ROOT_CAUSE', desc: 'Root Cause #4 in Southeastern Corridors (+68.8% latency)', link: '/root-causes' },
    { title: 'Carrier Rebalancing & Automated SLA Penalties', type: 'RECOMMENDATION', desc: 'Recommendation #1 (+$124K ARR recovery yield)', link: '/recommendations' },
    { title: 'INIT-2026-001: Win-Back Campaign Deployment', type: 'INITIATIVE', desc: 'Active execution initiative (78% complete)', link: '/execution' },
    { title: 'Customer Retention Rate', type: 'KPI', desc: 'Strategic KPI (Target 85.8%, Current 79.5%)', link: '/metrics' },
    { title: 'CRITICAL: Retention Drift Detected (-7.3%)', type: 'ALERT', desc: 'High severity alert fired in Southeastern corridor', link: '/monitoring' },
    { title: 'Recovery Forecast V3 ($480K Projected ARR)', type: 'FORECAST', desc: 'Rolling 3-cycle recovery forecast (88.4% accuracy)', link: '/forecasting' },
    { title: 'Simulation Run: Logistics Rebalancing (+20% FTE)', type: 'SIMULATION', desc: 'Digital Twin Monte Carlo simulation', link: '/simulations' },
    { title: 'Verified +$124K ARR Realized Recovery', type: 'OUTCOME', desc: 'Measured business recovery verified by OutcomeEngine', link: '/outcomes' },
    { title: 'Ask DEX Analyst about Churn in Southeast', type: 'AI_PROMPT', desc: 'Ask DEX Analyst for graph-grounded explanation', link: '/ai-analyst' },
  ];

  const filtered = items.filter((item) =>
    item.title.toLowerCase().includes(query.toLowerCase()) ||
    item.desc.toLowerCase().includes(query.toLowerCase()) ||
    item.type.toLowerCase().includes(query.toLowerCase())
  );

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        onClose();
      }
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        backdropFilter: 'blur(8px)',
        zIndex: 300,
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        paddingTop: '12vh',
        animation: 'fadeIn 0.15s ease',
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: '640px',
          maxWidth: '92vw',
          backgroundColor: '#090D14',
          border: '1px solid #1E293B',
          borderRadius: '12px',
          boxShadow: '0 25px 60px rgba(0,0,0,0.95)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input Bar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '16px 20px', borderBottom: '1px solid #1E293B' }}>
          <Search size={18} color="#38BDF8" />
          <input
            type="text"
            placeholder="Search KPIs, Root Causes, Recommendations, Initiatives, Simulations, Forecasts..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
            style={{
              width: '100%',
              background: 'transparent',
              border: 'none',
              outline: 'none',
              fontSize: '0.95rem',
              color: '#FFFFFF',
              fontWeight: 500,
            }}
          />
          <kbd style={{ background: '#1E293B', color: '#94A3B8', padding: '2px 6px', borderRadius: '4px', fontSize: '10px', fontWeight: 700 }}>
            ESC
          </kbd>
        </div>

        {/* Results List */}
        <div style={{ maxHeight: '380px', overflowY: 'auto', padding: '8px' }}>
          {filtered.length > 0 ? (
            filtered.map((res) => (
              <div
                key={res.title}
                onClick={() => {
                  navigate(res.link);
                  onClose();
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '10px 14px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  marginBottom: '2px',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(56, 189, 248, 0.1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '2px' }}>
                    <span style={{ fontSize: '0.68rem', fontWeight: 800, textTransform: 'uppercase', color: '#38BDF8', background: 'rgba(56, 189, 248, 0.12)', padding: '2px 6px', borderRadius: '4px' }}>
                      {res.type}
                    </span>
                    <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#FFFFFF' }}>{res.title}</span>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#94A3B8' }}>{res.desc}</div>
                </div>
                <ArrowRight size={14} color="#64748B" />
              </div>
            ))
          ) : (
            <div style={{ padding: '30px 20px', textAlign: 'center', color: '#64748B', fontSize: '0.85rem' }}>
              No intelligence entities found matching "{query}"
            </div>
          )}
        </div>

        {/* Footer info */}
        <div style={{ borderTop: '1px solid #1E293B', padding: '8px 16px', background: '#070A0F', display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.72rem', color: '#64748B' }}>
          <span>Navigate with Universal Deep Links</span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span>Press</span>
            <kbd style={{ background: '#1E293B', padding: '1px 4px', borderRadius: '3px', color: '#94A3B8' }}>↵ Enter</kbd>
            <span>to open</span>
          </div>
        </div>
      </div>
    </div>
  );
};
