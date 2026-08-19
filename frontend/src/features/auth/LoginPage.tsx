import React, { useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useAuth } from './AuthContext';
import { Lock, Mail, ArrowRight, ShieldCheck, AlertCircle, Sparkles } from 'lucide-react';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const redirectPath = searchParams.get('redirect') || '/dashboard';
  const { login } = useAuth();
  const { status: backendStatus } = useBackendHealth();

  const [email, setEmail] = useState('executive@decisionos.ai');
  const [password, setPassword] = useState('decisionos123');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      await login(email, password);
      navigate(redirectPath, { replace: true });
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify your credentials.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleQuickFill = (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setError(null);
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: '#040609',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '24px',
      color: '#FFFFFF',
      fontFamily: 'Inter, system-ui, sans-serif',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Background Radial Glow */}
      <div style={{
        position: 'absolute',
        top: '20%',
        left: '50%',
        transform: 'translateX(-50%)',
        width: '600px',
        height: '400px',
        background: 'radial-gradient(circle, rgba(56, 189, 248, 0.08) 0%, rgba(0,0,0,0) 70%)',
        pointerEvents: 'none',
        zIndex: 0,
      }} />

      <div style={{
        maxWidth: '440px',
        width: '100%',
        background: 'rgba(9, 12, 18, 0.85)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '16px',
        padding: '36px 32px',
        boxShadow: '0 25px 60px -15px rgba(0, 0, 0, 0.9)',
        backdropFilter: 'blur(20px)',
        position: 'relative',
        zIndex: 1,
      }}>
        {/* Brand Header */}
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #1D4ED8, #0284C7)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 16px rgba(56, 189, 248, 0.35)',
            }}>
              <ShieldCheck size={18} color="#FFFFFF" />
            </div>
            <span style={{ fontSize: '20px', fontWeight: 800, letterSpacing: '-0.03em', color: '#FFFFFF' }}>
              DecisionOS
            </span>
          </div>

          <h1 style={{ fontSize: '20px', fontWeight: 700, letterSpacing: '-0.02em', marginBottom: '6px' }}>
            Executive Platform Access
          </h1>
          <p style={{ fontSize: '12.5px', color: '#94A3B8' }}>
            Sign in to access your organization's decision intelligence engine
          </p>
        </div>

        {/* Backend Connectivity Status */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: backendStatus === 'connected' ? 'rgba(16, 185, 129, 0.08)' : 'rgba(239, 68, 68, 0.08)',
          border: `1px solid ${backendStatus === 'connected' ? 'rgba(16, 185, 129, 0.22)' : 'rgba(239, 68, 68, 0.25)'}`,
          padding: '6px 12px',
          borderRadius: '8px',
          marginBottom: '20px',
          fontSize: '11.5px',
        }}>
          <span style={{ color: '#94A3B8' }}>Backend Gateway</span>
          <span style={{
            color: backendStatus === 'connected' ? '#10B981' : '#EF4444',
            fontWeight: 700,
            display: 'flex',
            alignItems: 'center',
            gap: '5px',
          }}>
            <span>●</span>
            <span>{backendStatus === 'connected' ? 'Connected (Port 8000)' : 'Offline / Unreachable'}</span>
          </span>
        </div>

        {/* Error Alert */}
        {error && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.12)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '8px',
            padding: '10px 14px',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '8px',
            fontSize: '12px',
            color: '#F87171',
          }}>
            <AlertCircle size={15} style={{ flexShrink: 0, marginTop: '2px' }} />
            <span>{error}</span>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '11.5px', fontWeight: 600, color: '#CBD5E1', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Work Email
            </label>
            <div style={{ position: 'relative' }}>
              <Mail size={15} color="#64748B" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="executive@decisionos.ai"
                style={{
                  width: '100%',
                  background: '#04060A',
                  border: '1px solid #1E293B',
                  borderRadius: '8px',
                  padding: '10px 12px 10px 36px',
                  fontSize: '13px',
                  color: '#FFFFFF',
                  outline: 'none',
                  boxSizing: 'border-box',
                }}
              />
            </div>
          </div>

          <div style={{ marginBottom: '22px' }}>
            <label style={{ display: 'block', fontSize: '11.5px', fontWeight: 600, color: '#CBD5E1', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <Lock size={15} color="#64748B" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                style={{
                  width: '100%',
                  background: '#04060A',
                  border: '1px solid #1E293B',
                  borderRadius: '8px',
                  padding: '10px 12px 10px 36px',
                  fontSize: '13px',
                  color: '#FFFFFF',
                  outline: 'none',
                  boxSizing: 'border-box',
                }}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            style={{
              width: '100%',
              background: '#1D4ED8',
              border: '1px solid #3B82F6',
              borderRadius: '8px',
              padding: '11px',
              fontSize: '13.5px',
              fontWeight: 700,
              color: '#FFFFFF',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              cursor: submitting ? 'not-allowed' : 'pointer',
              opacity: submitting ? 0.7 : 1,
              transition: 'all 0.15s ease',
              boxShadow: '0 0 16px rgba(59, 130, 246, 0.3)',
            }}
          >
            <span>{submitting ? 'Authenticating...' : 'Sign In to DecisionOS'}</span>
            <ArrowRight size={15} />
          </button>
        </form>

        {/* Quick Demo Credentials Fill */}
        <div style={{
          marginTop: '24px',
          paddingTop: '18px',
          borderTop: '1px solid #141A24',
          textAlign: 'center',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '5px', fontSize: '11px', color: '#64748B', marginBottom: '8px' }}>
            <Sparkles size={11} color="#38BDF8" />
            <span>FastAPI Credentials</span>
          </div>

          <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
            <button
              type="button"
              onClick={() => handleQuickFill('executive@decisionos.ai', 'decisionos123')}
              style={{
                background: '#0C1017',
                border: '1px solid #1F2937',
                color: '#94A3B8',
                padding: '4px 10px',
                borderRadius: '5px',
                fontSize: '11px',
                cursor: 'pointer',
              }}
            >
              Executive (Admin)
            </button>

            <button
              type="button"
              onClick={() => handleQuickFill('analyst@decisionos.ai', 'analyst123')}
              style={{
                background: '#0C1017',
                border: '1px solid #1F2937',
                color: '#94A3B8',
                padding: '4px 10px',
                borderRadius: '5px',
                fontSize: '11px',
                cursor: 'pointer',
              }}
            >
              Analyst User
            </button>
          </div>
        </div>

        {/* Home Navigation link */}
        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          <Link to="/" style={{ fontSize: '12px', color: '#64748B', textDecoration: 'none' }}>
            ← Back to Marketing Overview
          </Link>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
