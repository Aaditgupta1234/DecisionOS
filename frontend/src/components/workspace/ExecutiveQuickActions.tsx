import React from 'react';
import { Play, Sparkles, Network, FileText, CheckSquare, PlusCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export interface ExecutiveQuickActionsProps {
  onOpenExplainability?: () => void;
}

export const ExecutiveQuickActions: React.FC<ExecutiveQuickActionsProps> = ({
  onOpenExplainability,
}) => {
  const navigate = useNavigate();

  const actions = [
    { label: 'Run Simulation', icon: Play, color: '#38BDF8', action: () => navigate('/simulations') },
    { label: 'Ask AI Analyst', icon: Sparkles, color: '#A855F7', action: () => navigate('/ai-analyst') },
    { label: 'Explore Knowledge Graph', icon: Network, color: '#10B981', action: () => navigate('/knowledge-graph') },
    { label: 'Decision Copilot', icon: CheckSquare, color: '#F59E0B', action: () => navigate('/decision-copilot') },
    { label: 'Generate Board Report', icon: FileText, color: '#06B6D4', action: () => navigate('/reports') },
  ];

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        padding: '12px 18px',
        background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(9, 13, 20, 0.95))',
        border: '1px solid #1E293B',
        borderRadius: '10px',
        overflowX: 'auto',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginRight: '6px', color: '#64748B', fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 800, letterSpacing: '0.06em' }}>
        <PlusCircle size={14} color="#38BDF8" />
        <span>Executive Quick Actions</span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
        {actions.map((act) => {
          const Icon = act.icon;
          return (
            <button
              key={act.label}
              onClick={act.action}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '6px 12px',
                background: 'rgba(30, 41, 59, 0.6)',
                border: '1px solid #334155',
                borderRadius: '6px',
                color: '#F1F5F9',
                fontSize: '0.78rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(56, 189, 248, 0.15)';
                e.currentTarget.style.borderColor = act.color;
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(30, 41, 59, 0.6)';
                e.currentTarget.style.borderColor = '#334155';
              }}
            >
              <Icon size={13} color={act.color} />
              <span>{act.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
