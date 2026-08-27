import React, { useEffect, useRef, useState } from 'react';
import {
  ArrowRight,
  Bot,
  MessageSquare,
  Send,
  Sparkles,
  User,
} from 'lucide-react';
import { ChatSummaryPayload } from '../../../types/dashboard';
import { chatAnalystApi } from '../../../api';
import { FadeIn, StaggerContainer, StaggerItem } from '../../../design-system/motion';

interface ChatSectionProps {
  datasetId: string;
  chatSummary: ChatSummaryPayload;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Array<{ title: string; source: string; confidence: number }>;
}

export const ChatSection: React.FC<ChatSectionProps> = ({
  datasetId,
  chatSummary,
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        'Hello. I am DEX Analyst, your DecisionOS autonomous strategic intelligence engine. Ask me anything about your verified business health, critical root causes, scenario simulations, or recommended action plans.',
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, sending]);

  const rawQuestions = chatSummary?.suggested_questions || [];
  const normalizedQuestions = rawQuestions.map((item) => {
    if (typeof item === 'string') {
      return { category: 'GENERAL' as const, question: item };
    }
    return item;
  });

  const suggestedQuestions =
    normalizedQuestions.length > 0
      ? normalizedQuestions
      : [
          { category: 'ROOT_CAUSE' as const, question: 'What are the primary operational bottlenecks identified in this dataset?' },
          { category: 'RECOMMENDATION' as const, question: 'Which strategic recommendation offers the highest ROI with lowest effort?' },
          { category: 'FORECAST' as const, question: 'What is the projected revenue trajectory over the next 90 days?' },
          { category: 'HEALTH_SCORE' as const, question: 'Summarize the boardroom briefing and highlight key decision points.' },
        ];

  const getCategoryColor = (cat: string) => {
    switch (cat) {
      case 'FORECAST':
        return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30';
      case 'ROOT_CAUSE':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'RECOMMENDATION':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'HEALTH_SCORE':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/30';
      default:
        return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  const handleSendMessage = async (textToSend?: string) => {
    const query = (textToSend || inputText).trim();
    if (!query || sending) return;

    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: query,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setSending(true);

    try {
      let currentSession = sessionId;
      if (!currentSession) {
        const sessionRes = await chatAnalystApi.createSession(
          datasetId,
          'Executive Dashboard Session'
        );
        currentSession = sessionRes.session_id || sessionRes.id;
        setSessionId(currentSession);
      }

      const response = await chatAnalystApi.sendMessage(currentSession!, query);

      const assistantMsg: Message = {
        id: response.message_id || `bot-${Date.now()}`,
        role: 'assistant',
        content: response.response_text || response.content || 'Analysis generated.',
        citations: response.citations || [],
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: 'assistant',
          content:
            err.message ||
            'Apologies, I encountered an issue querying the intelligence models. Please try again.',
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <section id="chat" className="scroll-mt-24 space-y-6">
      {/* Section Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-gradient-to-tr from-cyan-600 to-indigo-600 rounded-xl text-white shadow-lg">
            <MessageSquare className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white tracking-tight">
              DEX Analyst
            </h2>
            <p className="text-xs text-slate-400">
              Autonomous strategic Q&amp;A — anchored to verified dataset telemetry, causal graphs, and forecast projections
            </p>
          </div>
        </div>
      </div>

      {/* Main Chat Container */}
      <div className="bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl shadow-xl flex flex-col h-[560px] overflow-hidden">
        {/* Suggested Questions Header */}
        <div className="p-4 bg-slate-950/70 border-b border-slate-800">
          <div className="flex items-center gap-2 text-xs font-semibold text-cyan-400 mb-2">
            <Sparkles className="w-4 h-4" />
            <span>Suggested Executive Inquiries (Auto-Generated):</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((qObj, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(qObj.question)}
                disabled={sending}
                className="px-3 py-1.5 text-xs bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 rounded-xl transition-all text-left flex items-center gap-2 disabled:opacity-50"
              >
                <span className={`px-1.5 py-0.5 text-[9px] font-bold rounded uppercase border ${getCategoryColor(qObj.category)}`}>
                  {qObj.category.replace('_', ' ')}
                </span>
                <span>{qObj.question}</span>
                <ArrowRight className="w-3 h-3 text-cyan-400 shrink-0" />
              </button>
            ))}
          </div>
        </div>

        {/* Message Thread */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((m) => {
            const isUser = m.role === 'user';
            return (
              <FadeIn
                key={m.id}
                style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', flexDirection: isUser ? 'row-reverse' : 'row' }}
              >
                <div
                  className={`p-2 rounded-xl text-white shrink-0 ${
                    isUser
                      ? 'bg-gradient-to-tr from-cyan-600 to-indigo-600 shadow-md'
                      : 'bg-slate-800 text-cyan-400 border border-slate-700'
                  }`}
                >
                  {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>

                <div
                  className={`max-w-2xl rounded-2xl p-4 text-xs leading-relaxed ${
                    isUser
                      ? 'bg-gradient-to-r from-cyan-600 to-indigo-600 text-white shadow-lg'
                      : 'bg-slate-950/80 border border-slate-800 text-slate-200 shadow-md'
                  }`}
                >
                  {/* DEX Analyst label */}
                  {!isUser && (
                    <div style={{ fontSize: '0.68rem', fontWeight: 700, color: '#38BDF8', marginBottom: '4px', letterSpacing: '0.04em' }}>
                      DEX Analyst
                    </div>
                  )}
                  <div className="whitespace-pre-wrap">{m.content}</div>

                  {/* Citations block with 30ms stagger */}
                  {m.citations && m.citations.length > 0 && (
                    <div className="mt-3 pt-2.5 border-t border-slate-800 space-y-1">
                      <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                        Verified Data Sources:
                      </div>
                      <StaggerContainer
                        staggerDelay={0.03}
                        viewportOnce={false}
                        style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}
                      >
                        {m.citations.map((c, i) => (
                          <StaggerItem key={i}>
                            <span className="px-2 py-0.5 text-[10px] bg-slate-900 text-cyan-300 rounded border border-cyan-900/40">
                              {c.title || c.source}
                            </span>
                          </StaggerItem>
                        ))}
                      </StaggerContainer>
                    </div>
                  )}
                </div>
              </FadeIn>
            );
          })}

          {sending && (
            <FadeIn style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
              <div className="p-2 rounded-xl bg-slate-800 text-cyan-400 border border-slate-700">
                <Bot className="w-4 h-4" />
              </div>
              <div className="bg-slate-950/80 border border-slate-800 rounded-2xl p-4 text-xs text-slate-400 flex items-center gap-8px">
                <div style={{ display: 'flex', gap: '4px', alignItems: 'center', marginRight: '8px' }}>
                  <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#38BDF8', display: 'inline-block', animation: 'typingPulse 1.4s infinite ease-in-out', animationDelay: '0s' }} />
                  <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#38BDF8', display: 'inline-block', animation: 'typingPulse 1.4s infinite ease-in-out', animationDelay: '0.2s' }} />
                  <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#38BDF8', display: 'inline-block', animation: 'typingPulse 1.4s infinite ease-in-out', animationDelay: '0.4s' }} />
                </div>
                <span style={{ fontWeight: 600, color: '#38BDF8', fontSize: '0.75rem' }}>DEX Analyst</span>
                <span style={{ marginLeft: '6px' }}>conducting deterministic analysis...</span>
              </div>
            </FadeIn>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="p-4 bg-slate-950/80 border-t border-slate-800 flex items-center gap-3"
        >
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Ask a strategic decision question (e.g., 'What is causing the revenue drop in enterprise accounts?')..."
            className="flex-1 bg-slate-900/90 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white placeholder:text-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
          />
          <button
            type="submit"
            disabled={!inputText.trim() || sending}
            className="px-4 py-2.5 bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 disabled:opacity-50 text-white text-xs font-semibold rounded-xl flex items-center gap-1.5 shadow-lg transition-all"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Send</span>
          </button>
        </form>
      </div>
    </section>
  );
};
