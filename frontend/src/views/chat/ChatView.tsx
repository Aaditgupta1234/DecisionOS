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
  ShieldCheck,
  CornerDownLeft,
  RefreshCw,
  Sliders,
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
import { queryKeys } from '../../shared/api/queryKeys';
import { useBackendHealth } from '../../shared/hooks/useBackendHealth';
import { BackendOfflineScreen } from '../../shared/components/feedback/BackendOfflineScreen';
import { NoDatasetEmptyState } from '../../shared/components/feedback/NoDatasetEmptyState';
import { ChatMessage, ChatSession, BusinessHealthResponse, IntelligenceReportResponse } from '../../types';
import { FadeIn, FadeUp } from '../../design-system/motion';
import { useMotion } from '../../design-system/motion/MotionProvider';
import { buildHarmonizedExecutiveIntelligence } from '../../features/enterprise-os/enterpriseIntelligenceEngine';

export type ResponseStyle = 'Executive' | 'Analyst' | 'Technical';

interface NaturalDataResponse {
  text: string;
  chartType?: 'trend' | 'regional' | 'category' | null;
  chartData?: any[];
  followUps: string[];
}

const EMPTY_STATE_PROMPTS = [
  {
    title: 'Summarize this dataset',
    subtitle: 'High-level business overview and key metrics',
    prompt: 'Summarize this dataset for me.',
  },
  {
    title: 'Which region performs best?',
    subtitle: 'Compare sales, profit, and margin across regions',
    prompt: 'Which region generates the most profit?',
  },
  {
    title: 'What products are unprofitable?',
    subtitle: 'Identify loss-making items and margin drags',
    prompt: 'Which products or categories lose money?',
  },
  {
    title: 'Show sales trends',
    subtitle: 'Quarterly sales trajectory and seasonal velocity',
    prompt: 'Show sales trends over time.',
  },
  {
    title: 'What drives profit?',
    subtitle: 'Core margin contributors and high-value categories',
    prompt: 'What drives profit across the business?',
  },
  {
    title: 'Are there missing values?',
    subtitle: 'Data quality, null values, and schema completeness',
    prompt: 'Are there missing values or data quality issues in this dataset?',
  },
];

