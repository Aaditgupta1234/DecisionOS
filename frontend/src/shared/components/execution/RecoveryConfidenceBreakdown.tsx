import React from 'react';
import { ShieldCheck, ShieldAlert, Zap, Lock, Calculator, CheckCircle2 } from 'lucide-react';
import { RecoveryConfidenceEngine } from '../../utils/RecoveryConfidenceEngine';

interface Props {
  highConfidence?: string;
  mediumConfidence?: string;
  lowConfidence?: string;
  totalOpportunity?: string;
}

export const RecoveryConfidenceBreakdown: React.FC<Props> = ({
  highConfidence = '+$220K ARR (Guaranteed Upside)',
  mediumConfidence = '+$180K ARR (Likely Upside)',
  lowConfidence = '+$80K ARR (Speculative Upside)',
  totalOpportunity = '+$480K ARR Total',
}) => {
  const calc = RecoveryConfidenceEngine.calculateConfidence(0.89, 0.94, 0.80, 0.97);

  return (
    <div style={{
      background: '#090C12',
      border: '1px solid #1A2230',
      borderRadius: '12px',
      padding: '20px',
      marginBottom: '24px',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '2px' }}>
            <Calculator size={14} color="#38BDF8" />
            <span style={{ fontSize: '10.5px', fontWeight: 800, color: '#38BDF8', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Deterministic Recovery Confidence Engine ({calc.formulaVersion})
            </span>
          </div>
          <h4 style={{ fontSize: '14.5px', fontWeight: 800, color: '#FFFFFF', margin: 0, textTransform: 'uppercase' }}>
            Recovery Upside Confidence Segmentation & Mathematical Breakdown
          </h4>
        </div>

        <div style={{
          background: 'rgba(16, 185, 129, 0.12)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          color: '#10B981',
          padding: '3px 10px',
          borderRadius: '6px',
          fontSize: '12px',
          fontWeight: 800,
        }}>
          {totalOpportunity}
        </div>
      </div>

      {/* 3-Tier Segmentation Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '16px' }}>
        <div style={{ background: '#05070B', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', padding: '12px 14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#10B981', fontSize: '10.5px', fontWeight: 800, textTransform: 'uppercase', marginBottom: '2px' }}>
            <Lock size={12} />
            <span>High Confidence (&gt;80%)</span>
          </div>
          <div style={{ fontSize: '15px', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>
            {highConfidence}
          </div>
          <span style={{ fontSize: '10.5px', color: '#94A3B8' }}>Courier SLA & Win-Back core</span>
        </div>

        <div style={{ background: '#05070B', border: '1px solid rgba(56, 189, 248, 0.3)', borderRadius: '8px', padding: '12px 14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#38BDF8', fontSize: '10.5px', fontWeight: 800, textTransform: 'uppercase', marginBottom: '2px' }}>
            <Zap size={12} />
            <span>Medium Confidence (50–80%)</span>
          </div>
          <div style={{ fontSize: '15px', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>
            {mediumConfidence}
          </div>
          <span style={{ fontSize: '10.5px', color: '#94A3B8' }}>Multi-hub dispatch balancing</span>
        </div>

        <div style={{ background: '#05070B', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: '8px', padding: '12px 14px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px', color: '#F59E0B', fontSize: '10.5px', fontWeight: 800, textTransform: 'uppercase', marginBottom: '2px' }}>
            <ShieldAlert size={12} />
            <span>Low / Speculative (&lt;50%)</span>
          </div>
          <div style={{ fontSize: '15px', fontWeight: 800, color: '#FFFFFF', marginTop: '2px' }}>
            {lowConfidence}
          </div>
          <span style={{ fontSize: '10.5px', color: '#94A3B8' }}>Cross-sell attachment beta</span>
        </div>
      </div>

      {/* Mathematical Factor Formula Bar */}
      <div style={{
        background: '#05070B',
        border: '1px solid #141C28',
        borderRadius: '8px',
        padding: '12px 16px',
        marginBottom: '14px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
          <span style={{ fontSize: '11px', color: '#94A3B8', fontWeight: 700, textTransform: 'uppercase' }}>
            Mathematical Derivation (Confidence = Certainty × Reliability × Velocity × Quality)
          </span>
          <span style={{ fontSize: '12px', color: '#38BDF8', fontWeight: 800, fontFamily: 'monospace' }}>
            {calc.score}% Composite Score
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#CBD5E1', flexWrap: 'wrap' }}>
          <span style={{ color: '#10B981', fontWeight: 700 }}>89% (Root Cause)</span>
          <span style={{ color: '#64748B' }}>×</span>
          <span style={{ color: '#38BDF8', fontWeight: 700 }}>94% (Rec Reliability)</span>
          <span style={{ color: '#64748B' }}>×</span>
          <span style={{ color: '#F59E0B', fontWeight: 700 }}>80% (Execution Progress)</span>
          <span style={{ color: '#64748B' }}>×</span>
          <span style={{ color: '#A855F7', fontWeight: 700 }}>97% (Data Quality)</span>
          <span style={{ color: '#64748B' }}>=</span>
          <strong style={{ color: '#FFFFFF' }}>64.9% Realization Probability ({calc.tier} Confidence)</strong>
        </div>
      </div>

      {/* Plain-Language Executive Confidence Reasoning Bullets */}
      <div style={{ background: '#04060A', border: '1px solid #101620', borderRadius: '8px', padding: '12px 16px' }}>
        <span style={{ fontSize: '10.5px', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', display: 'block', marginBottom: '6px' }}>
          Plain-Language Executive Confidence Reasoning
        </span>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {calc.explanationBullets.map((bullet, idx) => (
            <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11.5px', color: '#CBD5E1' }}>
              <CheckCircle2 size={12} color="#10B981" />
              <span>{bullet}</span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
