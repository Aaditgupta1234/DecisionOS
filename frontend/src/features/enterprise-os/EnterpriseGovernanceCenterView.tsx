import React, { useState } from 'react';
import {
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Lock,
  Plus,
  ArrowUpRight,
  TrendingUp,
  Sparkles,
  GitMerge,
  Scale,
  Award,
} from 'lucide-react';
import { Link } from 'react-router-dom';

export const EnterpriseGovernanceCenterView: React.FC = () => {
  const [selectedDecision, setSelectedDecision] = useState<string>('DEC-2026-042');
  const [showSimModal, setShowSimModal] = useState(false);

  const decisions = [
    {
      code: 'DEC-2026-042',
      title: 'Southeastern Carrier Route Reallocation & SLA Penalty Enforcement',
      type: 'STRATEGIC',
      owner: 'VP Operations',
      expectedArr: '+$340,000 ARR',
      realizedArr: '+$312,000 ARR',
      accuracy: '91.8%',
      status: 'IMPLEMENTED',
      compliance: 'COMPLIANT',
    },
    {
      code: 'DEC-2026-043',
      title: 'Q2 Dynamic Pricing & Courier Surcharge Hedging',
      type: 'FINANCIAL',
      owner: 'CFO',
      expectedArr: '+$180,000 ARR',
      realizedArr: 'Pending Execution',
      accuracy: '95.2% Conf',
      status: 'APPROVED',
      compliance: 'COMPLIANT',
    },
    {
      code: 'DEC-2026-044',
      title: 'Secondary Regional Fulfillment Node Expansion',
      type: 'BOARD',
      owner: 'CEO',
      expectedArr: '+$850,000 ARR',
      realizedArr: 'Under Review',
      accuracy: '88.0% Conf',
      status: 'UNDER_REVIEW',
      compliance: 'PENDING_AUDIT',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#10B981', fontWeight: 800 }}>
            Decision Governance & Compliance Engine
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Enterprise Decision Registry & Governance Center
          </h1>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => setShowSimModal(true)}
            style={{
              padding: '8px 14px',
              background: 'rgba(56, 189, 248, 0.1)',
              border: '1px solid rgba(56, 189, 248, 0.3)',
              borderRadius: '8px',
              color: '#38BDF8',
              fontSize: '0.8rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <Sparkles size={14} />
            <span>Pre-Simulate Decision Impact</span>
          </button>
        </div>
      </div>

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>GOVERNANCE HEALTH</div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#10B981' }}>98.4%</div>
          <div style={{ fontSize: '0.75rem', color: '#10B981', fontWeight: 700 }}>28 Policy Rules Active • 0 Violations</div>
        </div>

        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>DECISION EFFECTIVENESS</div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#38BDF8' }}>91.8%</div>
          <div style={{ fontSize: '0.75rem', color: '#94A3B8', fontWeight: 700 }}>Realized vs Approved ARR Outcome</div>
        </div>

        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>REALIZED DECISION VALUE</div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#A855F7' }}>+$312,000</div>
          <div style={{ fontSize: '0.75rem', color: '#A855F7', fontWeight: 700 }}>Expected $340,000 ARR</div>
        </div>

        <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <div style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800, textTransform: 'uppercase' }}>BOARD DIRECTIVES</div>
          <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#F59E0B' }}>12 / 12</div>
          <div style={{ fontSize: '0.75rem', color: '#F59E0B', fontWeight: 700 }}>100% Enforced Alignment</div>
        </div>
      </div>

      {/* Decision Registry Table */}
      <div style={{ background: '#090D14', border: '1px solid #1E293B', borderRadius: '14px', overflow: 'hidden' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #1E293B', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '0.88rem', fontWeight: 800, color: '#FFFFFF' }}>Corporate Decision Registry</span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Permanent Institutional Audit Memory</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column' }}>
          {decisions.map((dec) => (
            <div
              key={dec.code}
              style={{
                padding: '20px',
                borderBottom: '1px solid #1E293B',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '14px',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '0.7rem', fontWeight: 800, padding: '2px 8px', borderRadius: '4px', background: 'rgba(16, 185, 129, 0.15)', color: '#10B981' }}>
                    {dec.type}
                  </span>
                  <span style={{ fontSize: '0.95rem', fontWeight: 800, color: '#FFFFFF' }}>
                    {dec.code}: {dec.title}
                  </span>
                </div>
                <div style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '4px' }}>
                  Owner: {dec.owner} • Expected: <strong style={{ color: '#38BDF8' }}>{dec.expectedArr}</strong> • Realized: <strong style={{ color: '#10B981' }}>{dec.realizedArr}</strong> (Accuracy: {dec.accuracy})
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#10B981', background: 'rgba(16, 185, 129, 0.1)', padding: '4px 10px', borderRadius: '6px' }}>
                  {dec.status}
                </span>
                <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#38BDF8', background: 'rgba(56, 189, 248, 0.1)', padding: '4px 10px', borderRadius: '6px' }}>
                  {dec.compliance}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Pre-Simulation Drawer Modal */}
      {showSimModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(6px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
            padding: '20px',
          }}
          onClick={() => setShowSimModal(false)}
        >
          <div
            style={{
              backgroundColor: '#090D14',
              border: '1px solid #1E293B',
              borderRadius: '16px',
              width: '100%',
              maxWidth: '620px',
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF' }}>
              Governance Pre-Simulation Analysis • DEC-2026-043
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '12px', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>EXPECTED ARR REVENUE</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 900, color: '#10B981', marginTop: '2px' }}>+$180,000</div>
              </div>
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '12px', borderRadius: '8px' }}>
                <div style={{ fontSize: '0.65rem', color: '#64748B' }}>EXPECTED RISK DELTA</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 900, color: '#F59E0B', marginTop: '2px' }}>+12.0%</div>
              </div>
            </div>

            <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: '14px', borderRadius: '8px', fontSize: '0.82rem', color: '#F1F5F9' }}>
              <strong style={{ color: '#10B981' }}>Governance Verdict: </strong>
              RECOMMENDED FOR EXECUTIVE APPROVAL. Risk envelope within CFO discretionary authority threshold ($500K max).
            </div>

            <button
              onClick={() => setShowSimModal(false)}
              style={{ padding: '10px', background: '#38BDF8', border: 'none', borderRadius: '8px', color: '#090D14', fontWeight: 800, cursor: 'pointer' }}
            >
              Close Pre-Simulation Analysis
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
