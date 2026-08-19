import React, { useState } from 'react';
import { Eye, ChevronDown, Check, Bookmark, Plus } from 'lucide-react';

export interface SavedViewsSelectorProps {
  currentView?: string;
  onSelectView?: (view: string) => void;
}

export const SavedViewsSelector: React.FC<SavedViewsSelectorProps> = ({
  currentView = 'CEO View',
  onSelectView,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [activeView, setActiveView] = useState(currentView);

  const views = [
    { name: 'CEO View', desc: 'High-level Health, ARR Recovery & Systemic Risk', default: true },
    { name: 'COO Operations View', desc: 'KPI Drift, Active Alerts & Secondary Hub Dispatch', default: false },
    { name: 'Growth & Marketing View', desc: 'Win-Back Campaign ROI & Churn Recovery', default: false },
    { name: 'Boardroom Governance View', desc: 'Forecast Reliability, Provenance & Decision Sessions', default: false },
  ];

  return (
    <div style={{ position: 'relative' }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 12px',
          fontSize: '0.82rem',
          fontWeight: 700,
          background: 'rgba(15, 23, 42, 0.8)',
          border: '1px solid #1E293B',
          borderRadius: '6px',
          color: '#FFFFFF',
          cursor: 'pointer',
        }}
      >
        <Eye size={13} color="#38BDF8" />
        <span>View:</span>
        <span style={{ color: '#38BDF8' }}>{activeView}</span>
        <ChevronDown size={12} color="#94A3B8" />
      </button>

      {isOpen && (
        <div
          style={{
            position: 'absolute',
            top: '100%',
            left: 0,
            marginTop: '6px',
            width: '280px',
            backgroundColor: '#090D14',
            border: '1px solid #1E293B',
            borderRadius: '8px',
            boxShadow: '0 20px 40px rgba(0,0,0,0.9)',
            padding: '6px',
            zIndex: 100,
          }}
        >
          <div style={{ padding: '6px 10px', fontSize: '0.7rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Executive Saved Views
          </div>
          {views.map((v) => {
            const isSelected = activeView === v.name;
            return (
              <div
                key={v.name}
                onClick={() => {
                  setActiveView(v.name);
                  if (onSelectView) onSelectView(v.name);
                  setIsOpen(false);
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '8px 10px',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  backgroundColor: isSelected ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
                  color: isSelected ? '#38BDF8' : '#F1F5F9',
                  fontSize: '0.8rem',
                  marginBottom: '2px',
                }}
              >
                <div>
                  <div style={{ fontWeight: isSelected ? 700 : 500 }}>{v.name}</div>
                  <div style={{ fontSize: '0.68rem', color: '#64748B' }}>{v.desc}</div>
                </div>
                {isSelected && <Check size={14} color="#38BDF8" />}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
