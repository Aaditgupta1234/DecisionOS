import React from 'react';
import { Bot, User, ShieldCheck, GitMerge, Zap, Sparkles } from 'lucide-react';
import { TraceabilityBadge } from './TraceabilityBadge';
import { ReasoningChain } from './ReasoningChain';
import { SourceNavigator } from './SourceNavigator';
import { SuggestedFollowUps } from './SuggestedFollowUps';
import { UnsupportedQuestionCard } from './UnsupportedQuestionCard';

export type AnswerType = 'ROOT_CAUSE' | 'KPI_EXPLANATION' | 'RECOMMENDATION' | 'EXECUTIVE_SUMMARY' | 'RISK_ASSESSMENT' | 'UNSUPPORTED';

export interface GroundedChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  answerType?: AnswerType;
  traceId?: string;
  verifiedFacts?: { label: string; value: string }[];
  aiInterpretation?: string;
  reasoningSteps?: string[];
  confidence?: number;
  sources?: {
    metrics?: { label: string; key: string }[];
    findings?: { label: string; id: string }[];
    rootCauses?: { label: string; id: string }[];
    recommendations?: { label: string; id: string }[];
  };
  followUps?: string[];
  isUnsupported?: boolean;
}

interface Props {
  message: GroundedChatMessage;
  onSelectFollowUp?: (prompt: string) => void;
}

export const ChatMessage: React.FC<Props> = ({ message, onSelectFollowUp }) => {
  const isUser = message.role === 'user';

  const getAnswerTypeBadge = (type?: AnswerType) => {
    switch (type) {
      case 'ROOT_CAUSE':
        return { label: 'ROOT CAUSE ANALYSIS', color: '#F59E0B' };
      case 'KPI_EXPLANATION':
        return { label: 'KPI EXPLANATION', color: '#38BDF8' };
      case 'RECOMMENDATION':
        return { label: 'RECOMMENDATION ANALYSIS', color: '#10B981' };
      case 'RISK_ASSESSMENT':
        return { label: 'RISK ASSESSMENT', color: '#EF4444' };
      case 'EXECUTIVE_SUMMARY':
      default:
        return { label: 'EXECUTIVE SUMMARY', color: '#38BDF8' };
    }
  };

  const badge = getAnswerTypeBadge(message.answerType);

  return (
    <div style={{
      display: 'flex',
      gap: '14px',
      marginBottom: '24px',
      alignItems: 'flex-start',
    }}>
      {/* Avatar Icon */}
      <div style={{
        width: '32px',
        height: '32px',
        borderRadius: '8px',
        background: isUser ? '#1D4ED8' : '#0B111A',
        border: `1px solid ${isUser ? '#3B82F6' : '#1E293B'}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
        marginTop: '2px',
      }}>
        {isUser ? <User size={16} color="#FFFFFF" /> : <Bot size={16} color="#38BDF8" />}
      </div>

      {/* Message Content Bubble */}
      <div style={{
        flex: 1,
        background: isUser ? '#070A10' : '#090C12',
        border: `1px solid ${isUser ? '#1E293B' : '#141C28'}`,
        borderRadius: '10px',
        padding: '16px 18px',
        color: '#FFFFFF',
        fontSize: '13px',
        lineHeight: 1.6,
      }}>
        {/* Message Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontWeight: 800, fontSize: '12px', color: isUser ? '#38BDF8' : '#FFFFFF' }}>
              {isUser ? 'Executive Operator' : 'DecisionOS Intelligence Analyst'}
            </span>

            {!isUser && message.answerType && !message.isUnsupported && (
              <span style={{
                fontSize: '9.5px',
                fontWeight: 800,
                color: badge.color,
                background: 'rgba(255, 255, 255, 0.04)',
                border: `1px solid ${badge.color}40`,
                padding: '1px 6px',
                borderRadius: '4px',
              }}>
                [{badge.label}]
              </span>
            )}
          </div>

          <span style={{ fontSize: '11px', color: '#64748B' }}>
            {message.timestamp}
          </span>
        </div>

        {/* Unsupported Query Guard */}
        {message.isUnsupported ? (
          <UnsupportedQuestionCard />
        ) : (
          <div>
            {/* User Message Simple Text */}
            {isUser ? (
              <div style={{ color: '#E2E8F0', fontWeight: 500 }}>
                {message.content}
              </div>
            ) : (
              <div>
                {/* 1. Verified Facts Container */}
                {message.verifiedFacts && message.verifiedFacts.length > 0 && (
                  <div style={{
                    background: '#04070D',
                    border: '1px solid #141D2B',
                    borderRadius: '6px',
                    padding: '10px 12px',
                    marginBottom: '12px',
                  }}>
                    <div style={{ fontSize: '10px', color: '#64748B', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '6px' }}>
                      Deterministic Verified Telemetry Facts:
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '6px', fontSize: '11.5px' }}>
                      {message.verifiedFacts.map((fact, idx) => (
                        <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', color: '#CBD5E1' }}>
                          <span style={{ color: '#94A3B8' }}>{fact.label}:</span>
                          <strong style={{ color: '#FFFFFF' }}>{fact.value}</strong>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 2. AI Strategic Interpretation */}
                <div style={{ color: '#E2E8F0', lineHeight: 1.6, marginBottom: '10px' }}>
                  {message.aiInterpretation || message.content}
                </div>

                {/* 3. Why This Answer? Reasoning Chain */}
                {message.reasoningSteps && message.reasoningSteps.length > 0 && (
                  <ReasoningChain steps={message.reasoningSteps} confidence={message.confidence} />
                )}

                {/* 4. Interactive Source Navigator */}
                {message.sources && (
                  <SourceNavigator
                    metrics={message.sources.metrics}
                    findings={message.sources.findings}
                    rootCauses={message.sources.rootCauses}
                    recommendations={message.sources.recommendations}
                  />
                )}

                {/* 5. Response Traceability ID */}
                <div style={{ marginTop: '12px' }}>
                  <TraceabilityBadge traceId={message.traceId} />
                </div>

                {/* 6. Dynamic Suggested Follow-Ups */}
                {message.followUps && message.followUps.length > 0 && (
                  <SuggestedFollowUps suggestions={message.followUps} onSelect={onSelectFollowUp} />
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
