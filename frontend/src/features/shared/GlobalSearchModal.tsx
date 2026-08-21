import React, { useState, useEffect, useRef } from 'react';
import { Search, Sparkles, TrendingUp, ShieldCheck, Play, ArrowRight, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { SearchEntity } from '../../types/SearchEntity';
import { Badge } from '../../design-system/Badge';

interface GlobalSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const GlobalSearchModal: React.FC<GlobalSearchModalProps> = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const searchEntities: SearchEntity[] = [
    { id: '1', code: 'DEC-042', type: 'DECISION', title: 'Southeastern Carrier Reallocation & SLA Penalties', subtitle: '+$312K realized ARR (91.8% accuracy)', category: 'Decisions', route: '/governance', badge: 'DECISION', badgeColor: 'emerald' },
    { id: '2', code: 'INIT-051', type: 'INITIATIVE', title: 'Carrier Route Dynamic Balancing', subtitle: 'Strategic recovery initiative for retention', category: 'Initiatives', route: '/strategy-execution', badge: 'INITIATIVE', badgeColor: 'sky' },
    { id: '3', code: 'PBT-001', type: 'PLAYBOOK', title: 'Autonomous Retention Recovery & Governance Playbook', subtitle: 'Triggered on retention drift < -5%', category: 'Playbooks', route: '/operating-system', badge: 'PLAYBOOK', badgeColor: 'purple' },
    { id: '4', code: 'KPI-ARR', type: 'KPI', title: 'Net ARR & Expansion Growth', subtitle: 'Global ARR: $12.4M (85.0 Health)', category: 'KPIs', route: '/metrics', badge: 'KPI', badgeColor: 'amber' },
    { id: '5', code: 'SIM-018', type: 'SCENARIO', title: 'Close Retention Gap to Industry Median', subtitle: 'Digital Twin Scenario (+$340K ARR)', category: 'Scenarios', route: '/scenarios/comparison', badge: 'SCENARIO', badgeColor: 'purple' },
    { id: '6', code: 'ALT-089', type: 'ALERT', title: 'Southeastern Courier SLA Transit Failure', subtitle: '15m Critical SLA countdown', category: 'Alerts', route: '/monitoring', badge: 'ALERT', badgeColor: 'rose' },
    { id: '7', code: 'CAP-001', type: 'PORTFOLIO', title: 'Capital Allocation: SaaS vs Retail ($1M)', subtitle: '62% SaaS (7.2x ROI) allocation recommendation', category: 'Capital Allocation', route: '/capital-allocation', badge: 'CAPITAL', badgeColor: 'emerald' },
    { id: '8', code: 'AGT-001', type: 'AGENT', title: 'Customer Retention Autonomous Agent', subtitle: 'Active causal diagnosis & SLA modeling', category: 'Agents', route: '/agents', badge: 'AGENT', badgeColor: 'sky' },
  ];

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
      const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
          onClose();
        }
      };
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    } else {
      setQuery('');
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const filtered = query
    ? searchEntities.filter(
        (e) =>
          e.title.toLowerCase().includes(query.toLowerCase()) ||
          e.code.toLowerCase().includes(query.toLowerCase()) ||
          e.subtitle.toLowerCase().includes(query.toLowerCase())
      )
    : searchEntities;

  const handleSelect = (route: string) => {
    navigate(route);
    onClose();
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(8px)',
        zIndex: 10000,
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        paddingTop: '100px',
        paddingLeft: '16px',
        paddingRight: '16px',
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '640px',
          backgroundColor: '#090D14',
          border: '1px solid #1E293B',
          borderRadius: '16px',
          overflow: 'hidden',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.8)',
          display: 'flex',
          flexDirection: 'column',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '16px 20px', borderBottom: '1px solid #1E293B' }}>
          <Search size={18} color="#64748B" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Type a command or search across KPIs, Decisions, Playbooks, Agents (Ctrl+K)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              color: '#FFFFFF',
              fontSize: '0.92rem',
              outline: 'none',
            }}
          />
          <kbd style={{ fontSize: '0.68rem', padding: '2px 6px', borderRadius: '4px', background: '#1E293B', color: '#94A3B8' }}>ESC</kbd>
        </div>

        {/* Results List */}
        <div style={{ maxHeight: '380px', overflowY: 'auto', padding: '10px' }}>
          {filtered.map((item) => (
            <div
              key={item.id}
              onClick={() => handleSelect(item.route)}
              style={{
                padding: '12px 14px',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                cursor: 'pointer',
                transition: 'background 0.15s ease',
              }}
              onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(56, 189, 248, 0.08)')}
              onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Badge variant={item.badgeColor as any} size="sm">
                  {item.badge}
                </Badge>
                <div>
                  <div style={{ fontSize: '0.86rem', fontWeight: 700, color: '#FFFFFF' }}>{item.title}</div>
                  <div style={{ fontSize: '0.74rem', color: '#64748B' }}>{item.subtitle}</div>
                </div>
              </div>
              <ArrowRight size={14} color="#64748B" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
