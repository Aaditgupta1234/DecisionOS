import React, { useState } from 'react';
import { Modal } from '../../design-system/Modal';
import { Button } from '../../design-system/Button';
import { CheckCircle2, ArrowRight, Sparkles, Building2, Users, Database, Activity, Bot } from 'lucide-react';

interface OnboardingWizardModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const OnboardingWizardModal: React.FC<OnboardingWizardModalProps> = ({ isOpen, onClose }) => {
  const [step, setStep] = useState(1);

  const steps = [
    { num: 1, title: 'Create Organization', icon: <Building2 size={16} /> },
    { num: 2, title: 'Portfolio Hierarchy', icon: <Users size={16} /> },
    { num: 3, title: 'Ingest Live Telemetry', icon: <Database size={16} /> },
    { num: 4, title: 'Run Causal Diagnostics', icon: <Activity size={16} /> },
    { num: 5, title: 'Deploy Autonomous Agents', icon: <Bot size={16} /> },
  ];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Enterprise DecisionOS Guided Setup" subtitle="Step-by-step enterprise SaaS productization wizard">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {/* Progress Bar */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'relative' }}>
          {steps.map((s) => (
            <div
              key={s.num}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '6px',
                zIndex: 1,
              }}
            >
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: step >= s.num ? '#10B981' : '#1E293B',
                  color: step >= s.num ? '#090D14' : '#64748B',
                  fontWeight: 800,
                  fontSize: '0.8rem',
                }}
              >
                {step > s.num ? <CheckCircle2 size={16} /> : s.num}
              </div>
              <span style={{ fontSize: '0.68rem', color: step >= s.num ? '#FFFFFF' : '#64748B', fontWeight: 700 }}>
                {s.title}
              </span>
            </div>
          ))}
        </div>

        {/* Step Content */}
        <div style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid #1E293B', borderRadius: '12px', padding: '24px' }}>
          {step === 1 && (
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF', margin: '0 0 8px 0' }}>Configure Multi-Tenant Organization</h3>
              <p style={{ fontSize: '0.82rem', color: '#94A3B8' }}>Apex Global Technologies Group created with Enterprise Pro Tier.</p>
            </div>
          )}
          {step === 2 && (
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF', margin: '0 0 8px 0' }}>Multi-Portfolio Hierarchy Initialized</h3>
              <p style={{ fontSize: '0.82rem', color: '#94A3B8' }}>Configured North America, Europe, and APAC regional divisions with capital allocation tracking.</p>
            </div>
          )}
          {step === 3 && (
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF', margin: '0 0 8px 0' }}>Enterprise Dataset Ingested</h3>
              <p style={{ fontSize: '0.82rem', color: '#94A3B8' }}>32 KPIs mapped with automated formula validation and schema verification.</p>
            </div>
          )}
          {step === 4 && (
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF', margin: '0 0 8px 0' }}>Deterministic Causal Diagnostics Complete</h3>
              <p style={{ fontSize: '0.82rem', color: '#94A3B8' }}>Identified primary APAC Logistics drag (-$140K) and Southeastern courier SLA transit bottlenecks.</p>
            </div>
          )}
          {step === 5 && (
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF', margin: '0 0 8px 0' }}>Autonomous Enterprise Agents Ready</h3>
              <p style={{ fontSize: '0.82rem', color: '#94A3B8' }}>6 Specialized Enterprise Agents deployed and guarded by human approval gates.</p>
            </div>
          )}
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Button variant="ghost" size="sm" onClick={onClose}>
            Skip Tutorial
          </Button>
          {step < 5 ? (
            <Button variant="primary" size="sm" onClick={() => setStep((s) => s + 1)}>
              Continue to Step {step + 1} →
            </Button>
          ) : (
            <Button variant="primary" size="sm" onClick={onClose}>
              Complete Onboarding & Enter Command Center
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
};
