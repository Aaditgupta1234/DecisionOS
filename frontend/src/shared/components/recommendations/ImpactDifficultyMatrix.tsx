import React from 'react';
import { Recommendation } from '../../../types';
import { Zap, ShieldCheck, ArrowRight } from 'lucide-react';

export interface MatrixItem {
  id: string;
  title: string;
  impactScore: string;
  difficulty: 'LOW' | 'MEDIUM' | 'HIGH';
  impactLevel: 'HIGH' | 'LOW';
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM';
}

interface Props {
  items?: MatrixItem[];
  onSelectItem?: (id: string) => void;
}

export const ImpactDifficultyMatrix: React.FC<Props> = ({
  items = [
    { id: 'rec_1', title: 'Targeted Win-Back Campaign', impactScore: '+$180K', difficulty: 'LOW', impactLevel: 'HIGH', priority: 'HIGH' },
    { id: 'rec_2', title: 'Dynamic Dispatch Load-Balancing', impactScore: '+$140K', difficulty: 'MEDIUM', impactLevel: 'HIGH', priority: 'HIGH' },
    { id: 'rec_3', title: 'Cross-Sell Recommendation Engine', impactScore: '+$85K', difficulty: 'LOW', impactLevel: 'LOW', priority: 'MEDIUM' },
    { id: 'rec_4', title: 'One-Click Payment Retries', impactScore: '+$40K', difficulty: 'LOW', impactLevel: 'LOW', priority: 'MEDIUM' },
    { id: 'rec_5', title: 'Warehouse Automation Overhaul', impactScore: '+$110K', difficulty: 'HIGH', impactLevel: 'HIGH', priority: 'MEDIUM' },
  ],
  onSelectItem,
}) => {
  const quickWins = items.filter(i => i.impactLevel === 'HIGH' && (i.difficulty === 'LOW' || i.difficulty === 'MEDIUM'));
  const majorProjects = items.filter(i => i.impactLevel === 'HIGH' && i.difficulty === 'HIGH');
  const optimizations = items.filter(i => i.impactLevel === 'LOW' && i.difficulty === 'LOW');
  const longTerm = items.filter(i => i.impactLevel === 'LOW' && (i.difficulty === 'MEDIUM' || i.difficulty === 'HIGH'));

  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '12px',
      padding: '20px',
      marginBottom: '24px',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div>
          <h3 style={{ fontSize: '15px', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
            Impact vs. Difficulty Quadrant Matrix
          </h3>
          <span style={{ fontSize: '11px', color: '#64748B' }}>
            Executive prioritization matrix segmenting quick wins from complex strategic initiatives
          </span>
        </div>
        <span style={{ fontSize: '10.5px', color: '#38BDF8', fontWeight: 700, background: 'rgba(56, 189, 248, 0.1)', padding: '2px 8px', borderRadius: '4px' }}>
          4-Quadrant Optimization
        </span>
      </div>

      {/* 2x2 Quadrant Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
        {/* Quadrant 1: Quick Wins (High Impact, Low Difficulty) */}
        <div style={{ background: '#050B12', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', padding: '14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
            <span style={{ fontSize: '11.5px', fontWeight: 800, color: '#10B981', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              ⚡ Quick Wins (High Impact / Low Effort)
            </span>
            <span style={{ fontSize: '10px', color: '#10B981', fontWeight: 700 }}>Priority Q1</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {quickWins.map((item) => (
              <div
                key={item.id}
                onClick={() => onSelectItem && onSelectItem(item.id)}
                style={{
                  background: '#090D14',
                  border: '1px solid #141C28',
                  borderRadius: '6px',
                  padding: '8px 10px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  cursor: 'pointer',
                  fontSize: '11.5px',
                }}
              >
                <span style={{ fontWeight: 600, color: '#FFFFFF' }}>{item.title}</span>
                <span style={{ fontWeight: 800, color: '#10B981' }}>{item.impactScore}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Quadrant 2: Major Strategic Projects (High Impact, High Difficulty) */}
        <div style={{ background: '#0B0D12', border: '1px solid rgba(56, 189, 248, 0.25)', borderRadius: '8px', padding: '14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
            <span style={{ fontSize: '11.5px', fontWeight: 800, color: '#38BDF8', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              🎯 Major Strategic Initiatives (High Impact / High Effort)
            </span>
            <span style={{ fontSize: '10px', color: '#38BDF8', fontWeight: 700 }}>Priority Q2</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {majorProjects.map((item) => (
              <div
                key={item.id}
                onClick={() => onSelectItem && onSelectItem(item.id)}
                style={{
                  background: '#090D14',
                  border: '1px solid #141C28',
                  borderRadius: '6px',
                  padding: '8px 10px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  cursor: 'pointer',
                  fontSize: '11.5px',
                }}
              >
                <span style={{ fontWeight: 600, color: '#FFFFFF' }}>{item.title}</span>
                <span style={{ fontWeight: 800, color: '#38BDF8' }}>{item.impactScore}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Quadrant 3: Optimizations (Low Impact, Low Difficulty) */}
        <div style={{ background: '#080A0E', border: '1px solid #1A2230', borderRadius: '8px', padding: '14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
            <span style={{ fontSize: '11.5px', fontWeight: 700, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              🔧 Operational Optimizations (Low Impact / Low Effort)
            </span>
            <span style={{ fontSize: '10px', color: '#64748B', fontWeight: 600 }}>Priority Q3</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {optimizations.map((item) => (
              <div
                key={item.id}
                onClick={() => onSelectItem && onSelectItem(item.id)}
                style={{
                  background: '#090D14',
                  border: '1px solid #141C28',
                  borderRadius: '6px',
                  padding: '8px 10px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  cursor: 'pointer',
                  fontSize: '11.5px',
                }}
              >
                <span style={{ fontWeight: 500, color: '#CBD5E1' }}>{item.title}</span>
                <span style={{ fontWeight: 700, color: '#10B981' }}>{item.impactScore}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Quadrant 4: Long-Term (Low Impact, High Difficulty) */}
        <div style={{ background: '#080A0E', border: '1px solid #141A24', borderRadius: '8px', padding: '14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
            <span style={{ fontSize: '11.5px', fontWeight: 700, color: '#64748B', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              ⏳ De-Prioritized / Long-Term
            </span>
            <span style={{ fontSize: '10px', color: '#475569', fontWeight: 600 }}>Priority Q4</span>
          </div>

          <div style={{ fontSize: '11.5px', color: '#64748B', padding: '8px 0' }}>
            {longTerm.length > 0 ? longTerm.map(i => i.title).join(', ') : 'No low-ROI complex initiatives detected.'}
          </div>
        </div>
      </div>
    </div>
  );
};
