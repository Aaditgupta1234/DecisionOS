import React, { useEffect, useState, useRef } from 'react';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { ChatMessage, ChatSession } from '../../types';
import { LoadingSkeleton } from '../../components/feedback/LoadingSkeleton';
import { ErrorBanner } from '../../components/feedback/ErrorBanner';
import { EmptyState } from '../../components/feedback/EmptyState';
import { MessageSquare, Send, Plus, Sparkles, Bot, User as UserIcon, ShieldCheck } from 'lucide-react';
import { FadeIn } from '../../design-system/motion';

export const ChatView: React.FC = () => {
  const { activeDataset } = useDataset();
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSession, setActiveSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState<string>('');
  const [loadingSessions, setLoadingSessions] = useState<boolean>(true);
  const [isSending, setIsSending] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestedPrompts = [
    'How healthy is my company?',
    'What is my biggest business risk?',
    'Why is revenue declining?',
    'What should I fix first?',
  ];

  const fetchSessions = async (datasetId: string) => {
    try {
      setLoadingSessions(true);
      setError(null);
      const data = await DecisionApi.listChatSessions(datasetId);
      const list = Array.isArray(data) ? data : [];
      setSessions(list);

      if (list.length > 0) {
        setActiveSession(list[0]);
        fetchMessages(list[0].id);
      } else {
        // Create initial session if none exists
        handleCreateSession(datasetId);
      }
    } catch (err: any) {
      console.error('Failed to load chat sessions:', err);
      setError(err?.message || 'Could not fetch chat sessions.');
    } finally {
      setLoadingSessions(false);
    }
  };

  const handleCreateSession = async (datasetId: string) => {
    try {
      const newSession = await DecisionApi.createChatSession(datasetId, 'Executive Investigation');
      setSessions([newSession, ...sessions]);
      setActiveSession(newSession);
      setMessages([]);
    } catch (err) {
      console.error('Failed to create chat session:', err);
    }
  };

  const fetchMessages = async (sessionId: string) => {
    try {
      const data = await DecisionApi.listChatMessages(sessionId);
      setMessages(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to load messages:', err);
    }
  };

  const handleSendMessage = async (textToSend?: string) => {
    const text = (textToSend || inputText).trim();
    if (!text || !activeSession) return;

    setInputText('');
    const tempUserMsg: ChatMessage = {
      id: `temp-${Date.now()}`,
      session_id: activeSession.id,
      role: 'USER',
      content: text,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      setIsSending(true);
      const response: any = await DecisionApi.sendChatMessage(activeSession.id, text);
      const responseMsg: ChatMessage = response?.assistant_message || response || {
        id: `ast-${Date.now()}`,
        session_id: activeSession.id,
        role: 'ASSISTANT',
        content: response?.answer || 'Response generated.',
        created_at: new Date().toISOString(),
        citations: response?.citations,
      };
      setMessages((prev) => [...prev, responseMsg]);
    } catch (err: any) {
      console.error('Chat response error:', err);
      const errorReply: ChatMessage = {
        id: `err-${Date.now()}`,
        session_id: activeSession.id,
        role: 'ASSISTANT',
        content: `Sorry, I encountered an issue analyzing your request: ${err?.message || 'Unknown error'}.`,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorReply]);
    } finally {
      setIsSending(false);
    }
  };

  useEffect(() => {
    if (activeDataset?.id) {
      fetchSessions(activeDataset.id);
    }
  }, [activeDataset?.id]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  if (!activeDataset) {
    return (
      <div className="page-container">
        <EmptyState
          title="No Active Dataset Selected"
          description="Select a dataset to converse with the grounded AI Business Analyst."
          icon={MessageSquare}
        />
      </div>
    );
  }

  // Helper to render citation badges
  const renderCitations = (citations: any) => {
    if (!citations) return null;
    let items: Array<{ type: string; title: string }> = [];

    if (Array.isArray(citations)) {
      items = citations.map(c => ({
        type: typeof c === 'string' ? 'Source' : (c.type || c.artifact_type || 'Source'),
        title: typeof c === 'string' ? c : (c.title || c.id || 'Reference'),
      }));
    } else if (typeof citations === 'object') {
      const categories = ['findings', 'root_causes', 'recommendations', 'forecasts', 'scenarios'];
      for (const cat of categories) {
        if (Array.isArray(citations[cat])) {
          for (const c of citations[cat]) {
            items.push({
              type: cat.replace('_', ' ').slice(0, -1).toUpperCase(),
              title: c.title || c.id || 'Artifact',
            });
          }
        }
      }
    }

    if (items.length === 0) return null;

    return (
      <div style={{ marginTop: '10px', paddingTop: '8px', borderTop: '1px solid rgba(255, 255, 255, 0.15)', fontSize: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
          <ShieldCheck size={12} color="var(--color-ai-light)" />
          <span style={{ color: 'var(--color-ai-light)', fontWeight: 600 }}>Grounded Citations:</span>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
          {items.map((c, i) => (
            <span key={i} className="badge badge-neutral" style={{ fontSize: '0.68rem', padding: '2px 8px' }}>
              <strong>{c.type}:</strong> {c.title}
            </span>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="page-container" style={{ height: 'calc(100vh - var(--header-height))', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-ai">Grounded Intelligence</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--color-ai-light)' }}>
              100% Deterministic Platform Telemetry
            </span>
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '2px 0 0 0' }}>AI Business Analyst</h1>
        </div>

        <button
          onClick={() => activeDataset && handleCreateSession(activeDataset.id)}
          className="btn btn-secondary btn-sm"
        >
          <Plus size={14} />
          <span>New Session</span>
        </button>
      </div>

      {error && <ErrorBanner message={error} />}

      {/* Main Chat Interface */}
      <div
        style={{
          flex: 1,
          display: 'flex',
          gap: '16px',
          minHeight: 0,
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-lg)',
          overflow: 'hidden',
        }}
      >
        {/* Sessions Sidebar */}
        <div
          style={{
            width: '240px',
            borderRight: '1px solid var(--border-subtle)',
            backgroundColor: 'var(--bg-app)',
            display: 'flex',
            flexDirection: 'column',
            overflowY: 'auto',
            padding: '12px',
          }}
        >
          <span style={{ fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '8px' }}>
            Investigation Sessions
          </span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {sessions.map((s) => {
              const isSelected = activeSession?.id === s.id;
              return (
                <div
                  key={s.id}
                  onClick={() => {
                    setActiveSession(s);
                    fetchMessages(s.id);
                  }}
                  style={{
                    padding: '8px 10px',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.8rem',
                    cursor: 'pointer',
                    backgroundColor: isSelected ? 'var(--color-ai-subtle)' : 'transparent',
                    color: isSelected ? 'var(--color-ai-light)' : 'var(--text-secondary)',
                    fontWeight: isSelected ? 600 : 400,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {s.title}
                </div>
              );
            })}
          </div>
        </div>

        {/* Message Thread & Input */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
          {/* Thread Scroll Area */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {messages.length === 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', textAlign: 'center' }}>
                <div style={{ width: '48px', height: '48px', borderRadius: '50%', background: 'rgba(56, 189, 248, 0.1)', border: '1px solid rgba(56, 189, 248, 0.25)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '14px' }}>
                  <Bot size={26} color="#38BDF8" />
                </div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 800, marginBottom: '6px', color: '#FFFFFF' }}>DEX Analyst</h3>
                <p style={{ fontSize: '0.85rem', color: '#94A3B8', maxWidth: '440px', marginBottom: '20px' }}>
                  Ask natural-language questions about health scores, diagnosed risks, root causes, and actionable recommendations.
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', width: '100%', maxWidth: '440px' }}>
                  {suggestedPrompts.map((prompt, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSendMessage(prompt)}
                      className="executive-motion-btn"
                      style={{
                        textAlign: 'left',
                        justifyContent: 'flex-start',
                        padding: '10px 14px',
                        background: '#090D14',
                        border: '1px solid #1A2230',
                        borderRadius: '8px',
                        color: '#E2E8F0',
                        fontSize: '0.82rem',
                        fontWeight: 600,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                      }}
                    >
                      <Sparkles size={14} color="#38BDF8" className="btn-icon-wrapper left" />
                      <span>{prompt}</span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((m) => {
                const isUser = m.role === 'USER';
                return (
                  <FadeIn
                    key={m.id}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: isUser ? 'flex-end' : 'flex-start',
                      width: '100%',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px', fontSize: '0.7rem', color: '#64748B' }}>
                      {isUser ? <UserIcon size={12} /> : <Bot size={12} color="#38BDF8" />}
                      <span>{isUser ? 'You' : 'DEX Analyst'}</span>
                    </div>

                    <div
                      style={{
                        maxWidth: '80%',
                        padding: '12px 16px',
                        borderRadius: '8px',
                        backgroundColor: isUser ? '#0284C7' : '#080C14',
                        border: `1px solid ${isUser ? 'transparent' : '#1A2230'}`,
                        color: '#ffffff',
                        fontSize: '0.88rem',
                        lineHeight: 1.6,
                        whiteSpace: 'pre-wrap',
                      }}
                    >
                      {m.content}

                      {/* Citations & Evidence Lineage */}
                      {!isUser && renderCitations(m.citations)}
                    </div>
                  </FadeIn>
                );
              })
            )}

            {isSending && (
              <FadeIn style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#38BDF8', fontSize: '0.82rem', padding: '6px 0' }}>
                <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
                  <span className="typing-dot" style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#38BDF8', animation: 'typingPulse 1.4s infinite ease-in-out', animationDelay: '0s' }} />
                  <span className="typing-dot" style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#38BDF8', animation: 'typingPulse 1.4s infinite ease-in-out', animationDelay: '0.2s' }} />
                  <span className="typing-dot" style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#38BDF8', animation: 'typingPulse 1.4s infinite ease-in-out', animationDelay: '0.4s' }} />
                </div>
                <span style={{ fontWeight: 600 }}>DEX Analyst is conducting deterministic evaluation...</span>
              </FadeIn>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Box */}
          <div style={{ padding: '16px', borderTop: '1px solid #141A24', backgroundColor: '#07090E' }}>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              style={{ display: 'flex', gap: '10px' }}
            >
              <input
                type="text"
                placeholder="Ask DEX Analyst about health score, risks, root causes, or recommendations..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                disabled={isSending}
                className="input"
                style={{ flex: 1, background: '#0A0E17', border: '1px solid #1A2230', borderRadius: '8px', color: '#FFFFFF', padding: '10px 14px', fontSize: '0.86rem' }}
              />
              <button
                type="submit"
                disabled={isSending || !inputText.trim()}
                className="executive-motion-btn"
                style={{
                  background: '#38BDF8',
                  color: '#080C14',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '0 18px',
                  fontWeight: 700,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <Send size={15} />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};
