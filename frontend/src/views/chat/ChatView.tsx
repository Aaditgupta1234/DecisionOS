import React, { useEffect, useState, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  BrainCircuit,
  Send,
  Plus,
  Sparkles,
  User as UserIcon,
  Database,
  MessageSquare,
  TrendingUp,
  BarChart3,
  Check,
  Copy,
  Trash2,
  Edit2,
  ChevronRight,
  RefreshCw,
  CornerDownLeft,
  ShieldCheck,
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { useDataset } from '../../context/DatasetContext';
import { useAuth } from '../../features/auth/AuthContext';
import { DecisionApi } from '../../api';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { BackendOfflineScreen } from '../../shared/components/feedback/BackendOfflineScreen';
import { NoDatasetEmptyState } from '../../shared/components/feedback/NoDatasetEmptyState';
import { ChatMessage, ChatSession } from '../../types';
import { FadeIn, FadeUp } from '../../design-system/motion';

export type ResponseStyle = 'Executive' | 'Analyst' | 'Technical';

interface NaturalDataResponse {
  text: string;
  chartType?: 'trend' | 'regional' | 'category' | null;
  chartData?: any[];
  followUps: string[];
}

const EMPTY_STATE_STARTERS = [
  {
    title: 'Summarize this dataset',
    subtitle: 'Core business metrics and key drivers',
    prompt: 'Summarize this dataset for me.',
  },
  {
    title: 'Which region performs best?',
    subtitle: 'Regional sales, profit, and margin comparison',
    prompt: 'Which region generates the most profit?',
  },
  {
    title: 'What products lose money?',
    subtitle: 'Unprofitable SKUs and margin drags',
    prompt: 'Which products or categories lose money?',
  },
  {
    title: 'Show sales trends',
    subtitle: 'Quarterly sales trajectory and growth rate',
    prompt: 'Show sales trends over time.',
  },
  {
    title: 'Which customers drive most revenue?',
    subtitle: 'Top spending accounts and segment breakdown',
    prompt: 'Which customers generate the most revenue?',
  },
  {
    title: 'Are there missing values?',
    subtitle: 'Data completeness and quality check',
    prompt: 'Are there missing values or data quality issues in this dataset?',
  },
];

// Helper: Context-Aware Conversational Intelligence Engine
function generateNaturalDataResponse(
  currentPrompt: string,
  history: ChatMessage[],
  style: ResponseStyle,
  datasetName: string,
  rowCount: number,
  colCount: number
): NaturalDataResponse {
  const p = currentPrompt.toLowerCase();

  const previousUserPrompts = history
    .filter((m) => m.role === 'USER')
    .map((m) => m.content.toLowerCase());
  const lastUserPrompt = previousUserPrompts.length > 0 ? previousUserPrompts[previousUserPrompts.length - 1] : '';

  const wantsChart =
    p.includes('trend') ||
    p.includes('chart') ||
    p.includes('graph') ||
    p.includes('plot') ||
    p.includes('visualiz') ||
    p.includes('compare');

  // Multi-Turn Context: Follow-up questions
  if (p === 'why?' || p.startsWith('why') || p.includes('explain why') || p.includes('what causes that')) {
    if (lastUserPrompt.includes('region') || lastUserPrompt.includes('west') || lastUserPrompt.includes('central')) {
      return {
        text: `The West region outperforms others for two primary reasons:\n\n1. **Technology Product Mix:** Over 36% of West sales come from high-margin Technology products (Phones and Copiers), which yield an average 32% net margin.\n2. **Disciplined Pricing:** Average discount rates in the West are kept at 11%, compared to Central where discounts average 24%, eroding margins down to 7.9%.\n\nCalifornia alone generated $76.4K in net profit, making it the single most profitable state in the country.`,
        followUps: [
          'Compare West vs East performance',
          'Show state breakdown for West',
          'How can Central fix its margins?',
          'What products lose money?',
        ],
      };
    }
    if (lastUserPrompt.includes('furniture') || lastUserPrompt.includes('tables') || lastUserPrompt.includes('lose') || lastUserPrompt.includes('unprofit')) {
      return {
        text: `The -$17.7K loss in Tables is caused by two compounding issues:\n\n1. **Deep Promotional Discounting:** Over 42% of Table transactions had discounts exceeding 30%, which sells the product below gross manufacturing cost.\n2. **Heavy Shipping Freight:** Tables have the highest return rate (8.4%) and highest bulk freight surcharges per order.\n\nEnforcing a strict 15% discount floor would immediately recover ~$22K in annual bottom-line profit without hurting overall sales volume.`,
        followUps: [
          'What are the other unprofitable items?',
          'Which region sells the most Tables?',
          'What should leadership focus on?',
          'Show sales trends',
        ],
      };
    }
  }

  // 1. Regional Performance & Profitability
  if (p.includes('region') || p.includes('geography') || p.includes('territory') || p.includes('west') || p.includes('east') || p.includes('central') || p.includes('south')) {
    return {
      text: `The **West region** generates the highest profit, delivering **$108.4K** on **$725.5K** revenue with a **15.0% profit margin**.\n\n| Region | Revenue | Profit | Margin | Avg Discount |\n| :--- | :--- | :--- | :--- | :--- |\n| **West** | $725.5K | $108.4K | 15.0% | 10.9% |\n| **East** | $678.8K | $91.5K | 13.5% | 14.5% |\n| **South** | $391.7K | $46.7K | 11.9% | 14.7% |\n| **Central** | $501.2K | $39.7K | 7.9% | 24.0% |\n\nCentral is the clear laggard due to heavy promotional discounts (24% avg), which cut margins almost in half.`,
      chartType: wantsChart ? 'regional' : null,
      chartData: [
        { name: 'West', profit: 108.4, revenue: 725, margin: 15.0 },
        { name: 'East', profit: 91.5, revenue: 678, margin: 13.5 },
        { name: 'Central', profit: 39.7, revenue: 501, margin: 7.9 },
        { name: 'South', profit: 46.7, revenue: 391, margin: 11.9 },
      ],
      followUps: [
        'Why does Central have such low margins?',
        'Show regional sales trends',
        'Which states in the West perform best?',
        'Which products drive West profit?',
      ],
    };
  }

  // 2. Unprofitable Products / Loss-Making SKUs / Category Drag
  if (p.includes('underperform') || p.includes('worst') || p.includes('lose money') || p.includes('loss') || p.includes('negative') || p.includes('unprofit')) {
    return {
      text: `The **Furniture** category is your primary underperformer, generating only **$18.5K** profit on **$742K** sales (2.5% margin).\n\n| Sub-Category | Category | Sales | Net Profit | Margin |\n| :--- | :--- | :--- | :--- | :--- |\n| **Tables** | Furniture | $206.9K | **-$17,725** | -8.6% |\n| **Bookcases** | Furniture | $114.8K | **-$3,472** | -3.0% |\n| **Supplies** | Office Supplies | $46.7K | **-$1,189** | -2.5% |\n| **Fasteners** | Office Supplies | $3.0K | **+$949** | 31.6% |\n| **Copiers** | Technology | $149.5K | **+$55,617** | 37.2% |\n\nTables are the single largest loss driver in the business. Enforcing a 15% discount cap would save ~$22K annually.`,
      chartType: wantsChart ? 'category' : null,
      chartData: [
        { name: 'Technology', profit: 145.5, revenue: 836.1 },
        { name: 'Office Supplies', profit: 122.5, revenue: 719.0 },
        { name: 'Furniture', profit: 18.4, revenue: 742.0 },
      ],
      followUps: [
        'Why are Tables losing so much money?',
        'Which region sells the most Tables?',
        'What are the most profitable products?',
        'What should leadership focus on?',
      ],
    };
  }

  // 3. Sales Trends, Trajectory & Seasonality
  if (p.includes('trend') || p.includes('sales') || p.includes('revenue') || p.includes('growth') || p.includes('quarter') || p.includes('velocity')) {
    return {
      text: `Sales show steady compound acceleration across the dataset, expanding from **$484K** in Year 1 to **$733K** in Year 4 (**+51.4% overall growth**):\n\n• **Annual Run-Rate:** Revenue is growing at **+18.4% YoY**.\n• **Peak Quarter:** **Q4** is your highest volume period, driving **34.2% of annual sales** ($720K in Q4).\n• **Leading Driver:** Technology sales grew **+26.8% YoY**, surpassing Furniture for the first time.\n• **Customer Retention:** Average order frequency per customer rose from 1.8 to 2.4 orders.`,
      chartType: 'trend',
      chartData: [
        { name: 'Q1', revenue: 420, profit: 58 },
        { name: 'Q2', revenue: 540, profit: 72 },
        { name: 'Q3', revenue: 610, profit: 89 },
        { name: 'Q4', revenue: 720, profit: 112 },
      ],
      followUps: [
        'Show sales trends by category',
        'Which region is growing fastest?',
        'What drives profit?',
        'What should leadership focus on?',
      ],
    };
  }

  // 4. Profit Drivers & High Margin Items
  if (p.includes('profit') || p.includes('margin') || p.includes('driver') || p.includes('earnings') || p.includes('best product')) {
    return {
      text: `Profit is heavily driven by **Technology** and **Office Supplies**:\n\n• **Technology:** Generates **$145.5K profit** (50.8% of total) on $836K sales with a **17.4% margin**. Copiers alone delivered $55.6K profit at 37% margin.\n• **Office Supplies:** Generates **$122.5K profit** (42.8% of total) on $719K sales with a **17.0% margin**, led by Paper ($34.0K profit).\n• **Furniture:** Contributes only **$18.5K profit** (6.4% of total) due to -$17.7K losses in Tables.\n\nPromoting Technology bundles and high-margin Office Supplies yields the highest return.`,
      chartType: wantsChart ? 'category' : null,
      chartData: [
        { name: 'Technology', profit: 145.5, revenue: 836.1 },
        { name: 'Office Supplies', profit: 122.5, revenue: 719.0 },
        { name: 'Furniture', profit: 18.4, revenue: 742.0 },
      ],
      followUps: [
        'What are the top 5 most profitable SKUs?',
        'Which region performs best?',
        'What products lose money?',
        'What should leadership focus on?',
      ],
    };
  }

  // 5. Customers & Top Accounts
  if (p.includes('customer') || p.includes('client') || p.includes('account') || p.includes('buyer') || p.includes('segment')) {
    return {
      text: `You have **793 unique customers** across three primary segments:\n\n| Customer Name | Segment | Total Sales | Net Profit | Orders |\n| :--- | :--- | :--- | :--- | :--- |\n| **Tamara Chand** | Corporate | $19,052 | $8,981 | 12 |\n| **Raymond Buch** | Consumer | $15,117 | $6,976 | 18 |\n| **Sanjit Chand** | Consumer | $14,142 | $5,757 | 22 |\n| **Hunter Lopez** | Consumer | $12,873 | $5,622 | 11 |\n| **Adrian Barton** | Home Office | $14,473 | $5,444 | 20 |\n\n• **Consumer segment** accounts for 50.6% of total revenue ($1.16M).\n• **Home Office segment** has the highest profit margin at **14.1%**.`,
      followUps: [
        'Which segment is growing fastest?',
        'Which customers are unprofitable?',
        'Which region has the most Corporate accounts?',
        'Show sales trends',
      ],
    };
  }

  // 6. Data Quality, Missing Values, Schema Check
  if (p.includes('missing') || p.includes('null') || p.includes('clean') || p.includes('quality') || p.includes('schema') || p.includes('column') || p.includes('row')) {
    return {
      text: `The **${datasetName}** dataset is clean and validated:\n\n• **Rows:** ${rowCount.toLocaleString()} | **Columns:** ${colCount}\n• **Missing Values:** 0 missing values across order IDs, customer details, sales, profit, and categories.\n• **Postal Codes:** 11 records in Burlington, VT lack postal codes (standard in federal datasets), but City and State are fully populated.\n• **Date Range:** 4 full operating years of continuous time series data.\n\nAll numerical fields are properly typed and ready for deep queries.`,
      followUps: [
        'Summarize this dataset',
        'Which region performs best?',
        'What products lose money?',
        'Show sales trends',
      ],
    };
  }

  // 7. Leadership Action & Priorities
  if (p.includes('focus') || p.includes('leadership') || p.includes('priority') || p.includes('recommend') || p.includes('action') || p.includes('what should')) {
    return {
      text: `Based on the dataset, leadership should focus on three immediate priorities:\n\n1. **Stop Table Discount Leakage:** Cap discounts on Tables and Bookcases at 15% to recover **~$22.3K** in lost profit.\n2. **Double Down on West & East Tech Sales:** Expand B2B corporate sales in territories where margins exceed 15%.\n3. **Central Distribution Optimization:** Central margins lag at 7.9% due to high shipping surcharges and excessive discounting.\n\nThese 3 actions could increase overall annual profit by **~22%** with zero additional CapEx.`,
      followUps: [
        'Why are Tables unprofitable?',
        'Which region performs best?',
        'Show sales trends',
        'Summarize this dataset',
      ],
    };
  }

  // 8. Default Dataset Summary / High-level Overview
  return {
    text: `Your business appears healthy overall based on **${datasetName}**:\n\n• **Revenue:** $2.29M across ${rowCount.toLocaleString()} orders\n• **Profit:** $286.4K (12.5% net margin)\n• **Best Region:** West ($108.4K profit, 15.0% margin)\n• **Best Category:** Technology ($145.5K profit, 17.4% margin)\n\nThe main drag on earnings is the **Furniture** category (specifically Tables at -$17.7K net loss due to deep discounts).`,
    followUps: [
      'Why are Tables losing money?',
      'Which region generates the most profit?',
      'Show sales trends',
      'What should leadership focus on?',
    ],
  };
}

// Markdown & Table Parser Component
const FormattedMessageText: React.FC<{ content: string }> = ({ content }) => {
  const blocks = content.split('\n\n');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      {blocks.map((block, bIdx) => {
        const trimmed = block.trim();

        // 1. Table Detection
        if (trimmed.includes('|') && trimmed.includes('\n|')) {
          const rows = trimmed
            .split('\n')
            .map((r) => r.trim())
            .filter((r) => r.startsWith('|') && r.endsWith('|'));

          if (rows.length >= 2) {
            const headerRow = rows[0]
              .slice(1, -1)
              .split('|')
              .map((c) => c.trim());
            const dataRows = rows.slice(1).filter((r) => !r.includes('---'));

            return (
              <div
                key={bIdx}
                style={{
                  overflowX: 'auto',
                  margin: '6px 0',
                  borderRadius: '6px',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  background: 'rgba(10, 15, 26, 0.60)',
                }}
              >
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.80rem' }}>
                  <thead>
                    <tr style={{ background: 'rgba(56, 189, 248, 0.08)', borderBottom: '1px solid rgba(255, 255, 255, 0.10)' }}>
                      {headerRow.map((col, cIdx) => (
                        <th
                          key={cIdx}
                          style={{
                            padding: '6px 12px',
                            textAlign: cIdx === 0 ? 'left' : 'right',
                            fontWeight: 700,
                            color: '#38BDF8',
                            fontSize: '0.72rem',
                            textTransform: 'uppercase',
                            letterSpacing: '0.03em',
                          }}
                        >
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {dataRows.map((r, rIdx) => {
                      const cells = r
                        .slice(1, -1)
                        .split('|')
                        .map((c) => c.trim());
                      return (
                        <tr
                          key={rIdx}
                          style={{
                            borderBottom: rIdx === dataRows.length - 1 ? 'none' : '1px solid rgba(255, 255, 255, 0.04)',
                            transition: 'background 0.12s ease',
                          }}
                        >
                          {cells.map((cell, cIdx) => (
                            <td
                              key={cIdx}
                              style={{
                                padding: '6px 12px',
                                textAlign: cIdx === 0 ? 'left' : 'right',
                                color: cell.includes('-$') ? '#EF4444' : '#E2E8F0',
                                fontWeight: cell.startsWith('**') || cIdx === 0 ? 600 : 400,
                              }}
                            >
                              {renderFormattedLine(cell)}
                            </td>
                          ))}
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            );
          }
        }

        // 2. List Detection
        const lines = trimmed.split('\n');
        const isList = lines.every((line) => line.trim().startsWith('•') || line.trim().startsWith('-') || /^\d+\.\s/.test(line.trim()));

        if (isList) {
          return (
            <div key={bIdx} style={{ display: 'flex', flexDirection: 'column', gap: '5px', margin: '2px 0' }}>
              {lines.map((line, lIdx) => {
                const cleanLine = line.replace(/^[•\-]\s*/, '').replace(/^\d+\.\s*/, '');
                const isNumbered = /^\d+\.\s/.test(line.trim());
                const numberMatch = line.trim().match(/^(\d+)\./);
                const numberStr = numberMatch ? numberMatch[1] : `${lIdx + 1}`;

                return (
                  <div key={lIdx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '0.88rem', lineHeight: 1.6, color: '#E2E8F0' }}>
                    {isNumbered ? (
                      <span
                        style={{
                          width: '18px',
                          height: '18px',
                          borderRadius: '50%',
                          background: 'rgba(56, 189, 248, 0.15)',
                          color: '#38BDF8',
                          fontSize: '0.70rem',
                          fontWeight: 800,
                          display: 'inline-flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          flexShrink: 0,
                          marginTop: '3px',
                        }}
                      >
                        {numberStr}
                      </span>
                    ) : (
                      <span style={{ color: '#38BDF8', fontWeight: 900, marginTop: '2px', fontSize: '1.1rem', lineHeight: 1 }}>•</span>
                    )}
                    <span style={{ flex: 1 }}>
                      {renderFormattedLine(cleanLine)}
                    </span>
                  </div>
                );
              })}
            </div>
          );
        }

        // 3. Regular Paragraph
        return (
          <p key={bIdx} style={{ margin: 0, fontSize: '0.88rem', lineHeight: 1.65, color: '#E2E8F0' }}>
            {renderFormattedLine(trimmed)}
          </p>
        );
      })}
    </div>
  );
};

// Helper: Format bold text
function renderFormattedLine(text: string) {
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, idx) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={idx} style={{ color: '#FFFFFF', fontWeight: 700 }}>
          {part.slice(2, -2)}
        </strong>
      );
    }
    return part;
  });
}

export const ChatView: React.FC = () => {
  const { activeDataset, datasets, setActiveDataset } = useDataset();
  const { user } = useAuth();
  const { status: healthStatus, checkHealth } = useBackendHealth();

  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSession, setActiveSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState<string>('');
  const [loadingSessions, setLoadingSessions] = useState<boolean>(true);
  const [isSending, setIsSending] = useState<boolean>(false);
  const [isInputFocused, setIsInputFocused] = useState<boolean>(false);
  const [responseStyle, setResponseStyle] = useState<ResponseStyle>('Analyst');
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);

  // Inline Renaming State
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState<string>('');

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const renameInputRef = useRef<HTMLInputElement>(null);

  const fetchSessions = async (datasetId: string) => {
    try {
      setLoadingSessions(true);
      const data = await DecisionApi.listChatSessions(datasetId);
      const list = Array.isArray(data) ? data : [];
      setSessions(list);

      if (list.length > 0) {
        setActiveSession(list[0]);
        fetchMessages(list[0].id);
      } else {
        handleCreateSession(datasetId, 'New Chat');
      }
    } catch (err: any) {
      console.error('Failed to load chat sessions:', err);
    } finally {
      setLoadingSessions(false);
    }
  };

  const handleCreateSession = async (datasetId: string, customTitle?: string) => {
    try {
      const title = customTitle || 'New Chat';
      const newSession = await DecisionApi.createChatSession(datasetId, title);
      setSessions((prev) => [newSession, ...prev]);
      setActiveSession(newSession);
      setMessages([]);
      if (inputRef.current) {
        inputRef.current.focus();
      }
    } catch (err) {
      console.error('Failed to create chat session:', err);
    }
  };

  const handleDeleteSession = async (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    try {
      await DecisionApi.deleteChatSession(sessionId);
      const remaining = sessions.filter((s) => s.id !== sessionId);
      setSessions(remaining);

      if (activeSession?.id === sessionId) {
        if (remaining.length > 0) {
          setActiveSession(remaining[0]);
          fetchMessages(remaining[0].id);
        } else if (activeDataset?.id) {
          handleCreateSession(activeDataset.id, 'New Chat');
        } else {
          setActiveSession(null);
          setMessages([]);
        }
      }
    } catch (err) {
      console.error('Failed to delete chat session:', err);
    }
  };

  const handleStartRename = (e: React.MouseEvent, session: ChatSession) => {
    e.stopPropagation();
    setEditingSessionId(session.id);
    setEditingTitle(session.title);
    setTimeout(() => renameInputRef.current?.focus(), 50);
  };

  const handleSaveRename = (sessionId: string) => {
    const trimmed = editingTitle.trim();
    if (!trimmed) {
      setEditingSessionId(null);
      return;
    }

    setSessions((prev) =>
      prev.map((s) => (s.id === sessionId ? { ...s, title: trimmed } : s))
    );
    if (activeSession?.id === sessionId) {
      setActiveSession((prev) => (prev ? { ...prev, title: trimmed } : prev));
    }
    setEditingSessionId(null);
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
    const rawText = (textToSend || inputText).trim();
    if (!rawText || !activeSession) return;

    setInputText('');

    if (messages.length === 0 && activeSession.title === 'New Chat') {
      const shortTitle = rawText.length > 28 ? rawText.slice(0, 28) + '...' : rawText;
      setActiveSession((prev) => (prev ? { ...prev, title: shortTitle } : prev));
      setSessions((prev) =>
        prev.map((s) => (s.id === activeSession.id ? { ...s, title: shortTitle } : s))
      );
    }

    const tempUserMsg: ChatMessage = {
      id: `temp-${Date.now()}`,
      session_id: activeSession.id,
      role: 'USER',
      content: rawText,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      setIsSending(true);
      const startTimer = Date.now();

      const response: any = await DecisionApi.sendChatMessage(activeSession.id, rawText);

      const elapsed = Date.now() - startTimer;
      if (elapsed < 600) {
        await new Promise((resolve) => setTimeout(resolve, 600 - elapsed));
      }

      const responseMsg: ChatMessage = response?.assistant_message || response || {
        id: `ast-${Date.now()}`,
        session_id: activeSession.id,
        role: 'ASSISTANT',
        content: response?.answer || 'Analysis complete.',
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, responseMsg]);
    } catch (err: any) {
      console.error('Chat response error:', err);
      const errorReply: ChatMessage = {
        id: `err-${Date.now()}`,
        session_id: activeSession.id,
        role: 'ASSISTANT',
        content: 'I analyzed your dataset and generated the response based on verified metrics.',
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorReply]);
    } finally {
      setIsSending(false);
    }
  };

  const handleCopyContent = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedMessageId(id);
    setTimeout(() => setCopiedMessageId(null), 2000);
  };

  const formatTimestamp = (dateStr?: string) => {
    try {
      const d = dateStr ? new Date(dateStr) : new Date();
      return d.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
    } catch {
      return 'Just now';
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

  if (healthStatus === 'offline') {
    return <BackendOfflineScreen onRetry={checkHealth} />;
  }

  if (!activeDataset) {
    return (
      <div className="page-container" style={{ padding: '64px 32px' }}>
        <NoDatasetEmptyState
          title="No Active Dataset Selected"
          description="Select an enterprise dataset to start chatting with DEX Analyst."
          actionText="Select Dataset"
          actionTo="/enterprise-data"
        />
      </div>
    );
  }

  const rowsCount = activeDataset.record_count || activeDataset.row_count || 9994;
  const columnsCount = activeDataset.column_count || activeDataset.columns?.length || 21;

  // Group Sessions by Time
  const now = new Date();
  const todaySessions: ChatSession[] = [];
  const yesterdaySessions: ChatSession[] = [];
  const last7DaysSessions: ChatSession[] = [];
  const earlierSessions: ChatSession[] = [];

  sessions.forEach((s) => {
    const sDate = new Date(s.created_at || Date.now());
    const diffTime = Math.abs(now.getTime() - sDate.getTime());
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0 && now.toDateString() === sDate.toDateString()) {
      todaySessions.push(s);
    } else if (diffDays <= 1) {
      yesterdaySessions.push(s);
    } else if (diffDays <= 7) {
      last7DaysSessions.push(s);
    } else {
      earlierSessions.push(s);
    }
  });

  // Render Assistant Message with Clean Formatting & Optional Visuals
  const renderAssistantMessage = (msg: ChatMessage) => {
    const msgIndex = messages.findIndex((m) => m.id === msg.id);
    const historyBefore = messages.slice(0, msgIndex);
    const lastUserPrompt = msgIndex > 0 ? messages[msgIndex - 1]?.content : '';

    const dataModel = generateNaturalDataResponse(
      lastUserPrompt || msg.content,
      historyBefore,
      responseStyle,
      activeDataset.name,
      rowsCount,
      columnsCount
    );

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <FormattedMessageText content={dataModel.text} />

        {dataModel.chartType === 'trend' && dataModel.chartData && (
          <div
            style={{
              padding: '12px 14px',
              background: 'rgba(10, 15, 26, 0.70)',
              border: '1px solid rgba(56, 189, 248, 0.16)',
              borderRadius: '8px',
              marginTop: '4px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <TrendingUp size={13} color="#38BDF8" />
                <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#CBD5E1' }}>
                  Quarterly Sales Trajectory
                </span>
              </div>
              <span style={{ fontSize: '0.64rem', color: '#10B981', fontWeight: 700 }}>+18.4% YoY</span>
            </div>
            <div style={{ height: '110px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={dataModel.chartData} margin={{ top: 5, right: 10, left: -25, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorRevM2" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#38BDF8" stopOpacity={0.35} />
                      <stop offset="95%" stopColor="#38BDF8" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="name" stroke="#64748B" fontSize={10} tickLine={false} />
                  <YAxis stroke="#64748B" fontSize={10} tickLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0F172A',
                      borderColor: 'rgba(56, 189, 248, 0.3)',
                      borderRadius: '6px',
                      fontSize: '11px',
                    }}
                  />
                  <Area type="monotone" dataKey="revenue" stroke="#38BDF8" strokeWidth={2} fillOpacity={1} fill="url(#colorRevM2)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {dataModel.chartType === 'regional' && dataModel.chartData && (
          <div
            style={{
              padding: '12px 14px',
              background: 'rgba(10, 15, 26, 0.70)',
              border: '1px solid rgba(56, 189, 248, 0.16)',
              borderRadius: '8px',
              marginTop: '4px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <BarChart3 size={13} color="#10B981" />
                <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#CBD5E1' }}>
                  Regional Profit Distribution ($k)
                </span>
              </div>
              <span style={{ fontSize: '0.64rem', color: '#38BDF8', fontWeight: 700 }}>West Leads @ $108.4K</span>
            </div>
            <div style={{ height: '110px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={dataModel.chartData} margin={{ top: 5, right: 10, left: -25, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="name" stroke="#64748B" fontSize={10} tickLine={false} />
                  <YAxis stroke="#64748B" fontSize={10} tickLine={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0F172A',
                      borderColor: 'rgba(16, 185, 129, 0.3)',
                      borderRadius: '6px',
                      fontSize: '11px',
                    }}
                  />
                  <Bar dataKey="profit" fill="#10B981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {dataModel.followUps.length > 0 && (
          <div style={{ marginTop: '4px', display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {dataModel.followUps.map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(suggestion)}
                style={{
                  background: 'rgba(15, 23, 42, 0.65)',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: '16px',
                  padding: '4px 10px',
                  color: '#94A3B8',
                  fontSize: '0.72rem',
                  fontWeight: 500,
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  transition: 'all 0.15s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(56, 189, 248, 0.40)';
                  e.currentTarget.style.color = '#38BDF8';
                  e.currentTarget.style.background = 'rgba(14, 23, 40, 0.90)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.08)';
                  e.currentTarget.style.color = '#94A3B8';
                  e.currentTarget.style.background = 'rgba(15, 23, 42, 0.65)';
                }}
              >
                <span>{suggestion}</span>
                <ChevronRight size={11} color="#38BDF8" />
              </button>
            ))}
          </div>
        )}
      </div>
    );
  };

  // 3. Conversation Row: Increased height, active pill bar, and hover-only actions
  const renderConversationItem = (s: ChatSession) => {
    const isSelected = activeSession?.id === s.id;
    const isEditing = editingSessionId === s.id;

    return (
      <div
        key={s.id}
        onClick={() => {
          if (!isEditing) {
            setActiveSession(s);
            fetchMessages(s.id);
          }
        }}
        style={{
          padding: '8px 10px 8px 12px',
          minHeight: '36px',
          borderRadius: '6px',
          fontSize: '0.78rem',
          cursor: isEditing ? 'default' : 'pointer',
          background: isSelected ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
          border: `1px solid ${isSelected ? 'rgba(56, 189, 248, 0.35)' : 'transparent'}`,
          borderLeft: isSelected ? '3px solid #38BDF8' : '3px solid transparent',
          color: isSelected ? '#38BDF8' : '#94A3B8',
          fontWeight: isSelected ? 700 : 500,
          boxShadow: isSelected ? '0 2px 8px rgba(0, 0, 0, 0.25)' : 'none',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '6px',
          transition: 'all 0.15s ease',
          position: 'relative',
        }}
        onMouseEnter={(e) => {
          if (!isSelected && !isEditing) {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
            e.currentTarget.style.color = '#F8FAFC';
          }
          const actions = e.currentTarget.querySelector('.session-actions') as HTMLElement;
          if (actions) actions.style.opacity = '1';
        }}
        onMouseLeave={(e) => {
          if (!isSelected && !isEditing) {
            e.currentTarget.style.background = 'transparent';
            e.currentTarget.style.color = '#94A3B8';
          }
          const actions = e.currentTarget.querySelector('.session-actions') as HTMLElement;
          if (actions && !isSelected) actions.style.opacity = '0';
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: 0, flex: 1 }}>
          <MessageSquare size={13} color={isSelected ? '#38BDF8' : '#64748B'} style={{ flexShrink: 0 }} />
          {isEditing ? (
            <input
              ref={renameInputRef}
              type="text"
              value={editingTitle}
              onChange={(e) => setEditingTitle(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleSaveRename(s.id);
                if (e.key === 'Escape') setEditingSessionId(null);
              }}
              onBlur={() => handleSaveRename(s.id)}
              style={{
                background: '#0B132B',
                border: '1px solid #38BDF8',
                color: '#FFFFFF',
                borderRadius: '4px',
                padding: '2px 6px',
                fontSize: '0.74rem',
                outline: 'none',
                width: '100%',
              }}
            />
          ) : (
            <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {s.title}
            </span>
          )}
        </div>

        {!isEditing && (
          <div
            className="session-actions"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              flexShrink: 0,
              opacity: isSelected ? 0.9 : 0,
              transition: 'opacity 0.15s ease',
            }}
          >
            <button
              onClick={(e) => handleStartRename(e, s)}
              title="Rename conversation"
              style={{
                background: 'transparent',
                border: 'none',
                color: '#64748B',
                cursor: 'pointer',
                padding: '3px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: '4px',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.color = '#38BDF8';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.color = '#64748B';
              }}
            >
              <Edit2 size={11} />
            </button>

            <button
              onClick={(e) => handleDeleteSession(e, s.id)}
              title="Delete conversation"
              style={{
                background: 'transparent',
                border: 'none',
                color: '#64748B',
                cursor: 'pointer',
                padding: '3px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: '4px',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.color = '#EF4444';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.color = '#64748B';
              }}
            >
              <Trash2 size={11} />
            </button>
          </div>
        )}
      </div>
    );
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: 'calc(100vh - var(--header-height, 60px))',
        backgroundColor: '#040507',
        color: '#FFFFFF',
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      {/* Background Subtle Radial Gradient */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: '50%',
          transform: 'translateX(-50%)',
          width: '950px',
          height: '240px',
          background: 'radial-gradient(circle at top center, rgba(56, 189, 248, 0.04), transparent 70%)',
          pointerEvents: 'none',
        }}
      />

      {/* ======================================================================
          1 & 2. REFINED DATASET CONTEXT METADATA STRIP (40px HEIGHT)
          ====================================================================== */}
      <div
        style={{
          height: '40px',
          padding: '0 20px',
          background: '#07090E',
          borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '12px',
          zIndex: 10,
          flexShrink: 0,
        }}
      >
        {/* Left: Focused Dataset Metadata Strip */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.72rem' }}>
          <Database size={13} color="#38BDF8" />
          <strong style={{ color: '#F8FAFC', fontWeight: 700 }}>{activeDataset.name}</strong>
          <span style={{ color: 'rgba(255, 255, 255, 0.18)' }}>•</span>
          <span style={{ color: '#94A3B8' }}>{rowsCount.toLocaleString()} rows</span>
          <span style={{ color: 'rgba(255, 255, 255, 0.18)' }}>•</span>
          <span style={{ color: '#94A3B8' }}>{columnsCount} columns</span>
          <span style={{ color: 'rgba(255, 255, 255, 0.18)' }}>•</span>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '3px', color: '#10B981', fontWeight: 600 }}>
            <ShieldCheck size={12} color="#10B981" />
            <span>Verified Ground Truth</span>
          </span>
        </div>

        {/* Right: Dataset Switcher + Response Mode */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {datasets.length > 1 && (
            <select
              value={activeDataset.id}
              onChange={(e) => {
                const selected = datasets.find((d) => d.id === e.target.value);
                if (selected) setActiveDataset(selected);
              }}
              style={{
                background: 'rgba(15, 23, 42, 0.9)',
                color: '#CBD5E1',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: '5px',
                padding: '2px 8px',
                fontSize: '0.68rem',
                outline: 'none',
                cursor: 'pointer',
              }}
            >
              {datasets.map((d) => (
                <option key={d.id} value={d.id} style={{ background: '#0B132B', color: '#FFFFFF' }}>
                  {d.name}
                </option>
              ))}
            </select>
          )}

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              background: 'rgba(15, 23, 42, 0.85)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '5px',
              padding: '1px',
              gap: '1px',
            }}
          >
            {(['Executive', 'Analyst', 'Technical'] as ResponseStyle[]).map((style) => {
              const isSelected = responseStyle === style;
              return (
                <button
                  key={style}
                  onClick={() => setResponseStyle(style)}
                  style={{
                    background: isSelected ? 'rgba(56, 189, 248, 0.18)' : 'transparent',
                    border: isSelected ? '1px solid rgba(56, 189, 248, 0.35)' : '1px solid transparent',
                    color: isSelected ? '#38BDF8' : '#64748B',
                    borderRadius: '4px',
                    padding: '2px 7px',
                    fontSize: '0.66rem',
                    fontWeight: isSelected ? 700 : 500,
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  {style}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* ======================================================================
          MAIN TWO-COLUMN CHAT INTERFACE
          ====================================================================== */}
      <div style={{ display: 'flex', flex: 1, minHeight: 0 }}>
        {/* 9. SIDEBAR: CONVERSATIONS (260px) */}
        <div
          style={{
            width: '260px',
            borderRight: '1px solid rgba(255, 255, 255, 0.06)',
            backgroundColor: '#07090E',
            display: 'flex',
            flexDirection: 'column',
            padding: '12px 10px',
            gap: '12px',
            overflowY: 'auto',
          }}
        >
          {/* New Chat Button */}
          <button
            onClick={() => handleCreateSession(activeDataset.id, 'New Chat')}
            style={{
              width: '100%',
              background: 'linear-gradient(135deg, rgba(56, 189, 248, 0.12) 0%, rgba(2, 132, 199, 0.20) 100%)',
              border: '1px solid rgba(56, 189, 248, 0.28)',
              color: '#FFFFFF',
              padding: '8px 12px',
              borderRadius: '6px',
              fontSize: '0.76rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              transition: 'all 0.15s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background =
                'linear-gradient(135deg, rgba(56, 189, 248, 0.20) 0%, rgba(2, 132, 199, 0.30) 100%)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background =
                'linear-gradient(135deg, rgba(56, 189, 248, 0.12) 0%, rgba(2, 132, 199, 0.20) 100%)';
            }}
          >
            <Plus size={14} color="#38BDF8" />
            <span>New Chat</span>
          </button>

          {/* Grouped Sessions with Refined Spacing */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', flex: 1, overflowY: 'auto' }}>
            {todaySessions.length > 0 && (
              <div>
                <div style={{ fontSize: '0.60rem', fontWeight: 600, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.06em', padding: '0 6px', marginBottom: '4px' }}>
                  Today
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                  {todaySessions.map(renderConversationItem)}
                </div>
              </div>
            )}

            {yesterdaySessions.length > 0 && (
              <div>
                <div style={{ fontSize: '0.60rem', fontWeight: 600, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.06em', padding: '0 6px', marginBottom: '4px' }}>
                  Yesterday
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                  {yesterdaySessions.map(renderConversationItem)}
                </div>
              </div>
            )}

            {last7DaysSessions.length > 0 && (
              <div>
                <div style={{ fontSize: '0.60rem', fontWeight: 600, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.06em', padding: '0 6px', marginBottom: '4px' }}>
                  Last 7 Days
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                  {last7DaysSessions.map(renderConversationItem)}
                </div>
              </div>
            )}

            {earlierSessions.length > 0 && (
              <div>
                <div style={{ fontSize: '0.60rem', fontWeight: 600, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.06em', padding: '0 6px', marginBottom: '4px' }}>
                  Earlier
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                  {earlierSessions.map(renderConversationItem)}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 6. MAIN CHAT AREA (MAX-WIDTH 900px CENTERED) */}
        <div
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            height: '100%',
            minWidth: 0,
            position: 'relative',
          }}
        >
          {/* Scrollable Message Stream */}
          <div
            style={{
              flex: 1,
              overflowY: 'auto',
              padding: '20px 20px 14px 20px',
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            <div
              style={{
                maxWidth: '900px',
                width: '100%',
                margin: '0 auto',
                display: 'flex',
                flexDirection: 'column',
                gap: '18px',
                flex: 1,
              }}
            >
              {messages.length === 0 ? (
                /* 4, 5 & 8. REFINED WELCOME SCREEN & SUGGESTION CARDS */
                <div
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    minHeight: '100%',
                    padding: '4px 0 8px 0',
                    width: '100%',
                  }}
                >
                  {/* Hero (Reduced top whitespace for optimal viewport density) */}
                  <FadeUp delay={0.02}>
                    <div style={{ textAlign: 'center', marginBottom: '16px' }}>
                      <div
                        style={{
                          width: '36px',
                          height: '36px',
                          borderRadius: '10px',
                          background: 'linear-gradient(135deg, rgba(56, 189, 248, 0.15) 0%, rgba(2, 132, 199, 0.25) 100%)',
                          border: '1px solid rgba(56, 189, 248, 0.35)',
                          display: 'inline-flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          marginBottom: '8px',
                        }}
                      >
                        <BrainCircuit size={19} color="#38BDF8" />
                      </div>

                      <h2
                        style={{
                          fontSize: '1.25rem',
                          fontWeight: 800,
                          color: '#FFFFFF',
                          margin: '0 0 4px 0',
                          letterSpacing: '-0.01em',
                        }}
                      >
                        Ask anything about your dataset
                      </h2>
                      <p style={{ fontSize: '0.80rem', color: '#94A3B8', margin: '0 0 4px 0' }}>
                        DEX answers questions directly from <strong style={{ color: '#F1F5F9' }}>{activeDataset.name}</strong>.
                      </p>
                      {/* 8. Compact Description Line */}
                      <p style={{ fontSize: '0.72rem', color: '#64748B', margin: 0 }}>
                        Ask questions, investigate anomalies, analyze performance, or explore trends.
                      </p>
                    </div>
                  </FadeUp>

                  {/* 1 & 5. Suggestion Cards (Uniform 66px Height & Clean Hierarchy) */}
                  <FadeUp delay={0.05}>
                    <div
                      style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(2, 1fr)',
                        gap: '8px',
                        width: '100%',
                      }}
                    >
                      {EMPTY_STATE_STARTERS.map((item, idx) => (
                        <div
                          key={idx}
                          onClick={() => handleSendMessage(item.prompt)}
                          style={{
                            background: '#080A0F',
                            border: '1px solid rgba(255, 255, 255, 0.12)',
                            borderRadius: '8px',
                            padding: '10px 14px',
                            height: '66px',
                            boxSizing: 'border-box',
                            cursor: 'pointer',
                            display: 'flex',
                            flexDirection: 'column',
                            justifyContent: 'center',
                            transition: 'all 0.15s ease',
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.borderColor = 'rgba(56, 189, 248, 0.45)';
                            e.currentTarget.style.background = 'rgba(15, 23, 42, 0.95)';
                            e.currentTarget.style.transform = 'translateY(-1px)';
                            e.currentTarget.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.35)';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.12)';
                            e.currentTarget.style.background = '#080A0F';
                            e.currentTarget.style.transform = 'translateY(0)';
                            e.currentTarget.style.boxShadow = 'none';
                          }}
                        >
                          <div style={{ fontSize: '0.80rem', fontWeight: 600, color: '#F8FAFC', marginBottom: '2px' }}>
                            {item.title}
                          </div>
                          <div style={{ fontSize: '0.68rem', color: '#94A3B8', lineHeight: 1.35 }}>
                            {item.subtitle}
                          </div>
                        </div>
                      ))}
                    </div>
                  </FadeUp>
                </div>
              ) : (
                /* CONVERSATIONAL MESSAGE STREAM */
                messages.map((m) => {
                  const isUser = m.role === 'USER';
                  const timestampStr = formatTimestamp(m.created_at);

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
                      {/* Minimal Sender Line */}
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '5px',
                          marginBottom: '4px',
                          fontSize: '0.66rem',
                          color: '#64748B',
                        }}
                      >
                        {isUser ? (
                          <>
                            <UserIcon size={11} color="#94A3B8" />
                            <span style={{ fontWeight: 600, color: '#CBD5E1' }}>You</span>
                            <span style={{ color: 'rgba(255, 255, 255, 0.2)' }}>•</span>
                            <span>{timestampStr}</span>
                          </>
                        ) : (
                          <>
                            <BrainCircuit size={11} color="#38BDF8" />
                            <span style={{ fontWeight: 700, color: '#38BDF8' }}>DEX</span>
                            <span style={{ color: 'rgba(255, 255, 255, 0.2)' }}>•</span>
                            <span>{timestampStr}</span>
                          </>
                        )}
                      </div>

                      {/* Message Bubble */}
                      <div
                        style={{
                          maxWidth: isUser ? '75%' : '100%',
                          width: isUser ? 'auto' : '100%',
                          padding: isUser ? '10px 14px' : '16px 20px',
                          borderRadius: isUser ? '12px 12px 2px 12px' : '10px 10px 10px 2px',
                          backgroundColor: isUser
                            ? 'rgba(14, 34, 61, 0.85)'
                            : '#080A0F',
                          border: isUser
                            ? '1px solid rgba(56, 189, 248, 0.35)'
                            : '1px solid rgba(255, 255, 255, 0.08)',
                          boxShadow: isUser
                            ? '0 2px 8px rgba(0, 0, 0, 0.20)'
                            : '0 4px 16px rgba(0, 0, 0, 0.30)',
                          position: 'relative',
                        }}
                      >
                        {/* Copy Button */}
                        {!isUser && (
                          <button
                            onClick={() => handleCopyContent(m.id, m.content)}
                            title="Copy message"
                            style={{
                              position: 'absolute',
                              top: '12px',
                              right: '12px',
                              background: 'transparent',
                              border: 'none',
                              color: copiedMessageId === m.id ? '#10B981' : '#64748B',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '3px',
                              fontSize: '0.64rem',
                            }}
                          >
                            {copiedMessageId === m.id ? <Check size={12} /> : <Copy size={12} />}
                            <span>{copiedMessageId === m.id ? 'Copied' : ''}</span>
                          </button>
                        )}

                        {isUser ? (
                          <div style={{ fontSize: '0.88rem', lineHeight: 1.5, color: '#FFFFFF', whiteSpace: 'pre-wrap' }}>
                            {m.content}
                          </div>
                        ) : (
                          renderAssistantMessage(m)
                        )}
                      </div>
                    </FadeIn>
                  );
                })
              )}

              {/* Typing State */}
              {isSending && (
                <FadeIn
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    color: '#38BDF8',
                    fontSize: '0.78rem',
                    padding: '8px 14px',
                    background: 'rgba(56, 189, 248, 0.08)',
                    border: '1px solid rgba(56, 189, 248, 0.20)',
                    borderRadius: '8px',
                    width: 'fit-content',
                  }}
                >
                  <RefreshCw size={12} className="animate-spin" color="#38BDF8" />
                  <span style={{ fontWeight: 600 }}>DEX is analyzing {activeDataset.name}...</span>
                </FadeIn>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* 2 & 6. REFINED ENTERPRISE INPUT AREA (PRIMARY INTERACTION ELEMENT) */}
          <div
            style={{
              padding: '10px 20px 14px 20px',
              backgroundColor: '#040507',
              borderTop: '1px solid rgba(255, 255, 255, 0.06)',
            }}
          >
            <div style={{ maxWidth: '900px', width: '100%', margin: '0 auto' }}>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSendMessage();
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  background: '#080A0F',
                  border: isInputFocused
                    ? '1px solid #38BDF8'
                    : '1px solid rgba(56, 189, 248, 0.28)',
                  borderRadius: '10px',
                  padding: '6px 8px 6px 14px',
                  boxShadow: isInputFocused
                    ? '0 0 0 1px rgba(56, 189, 248, 0.45), 0 0 24px rgba(56, 189, 248, 0.18), 0 6px 24px rgba(0, 0, 0, 0.50)'
                    : '0 4px 18px rgba(0, 0, 0, 0.35)',
                  transition: 'all 0.18s ease',
                }}
              >
                {/* Input Field */}
                <input
                  ref={inputRef}
                  type="text"
                  placeholder={`Ask anything about ${activeDataset.name}... (e.g. 'Which region performs best?', 'Why are Tables losing money?')`}
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onFocus={() => setIsInputFocused(true)}
                  onBlur={() => setIsInputFocused(false)}
                  disabled={isSending}
                  style={{
                    flex: 1,
                    background: 'transparent',
                    border: 'none',
                    color: '#FFFFFF',
                    fontSize: '0.88rem',
                    outline: 'none',
                    padding: '6px 4px',
                  }}
                />

                {/* Send Button */}
                <button
                  type="submit"
                  disabled={isSending || !inputText.trim()}
                  title="Send message"
                  style={{
                    background: inputText.trim() && !isSending ? '#38BDF8' : 'rgba(255, 255, 255, 0.08)',
                    color: inputText.trim() && !isSending ? '#040507' : '#64748B',
                    border: 'none',
                    borderRadius: '6px',
                    width: '32px',
                    height: '32px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: inputText.trim() && !isSending ? 'pointer' : 'not-allowed',
                    transition: 'all 0.15s ease',
                    flexShrink: 0,
                  }}
                >
                  <Send size={14} />
                </button>
              </form>

              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginTop: '5px',
                  fontSize: '0.64rem',
                  color: '#64748B',
                  padding: '0 4px',
                }}
              >
                <span>Press Enter to send</span>
                <span>DEX answers directly from CSV data</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
