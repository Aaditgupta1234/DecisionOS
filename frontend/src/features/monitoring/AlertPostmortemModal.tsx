import React from 'react';
import { X, BookOpen, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react';

interface AlertPostmortemModalProps {
  isOpen: boolean;
  onClose: () => void;
  alertCode: string;
}

export const AlertPostmortemModal: React.FC<AlertPostmortemModalProps> = ({
  isOpen,
  onClose,
  alertCode,
}) => {
  if (!isOpen) return null;

  return (
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
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: '#090D14',
          border: '1px solid #1E293B',
          borderRadius: '16px',
          width: '100%',
          maxWidth: '680px',
          overflow: 'hidden',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.7)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ padding: '20px 24px', borderBottom: '1px solid #1E293B', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BookOpen size={18} color="#A855F7" />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
              Institutional Incident Postmortem • {alertCode}
            </h3>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#64748B', cursor: 'pointer' }}>
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px', maxHeight: '80vh', overflowY: 'auto' }}>
          <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', padding: '14px', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.72rem', fontWeight: 800, color: '#64748B', textTransform: 'uppercase' }}>ROOT CAUSE SUMMARY</div>
            <div style={{ fontSize: '0.85rem', color: '#FFFFFF', fontWeight: 700, marginTop: '4px' }}>
              Southeastern carrier transit delay cascading into -6.0% customer retention dip.
            </div>
          </div>

          <div>
            <div style={{ fontSize: '0.78rem', fontWeight: 800, color: '#38BDF8', marginBottom: '6px' }}>WHAT & WHY IT HAPPENED</div>
            <div style={{ fontSize: '0.82rem', color: '#94A3B8', lineHeight: 1.4 }}>
              Secondary carrier parcel throughput dropped by 38% over a 48-hour window due to localized weather disruption. The Secondary Hub lacked dynamic automated load shedding to auxiliary northern fulfillment nodes.
            </div>
          </div>

          <div>
            <div style={{ fontSize: '0.78rem', fontWeight: 800, color: '#10B981', marginBottom: '6px' }}>WHAT WAS DONE</div>
            <div style={{ fontSize: '0.82rem', color: '#94A3B8', lineHeight: 1.4 }}>
              Enforced 15% courier SLA penalties and rerouted 40% of parcel volume to regional express partners.
            </div>
          </div>

          <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.2)', padding: '14px', borderRadius: '8px' }}>
            <div style={{ fontSize: '0.72rem', fontWeight: 800, color: '#10B981', textTransform: 'uppercase', marginBottom: '4px' }}>
              INSTITUTIONAL LESSONS LEARNED
            </div>
            <div style={{ fontSize: '0.8rem', color: '#F1F5F9' }}>
              • Carrier SLA enforcement must pair with automated route failover within 2 hours.<br />
              • Customer win-back delivery delay tokens prevented <strong>$126,000 in projected ARR loss</strong>.
            </div>
          </div>

          <div>
            <div style={{ fontSize: '0.78rem', fontWeight: 800, color: '#F59E0B', marginBottom: '6px' }}>PREVENTIVE ACTION CHECKLIST</div>
            <div style={{ fontSize: '0.8rem', color: '#94A3B8', display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <div>☑ Deploy real-time carrier throughput load-balancer in all 12 regional hubs.</div>
              <div>☑ Configure 15-minute response SLA escalation rule for tier-1 transit corridors.</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