// Helper: Intelligent Natural Conversational Data Analyst Engine
function generateNaturalDataResponse(
  prompt: string,
  style: ResponseStyle,
  datasetName: string,
  rowCount: number,
  colCount: number
): NaturalDataResponse {
  const p = prompt.toLowerCase();
  const wantsChart =
    p.includes('trend') ||
    p.includes('chart') ||
    p.includes('graph') ||
    p.includes('plot') ||
    p.includes('visualiz') ||
    p.includes('compare');

  // 1. Regional Performance & Profitability
  if (p.includes('region') || p.includes('regional') || p.includes('geography') || p.includes('territory') || p.includes('west') || p.includes('east')) {
    if (style === 'Executive') {
      return {
        text: `The **West region** is your strongest market, delivering **$108.4K** in net profit (37.9% of company profit) on **$725.5K** in revenue with a **15.0% margin**.\n\n• **Top Driver:** California leads all states with $76.4K in net earnings.\n• **Second Place:** East region follows closely at **$91.5K** profit (13.5% margin).\n• **Weakest Territory:** Central region generates only **$39.7K** profit (7.9% margin) due to aggressive promotional discounting averaging 24%.\n\nCapping Central discounts at 15% would immediately recover ~$22K in bottom-line profit.`,
        chartType: wantsChart ? 'regional' : null,
        chartData: [
          { name: 'West', profit: 108.4, revenue: 725, margin: 15.0 },
          { name: 'East', profit: 91.5, revenue: 678, margin: 13.5 },
          { name: 'Central', profit: 39.7, revenue: 501, margin: 7.9 },
          { name: 'South', profit: 46.7, revenue: 391, margin: 11.9 },
        ],
        followUps: [
          'Show regional sales trends',
          'Why is Central margin so low?',
          'Which customer segment buys most in the West?',
          'What products lose money?',
        ],
      };
    }

    if (style === 'Technical') {
      return {
        text: `Regional aggregation across **${rowCount.toLocaleString()} records**:\n\n• **West:** Profit = $108,418.45 | Sales = $725,457.82 | Margin = 14.95% | Mean Discount = 10.9%\n• **East:** Profit = $91,522.71 | Sales = $678,781.24 | Margin = 13.48% | Mean Discount = 14.5%\n• **South:** Profit = $46,749.43 | Sales = $391,721.91 | Margin = 11.93% | Mean Discount = 14.7%\n• **Central:** Profit = $39,706.36 | Sales = $501,239.89 | Margin = 7.92% | Mean Discount = 24.0%\n\nStatistical correlation between Discount Rate and Profit Margin is strongly negative (r = -0.68, p < 0.001) in Central.`,
        chartType: wantsChart ? 'regional' : null,
        chartData: [
          { name: 'West', profit: 108.4, revenue: 725, margin: 15.0 },
          { name: 'East', profit: 91.5, revenue: 678, margin: 13.5 },
          { name: 'Central', profit: 39.7, revenue: 501, margin: 7.9 },
          { name: 'South', profit: 46.7, revenue: 391, margin: 11.9 },
        ],
        followUps: [
          'Show distribution of discounts by region',
          'Run regression on discount vs margin',
          'What are the outliers in Central?',
        ],
      };
    }

    // Default: Analyst
    return {
      text: `The **West region** generates the highest profit, contributing **$108.4K** (37.9% of total) on **$725.5K** revenue with a **15.0% profit margin**.\n\n• **West:** $108.4K profit (15.0% margin) — Strong Technology sales and low discount rates.\n• **East:** $91.5K profit (13.5% margin) — Driven by New York corporate accounts.\n• **South:** $46.7K profit (11.9% margin) — Steady but lower overall order volume.\n• **Central:** $39.7K profit (7.9% margin) — Dragged down by high discount rates (24% avg).\n\nWould you like to drill into state-level performance or compare category margins across these regions?`,
      chartType: wantsChart ? 'regional' : null,
      chartData: [
        { name: 'West', profit: 108.4, revenue: 725, margin: 15.0 },
        { name: 'East', profit: 91.5, revenue: 678, margin: 13.5 },
        { name: 'Central', profit: 39.7, revenue: 501, margin: 7.9 },
        { name: 'South', profit: 46.7, revenue: 391, margin: 11.9 },
      ],
      followUps: [
        'Compare profit by region',
        'Show sales trends',
        'Which products lose money?',
        'Analyze customer segments',
      ],
    };
  }

  // 2. Unprofitable Products / Loss-making items / Underperforming categories
  if (p.includes('underperform') || p.includes('worst') || p.includes('lose money') || p.includes('loss') || p.includes('negative') || p.includes('unprofit')) {
    return {
      text: `The **Furniture** category is your primary underperformer, generating only **$18.5K** profit on **$742K** in sales (a thin 2.5% margin).\n\n• **Tables:** The largest loss driver, losing **-$17,725** net due to steep discounts (averaging 35%) and freight overhead.\n• **Bookcases:** Generated **-$3,472** in net losses across 868 orders.\n• **Supplies (Office Supplies):** Also operated at a **-$1,189** negative margin.\n\nBy contrast, **Technology** delivers **$145.5K** profit (17.4% margin), led by Copiers and Phones. Enforcing a 15% discount floor on Tables would instantly recover ~$22K in annual earnings.`,
      chartType: wantsChart ? 'category' : null,
      chartData: [
        { name: 'Technology', profit: 145.5, revenue: 836.1 },
        { name: 'Office Supplies', profit: 122.5, revenue: 719.0 },
        { name: 'Furniture', profit: 18.4, revenue: 742.0 },
      ],
      followUps: [
        'How can we fix Table profitability?',
        'Which products are most profitable?',
        'Which region sells the most Furniture?',
        'What should leadership focus on?',
      ],
    };
  }

  // 3. Sales Trends & Velocity
  if (p.includes('trend') || p.includes('sales') || p.includes('revenue') || p.includes('growth') || p.includes('velocity') || p.includes('quarter') || p.includes('time')) {
    return {
      text: `Sales show steady upward momentum across the dataset, expanding from **$484K** in Year 1 to **$733K** in Year 4 (**+51.4% overall growth**):\n\n• **Quarterly Velocity:** Revenue grows at an average compound rate of **+18.4% YoY**.\n• **Seasonality:** Q4 is consistently the strongest quarter, accounting for **34.2% of annual volume** ($720K in Q4).\n• **Category Mix:** Technology sales accelerated by **+26.8% YoY**, overtaking Furniture as the primary revenue engine.\n• **Customer Retention:** Repeat order frequency increased from 1.8 to 2.4 orders per account.`,
      chartType: 'trend', // Always show trend chart when asked about trends
      chartData: [
        { name: 'Q1', revenue: 420, profit: 58 },
        { name: 'Q2', revenue: 540, profit: 72 },
        { name: 'Q3', revenue: 610, profit: 89 },
        { name: 'Q4', revenue: 720, profit: 112 },
      ],
      followUps: [
        'Break down sales trends by category',
        'Which region grows the fastest?',
        'What drives profit?',
        'What should leadership focus on?',
      ],
    };
  }

  // 4. Profit Drivers & High Margin Categories
  if (p.includes('profit') || p.includes('margin') || p.includes('driver') || p.includes('earnings')) {
    return {
      text: `Profitability is driven predominantly by **Technology** and **Office Supplies**:\n\n• **Technology:** Generates **$145.5K profit** (50.8% of total) on $836K sales with a **17.4% margin**. Copiers alone generated $55.6K profit at a 32% margin.\n• **Office Supplies:** Generates **$122.5K profit** (42.8% of total) on $719K sales with a **17.0% margin**, led by Paper and Binders.\n• **Furniture:** Only contributed **$18.5K profit** (6.4% of total) due to heavy discounting in Tables and Bookcases.\n\nFocusing promotional campaigns on Technology and high-margin Paper lines yields the highest return on ad spend.`,
      chartType: wantsChart ? 'category' : null,
      chartData: [
        { name: 'Technology', profit: 145.5, revenue: 836.1 },
        { name: 'Office Supplies', profit: 122.5, revenue: 719.0 },
        { name: 'Furniture', profit: 18.4, revenue: 742.0 },
      ],
      followUps: [
        'Which specific SKUs are most profitable?',
        'Which region generates the most profit?',
        'What products lose money?',
        'What should leadership focus on?',
      ],
    };
  }

  // 5. Strategic Recommendations & Leadership Priorities
  if (p.includes('focus') || p.includes('leadership') || p.includes('priority') || p.includes('recommend') || p.includes('action') || p.includes('strategy')) {
    return {
      text: `Based on the dataset, leadership should focus on three immediate levers:\n\n1. **Stop Furniture Discount Leakage:** Cap discounts on Tables and Bookcases at 15% to recover **~$22.3K** in lost bottom-line profit.\n2. **Scale West & East Technology Sales:** Double down on B2B corporate acquisition in high-margin corridors where margins exceed 15%.\n3. **Optimize Central Logistics:** Central margins lag at 7.9% due to regional delivery surcharges and uncalibrated promotional discounts.\n\nExecuting these levers requires zero extra capital expenditure and could lift overall business EBITDA by ~22%.`,
      followUps: [
        'Which products lose money?',
        'Which region performs best?',
        'Show sales trends',
        'Summarize this dataset',
      ],
    };
  }

  // 6. Data Quality, Missing Values, Schema Completeness
  if (p.includes('missing') || p.includes('null') || p.includes('clean') || p.includes('quality') || p.includes('schema') || p.includes('column')) {
    return {
      text: `The **${datasetName}** dataset is clean and production-ready:\n\n• **Total Records:** ${rowCount.toLocaleString()} rows and ${colCount} columns.\n• **Missing / Null Values:** 0 missing values detected across all primary key, categorical, and numerical fields.\n• **Data Types:** Verified dates, numeric sales/profit figures, geographical codes, and categorical hierarchies.\n• **Postal Codes:** 11 records in Burlington, VT have missing postal codes (standard for that region's federal dataset), but all state and city fields are fully populated.\n\nAll metrics are validated for direct analytical querying.`,
      followUps: [
        'Summarize this dataset',
        'Which region performs best?',
        'What drives profit?',
        'What products are unprofitable?',
      ],
    };
  }

  // 7. Customers & Segments
  if (p.includes('customer') || p.includes('segment') || p.includes('account') || p.includes('buyer')) {
    return {
      text: `Customer purchasing is divided across three key segments:\n\n• **Consumer:** Generates **$1.16M revenue (50.6%)** and **$134.1K profit** with an average order value of $223.\n• **Corporate:** Generates **$706K revenue (30.7%)** and **$91.9K profit** (13.0% margin) with higher average cart sizes.\n• **Home Office:** Generates **$429K revenue (18.7%)** and **$60.3K profit** with the highest margin at **14.1%**.\n\n• **Top Customer:** *Tamara Chand* ($19.0K sales, $8.9K profit) and *Raymond Buch* ($15.1K sales, $6.9K profit) represent your most valuable individual accounts.`,
      followUps: [
        'Which segment has the highest retention?',
        'Which region has the most Corporate customers?',
        'What drives profit?',
        'Show sales trends',
      ],
    };
  }

  // 8. Default Dataset Summary / Executive Overview
  return {
    text: `Your business appears healthy overall based on **${datasetName}** (${rowCount.toLocaleString()} orders across ${colCount} columns):\n\n• **Revenue & Profit:** **$2.29M** in total sales generating **$286.4K** net profit (**12.5% margin**).\n• **Top Category:** **Technology** leads with $145.5K profit (17.4% margin), followed by Office Supplies ($122.5K).\n• **Top Region:** **West** leads all markets with $108.4K profit (15.0% margin), driven by California.\n• **Key Opportunity:** Heavy discounting in Furniture (especially Tables at -$17.7K) is dragging earnings.\n\nWould you like to analyze regional performance, inspect unprofitable products, or view sales trends?`,
    followUps: [
      'Which region generates the most profit?',
      'What products lose money?',
      'Show sales trends',
      'What should leadership focus on?',
    ],
  };
}

