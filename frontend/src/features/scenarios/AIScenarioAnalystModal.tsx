import React, { useState } from 'react';
import { X, Sparkles, Send, ShieldCheck, CheckCircle2, Database, ArrowRight, Bot } from 'lucide-react';

export interface AIScenarioAnalystModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AIScenarioAnalystModal: React.FC<AIScenarioAnalystModalProps> = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState([
    {
      role: 'ASSISTANT',
      content:
        "Hello! I am your AI Scenario Analyst. Ask me about parameter trade-offs, why Scenario A outperforms Scenario B, or how capacity constraints impact your recovery velocity.",
      citations: [
        { label: 'KnowledgeGraphSnapshot V3', type: 'SNAPSHOT' },
        { label: 'StrategicRankingEngine', type: 'RANKING' },
      ],
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userQ = input;
    setMessages((prev) => [...prev, { role: 'USER', content: userQ, citations: [] }]);
    setInput('');
    setIsTyping(true);

    setTimeout(() => {
      setIsTyping(false);
      setMessages((prev) => [
        ...prev,
        {
          role: 'ASSISTANT',
          content:
            "**Strategic Recommendation: Retention First**\n\n• **Expected ARR:** +$124,000 with 4.8x ROI multiplier.\n• **Causal Driver:** Root Cause #4 (Secondary Hub Bottleneck) is resolved by enforcing 15% courier SLA penalties, dropping latency from 5.4d to 3.4d.\n• **Why it beats Scenario B:** Scenario B requires $30.5K in paid ads but only yields +$98K ARR due to existing courier churn leakage. Retention First fixes the leak first before scaling.",
          citations: [
            { label: 'RootCauseEngine #4', type: 'ROOT_CAUSE' },
            { label: 'RecommendationEngine #1', type: 'RECOMMENDATION' },
            { label: 'ForecastEngine V3', type: 'FORECAST' },
          ],
        },
      ]);
    }, 800);
  };

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.85)',
        backdropFilter: 'blur(8px)',
        zIndex: 300,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
        animation: 'fadeIn 0.15s ease',
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: '740px',
          maxWidth: '94vw',
          backgroundColor: '#090D14',
          border: '1px solid #1E293B',
          borderRadius: '16px',
          boxShadow: '0 25px 60px rgba(0,0,0,0.95)',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
          height: '620px',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px 24px', borderBottom: '1px solid #1E293B', background: '#070A0F' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'linear-gradient(135deg, #7C3AED 0%, #2563EB 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Bot size={18} color="#FFFFFF" />
            </div>
            <div>
              <span style={{ fontSize: '0.72rem', color: '#A855F7', textTransform: 'uppercase', fontWeight: 800 }}>
                AI Scenario Analyst & Narrative Engine
              </span>
              <div style={{ fontSize: '0.95rem', fontWeight: 800, color: '#FFFFFF' }}>Explainable Scenario Reasoning</div>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{ background: 'rgba(30, 41, 59, 0.6)', border: '1px solid #334155', color: '#94A3B8', borderRadius: '6px', padding: '6px', cursor: 'pointer' }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Chat History */}
        <div style={{ flex: 1, padding: '20px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {messages.map((m, idx) => (
            <div
              key={idx}
              style={{
                alignSelf: m.role === 'USER' ? 'flex-end' : 'flex-start',
                maxWidth: '85%',
                background: m.role === 'USER' ? '#0284C7' : 'rgba(15, 23, 42, 0.8)',
                border: m.role === 'USER' ? 'none' : '1px solid #1E293B',
                borderRadius: '12px',
                padding: '14px 18px',
                color: '#FFFFFF',
                fontSize: '0.88rem',
                lineHeight: 1.5,
              }}
            >
              <div style={{ whiteSpace: 'pre-wrap' }}>{m.content}</div>

              {m.citations && m.citations.length > 0 && (
                <div style={{ marginTop: '10px', paddingTop: '8px', borderTop: '1px solid rgba(255,255,255,0.1)', display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  <span style={{ fontSize: '0.7rem', color: '#A855F7', fontWeight: 700 }}>Sources:</span>
                  {m.citations.map((c, cIdx) => (
                    <span key={cIdx} style={{ fontSize: '0.7rem', color: '#38BDF8', background: 'rgba(56, 189, 248, 0.15)', padding: '1px 6px', borderRadius: '4px' }}>
                      • {c.label}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}

          {isTyping && (
            <div style={{ alignSelf: 'flex-start', padding: '10px 16px', background: 'rgba(15, 23, 42, 0.8)', borderRadius: '10px', fontSize: '0.8rem', color: '#94A3B8' }}>
              Analyst is reasoning over Digital Twin and causal DAG...
            </div>
          )}
        </div>

        {/* Input Bar */}
        <form onSubmit={handleSend} style={{ padding: '16px 20px', background: '#070A0F', borderTop: '1px solid #1E293B', display: 'flex', gap: '10px' }}>
          <input
            type="text"
            placeholder="Ask: Why does Scenario A outperform Scenario B?"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            style={{
              flex: 1,
              padding: '10px 14px',
              background: 'rgba(15, 23, 42, 0.8)',
              border: '1px solid #1E293B',
              borderRadius: '8px',
              color: '#FFFFFF',
              fontSize: '0.85rem',
              outline: 'none',
            }}
          />
          <button
            type="submit"
            style={{
              padding: '10px 16px',
              background: '#0284C7',
              border: 'none',
              borderRadius: '8px',
              color: '#FFFFFF',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <Send size={14} />
            <span>Send</span>
          </button>
        </form>
      </div>
    </div>
  );
};
