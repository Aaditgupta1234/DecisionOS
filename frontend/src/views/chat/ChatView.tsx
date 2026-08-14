import React, { useEffect, useState, useRef } from 'react';
import { useDataset } from '../../context/DatasetContext';
import { DecisionApi } from '../../api';
import { ChatMessage, ChatSession } from '../../types';
import { LoadingSkeleton } from '../../components/feedback/LoadingSkeleton';
import { ErrorBanner } from '../../components/feedback/ErrorBanner';
import { EmptyState } from '../../components/feedback/EmptyState';
import { MessageSquare, Send, Plus, Sparkles, Bot, User as UserIcon } from 'lucide-react';

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
    'What is the primary risk diagnosed in this dataset?',
    'Explain the top root cause driving performance decline.',
    'What are the highest priority recommendations?',
    'How is the 0-100 business health score calculated?',
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
      const responseMsg = await DecisionApi.sendChatMessage(activeSession.id, text);
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

  return (
    <div className="page-container" style={{ height: 'calc(100vh - var(--header-height))', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <span className="badge badge-ai">Phase 6.1 AI Chat Analyst</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--color-ai-light)' }}>
              Grounded in Deterministic Pipeline Intelligence
            </span>
          </div>
          <h1>AI Analyst Studio</h1>
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
            width: '220px',
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
                <Bot size={36} color="var(--color-ai-light)" style={{ marginBottom: '12px' }} />
                <h3 style={{ fontSize: '1.1rem', marginBottom: '6px' }}>DecisionOS Grounded Chat Analyst</h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', maxWidth: '400px', marginBottom: '20px' }}>
                  Ask questions about diagnosed findings, root causes, KPI trends, and actionable recommendations.
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', width: '100%', maxWidth: '420px' }}>
                  {suggestedPrompts.map((prompt, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSendMessage(prompt)}
                      className="btn btn-secondary btn-sm"
                      style={{ textAlign: 'left', justifyContent: 'flex-start' }}
                    >
                      <Sparkles size={14} color="var(--color-ai-light)" />
                      <span>{prompt}</span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((m) => {
                const isUser = m.role === 'USER';
                return (
                  <div
                    key={m.id}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: isUser ? 'flex-end' : 'flex-start',
                      width: '100%',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                      {isUser ? <UserIcon size={12} /> : <Bot size={12} color="var(--color-ai-light)" />}
                      <span>{isUser ? 'You' : 'AI Analyst'}</span>
                    </div>

                    <div
                      style={{
                        maxWidth: '80%',
                        padding: '12px 16px',
                        borderRadius: 'var(--radius-md)',
                        backgroundColor: isUser ? 'var(--color-primary)' : 'var(--bg-surface-elevated)',
                        border: `1px solid ${isUser ? 'transparent' : 'var(--border-default)'}`,
                        color: '#ffffff',
                        fontSize: '0.9rem',
                        lineHeight: 1.6,
                        whiteSpace: 'pre-wrap',
                      }}
                    >
                      {m.content}

                      {/* Citations */}
                      {m.citations && m.citations.length > 0 && (
                        <div style={{ marginTop: '10px', paddingTop: '8px', borderTop: '1px solid rgba(255, 255, 255, 0.15)', fontSize: '0.75rem' }}>
                          <span style={{ color: 'var(--color-ai-light)', fontWeight: 600 }}>Citations: </span>
                          {m.citations.map((c, i) => (
                            <span key={i} className="badge badge-neutral" style={{ marginRight: '4px', fontSize: '0.65rem' }}>
                              {c.type}: {c.title}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })
            )}

            {isSending && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-ai-light)', fontSize: '0.85rem' }}>
                <Bot size={16} />
                <span>Analyst is evaluating dataset context...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Box */}
          <div style={{ padding: '16px', borderTop: '1px solid var(--border-subtle)', backgroundColor: 'var(--bg-app)' }}>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              style={{ display: 'flex', gap: '10px' }}
            >
              <input
                type="text"
                placeholder="Ask about revenue trends, findings, or recommendations..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                disabled={isSending}
                className="input"
                style={{ flex: 1 }}
              />
              <button type="submit" disabled={isSending || !inputText.trim()} className="btn btn-primary">
                <Send size={16} />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};