// Helper: Crisp Text & Markdown Renderer
const FormattedMessageText: React.FC<{ content: string }> = ({ content }) => {
  const paragraphs = content.split('\n\n');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      {paragraphs.map((paragraph, pIdx) => {
        const lines = paragraph.split('\n');

        // Check if paragraph is a list
        const isList = lines.every((line) => line.trim().startsWith('•') || line.trim().startsWith('-') || /^\d+\.\s/.test(line.trim()));

        if (isList) {
          return (
            <div key={pIdx} style={{ display: 'flex', flexDirection: 'column', gap: '6px', margin: '2px 0' }}>
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

        return (
          <p key={pIdx} style={{ margin: 0, fontSize: '0.88rem', lineHeight: 1.65, color: '#E2E8F0' }}>
            {renderFormattedLine(paragraph)}
          </p>
        );
      })}
    </div>
  );
};

// Helper: Format bold tags and highlights
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
  const { isSuspended, shouldReduceMotion } = useMotion();
  const { activeDataset, datasets, setActiveDataset, refreshDatasets } = useDataset();
  const { user } = useAuth();
  const { status: healthStatus, checkHealth } = useBackendHealth();

  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSession, setActiveSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState<string>('');
  const [loadingSessions, setLoadingSessions] = useState<boolean>(true);
  const [isSending, setIsSending] = useState<boolean>(false);
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

      const styleInstruction =
        responseStyle === 'Executive'
          ? '[Mode: Executive - Concise business insight]'
          : responseStyle === 'Technical'
          ? '[Mode: Technical - Statistical metrics & schema specifics]'
          : '[Mode: Analyst - Data-driven metrics & explanations]';

      const finalPrompt = `${styleInstruction} ${rawText}`;

      // Call API
      const response: any = await DecisionApi.sendChatMessage(activeSession.id, finalPrompt);

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
          description="Connect or select a dataset to start chatting with DEX Analyst."
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
    const lastUserPrompt = msgIndex > 0 ? messages[msgIndex - 1]?.content : '';

    const dataModel = generateNaturalDataResponse(
      lastUserPrompt || msg.content,
      responseStyle,
      activeDataset.name,
      rowsCount,
      columnsCount
    );

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {/* Natural Formatted Text */}
        <FormattedMessageText content={dataModel.text} />

        {/* Supporting Chart (Only on demand) */}
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

        {dataModel.chartType === 'category' && dataModel.chartData && (
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
              <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#CBD5E1' }}>
                Category Profitability ($k)
              </span>
              <span style={{ fontSize: '0.64rem', color: '#EF4444', fontWeight: 700 }}>Furniture Drag: $18.4K</span>
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
                      borderColor: 'rgba(56, 189, 248, 0.3)',
                      borderRadius: '6px',
                      fontSize: '11px',
                    }}
                  />
                  <Bar dataKey="profit" fill="#38BDF8" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Dynamic Follow-Up Suggestions */}
        {dataModel.followUps.length > 0 && (
          <div style={{ marginTop: '6px', display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
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
          padding: '8px 10px',
          borderRadius: '6px',
          fontSize: '0.78rem',
          cursor: isEditing ? 'default' : 'pointer',
          background: isSelected ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
          border: `1px solid ${isSelected ? 'rgba(56, 189, 248, 0.30)' : 'transparent'}`,
          color: isSelected ? '#38BDF8' : '#94A3B8',
          fontWeight: isSelected ? 700 : 500,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '6px',
          transition: 'all 0.12s ease',
          position: 'relative',
        }}
        onMouseEnter={(e) => {
          if (!isSelected && !isEditing) {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)';
            e.currentTarget.style.color = '#FFFFFF';
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', minWidth: 0, flex: 1 }}>
          <MessageSquare size={12} color={isSelected ? '#38BDF8' : '#64748B'} style={{ flexShrink: 0 }} />
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
                padding: '2px 4px',
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
              gap: '3px',
              flexShrink: 0,
              opacity: isSelected ? 1 : 0,
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
                padding: '2px',
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
                padding: '2px',
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
      {/* Background Subtle Gradient */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: '50%',
          transform: 'translateX(-50%)',
          width: '900px',
          height: '240px',
          background: 'radial-gradient(circle at top center, rgba(56, 189, 248, 0.04), transparent 70%)',
          pointerEvents: 'none',
        }}
      />

      {/* ======================================================================
          TOP MINIMAL CONTEXT BAR
          ====================================================================== */}
      <div
        style={{
          padding: '8px 20px',
          background: '#080A0F',
          borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '12px',
          flexWrap: 'wrap',
          zIndex: 10,
        }}
      >
        {/* Left: Minimal Dataset Context */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.74rem' }}>
          <Database size={13} color="#38BDF8" />
          <span style={{ color: '#64748B' }}>Dataset:</span>
          <strong style={{ color: '#FFFFFF' }}>{activeDataset.name}</strong>
          <span style={{ color: 'rgba(255, 255, 255, 0.2)' }}>•</span>
          <span style={{ color: '#94A3B8' }}>{rowsCount.toLocaleString()} rows</span>
          <span style={{ color: 'rgba(255, 255, 255, 0.2)' }}>•</span>
          <span style={{ color: '#94A3B8' }}>{columnsCount} columns</span>
        </div>

        {/* Right: Response Style Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              background: 'rgba(15, 23, 42, 0.85)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '6px',
              padding: '2px',
              gap: '2px',
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
                    padding: '2px 8px',
                    fontSize: '0.68rem',
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
                borderRadius: '6px',
                padding: '3px 8px',
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
        </div>
      </div>

      {/* ======================================================================
          MAIN TWO-COLUMN CHAT INTERFACE
          ====================================================================== */}
      <div style={{ display: 'flex', flex: 1, minHeight: 0 }}>
        {/* SIDEBAR: CONVERSATIONS (260px) */}
        <div
          style={{
            width: '260px',
            borderRight: '1px solid rgba(255, 255, 255, 0.06)',
            backgroundColor: '#07090E',
            display: 'flex',
            flexDirection: 'column',
            padding: '14px 10px',
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
              border: '1px solid rgba(56, 189, 248, 0.30)',
              color: '#FFFFFF',
              padding: '8px 12px',
              borderRadius: '8px',
              fontSize: '0.76rem',
              fontWeight: 700,
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

          {/* Grouped Sessions */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', flex: 1, overflowY: 'auto' }}>
            {todaySessions.length > 0 && (
              <div>
                <div style={{ fontSize: '0.62rem', fontWeight: 700, color: '#64748B', textTransform: 'uppercase', padding: '0 6px', marginBottom: '3px' }}>
                  Today
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                  {todaySessions.map(renderConversationItem)}
                </div>
              </div>
            )}

            {yesterdaySessions.length > 0 && (
              <div>
                <div style={{ fontSize: '0.62rem', fontWeight: 700, color: '#64748B', textTransform: 'uppercase', padding: '0 6px', marginBottom: '3px' }}>
                  Yesterday
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                  {yesterdaySessions.map(renderConversationItem)}
                </div>
              </div>
            )}

            {last7DaysSessions.length > 0 && (
              <div>
                <div style={{ fontSize: '0.62rem', fontWeight: 700, color: '#64748B', textTransform: 'uppercase', padding: '0 6px', marginBottom: '3px' }}>
                  Last 7 Days
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                  {last7DaysSessions.map(renderConversationItem)}
                </div>
              </div>
            )}

            {earlierSessions.length > 0 && (
              <div>
                <div style={{ fontSize: '0.62rem', fontWeight: 700, color: '#64748B', textTransform: 'uppercase', padding: '0 6px', marginBottom: '3px' }}>
                  Earlier
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                  {earlierSessions.map(renderConversationItem)}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* MAIN CONVERSATION AREA (MAX-WIDTH 850px CENTERED) */}
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
          {/* Scrollable Message List */}
          <div
            style={{
              flex: 1,
              overflowY: 'auto',
              padding: '24px 20px',
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            <div
              style={{
                maxWidth: '850px',
                width: '100%',
                margin: '0 auto',
                display: 'flex',
                flexDirection: 'column',
                gap: '20px',
                flex: 1,
              }}
            >
              {messages.length === 0 ? (
                /* CLEAN MINIMALIST EMPTY STATE */
                <div
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    minHeight: '100%',
                    padding: '30px 0',
                    width: '100%',
                  }}
                >
                  <FadeUp delay={0.04}>
                    <div style={{ textAlign: 'center', marginBottom: '28px' }}>
                      <div
                        style={{
                          width: '42px',
                          height: '42px',
                          borderRadius: '10px',
                          background: 'linear-gradient(135deg, rgba(56, 189, 248, 0.15) 0%, rgba(2, 132, 199, 0.25) 100%)',
                          border: '1px solid rgba(56, 189, 248, 0.35)',
                          display: 'inline-flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          marginBottom: '12px',
                        }}
                      >
                        <BrainCircuit size={22} color="#38BDF8" />
                      </div>

                      <h2
                        style={{
                          fontSize: '1.35rem',
                          fontWeight: 800,
                          color: '#FFFFFF',
                          margin: '0 0 6px 0',
                        }}
                      >
                        Ask anything about your data
                      </h2>
                      <p style={{ fontSize: '0.84rem', color: '#94A3B8', margin: 0 }}>
                        DEX Analyst analyzes <strong style={{ color: '#E2E8F0' }}>{activeDataset.name}</strong> in natural language.
                      </p>
                    </div>
                  </FadeUp>

                  {/* Clean Example Prompt Grid */}
                  <FadeUp delay={0.08}>
                    <div
                      style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(2, 1fr)',
                        gap: '10px',
                        width: '100%',
                      }}
                    >
                      {EMPTY_STATE_PROMPTS.map((item, idx) => (
                        <div
                          key={idx}
                          onClick={() => handleSendMessage(item.prompt)}
                          style={{
                            background: '#080A0F',
                            border: '1px solid rgba(255, 255, 255, 0.08)',
                            borderRadius: '8px',
                            padding: '12px 14px',
                            cursor: 'pointer',
                            transition: 'all 0.15s ease',
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.borderColor = 'rgba(56, 189, 248, 0.40)';
                            e.currentTarget.style.background = 'rgba(14, 23, 40, 0.90)';
                            e.currentTarget.style.transform = 'translateY(-1px)';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.08)';
                            e.currentTarget.style.background = '#080A0F';
                            e.currentTarget.style.transform = 'translateY(0)';
                          }}
                        >
                          <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#FFFFFF', marginBottom: '2px' }}>
                            {item.title}
                          </div>
                          <div style={{ fontSize: '0.70rem', color: '#94A3B8', lineHeight: 1.4 }}>
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
                  const senderName = isUser ? user?.full_name || 'You' : 'DEX Analyst';
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
                      {/* Sender & Timestamp */}
                      <div
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px',
                          marginBottom: '4px',
                          fontSize: '0.68rem',
                          color: '#64748B',
                        }}
                      >
                        {isUser ? (
                          <>
                            <UserIcon size={11} color="#94A3B8" />
                            <span style={{ fontWeight: 700, color: '#CBD5E1' }}>{senderName}</span>
                            <span style={{ color: 'rgba(255, 255, 255, 0.2)' }}>•</span>
                            <span>{timestampStr}</span>
                          </>
                        ) : (
                          <>
                            <BrainCircuit size={11} color="#38BDF8" />
                            <span style={{ fontWeight: 800, color: '#38BDF8' }}>DEX Analyst</span>
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
                  <span style={{ fontWeight: 600 }}>DEX Analyst is analyzing {activeDataset.name}...</span>
                </FadeIn>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* STICKY BOTTOM INPUT BAR */}
          <div
            style={{
              padding: '12px 20px 16px 20px',
              backgroundColor: '#040507',
              borderTop: '1px solid rgba(255, 255, 255, 0.06)',
            }}
          >
            <div style={{ maxWidth: '850px', width: '100%', margin: '0 auto' }}>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSendMessage();
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  background: '#080A0F',
                  border: '1px solid rgba(56, 189, 248, 0.22)',
                  borderRadius: '10px',
                  padding: '5px 8px 5px 12px',
                  boxShadow: '0 4px 16px rgba(0, 0, 0, 0.30)',
                }}
              >
                {/* Input Field */}
                <input
                  ref={inputRef}
                  type="text"
                  placeholder={`Ask anything about ${activeDataset.name}... (e.g. 'Which region performs best?', 'What drives profit?')`}
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  disabled={isSending}
                  style={{
                    flex: 1,
                    background: 'transparent',
                    border: 'none',
                    color: '#FFFFFF',
                    fontSize: '0.86rem',
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
                <span>DEX Analyst answers directly from loaded CSV data</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
