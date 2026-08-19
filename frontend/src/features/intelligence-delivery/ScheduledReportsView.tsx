import React, { useState } from 'react';
import { Send, Clock, CheckCircle2, Bell, Mail, ArrowRight, Play, MessageSquare } from 'lucide-react';
import { Card, Badge, Button, MetricTile } from '../../design-system';

export const ScheduledReportsView: React.FC = () => {
  const [dispatchedId, setDispatchedId] = useState<string | null>(null);

  const schedules = [
    { id: 'del-01', title: 'Monday Morning Executive Strategic Pulse', cadence: 'Weekly (Mon 08:00 UTC)', channels: 'Slack (#board-updates) + Email', format: 'Interactive Briefing + PDF', recipients: '14 Executives', status: 'ACTIVE', lastSent: 'Yesterday at 08:00 UTC' },
    { id: 'del-02', title: 'Monthly Boardroom Performance Briefing', cadence: 'Monthly (1st Day 09:00 UTC)', channels: 'Email + PDF Bundle', format: 'Full Slide Deck Deck', recipients: '8 Board Members', status: 'ACTIVE', lastSent: 'April 1, 2026' },
    { id: 'del-03', title: 'Real-Time Critical SLA & Churn Escalations', cadence: 'Trigger-Based (Immediate)', channels: 'Slack (#critical-alerts) + MS Teams', format: 'Decision Card', recipients: '22 Ops Leaders', status: 'ACTIVE', lastSent: '34m ago' },
  ];

  const handleTest = (id: string) => {
    setDispatchedId(id);
    setTimeout(() => setDispatchedId(null), 2000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '40px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#38BDF8', fontWeight: 800 }}>
            Automated Multi-Channel Intelligence Delivery
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 900, color: '#FFFFFF', margin: '4px 0 0 0' }}>
            Scheduled Intelligence Delivery & Distribution
          </h1>
        </div>

        <Button variant="primary" size="sm">
          + Create Intelligence Schedule
        </Button>
      </div>

      {/* Hero Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <MetricTile label="ACTIVE DELIVERY SCHEDULES" value="3 Active" sublabel="Dispatched on Automated Cron" valueColor="#38BDF8" />
        <MetricTile label="TOTAL RECIPIENTS REACHED" value="44 C-Suite" sublabel="Slack, MS Teams, Email" valueColor="#10B981" />
        <MetricTile label="DISPATCH SUCCESS RATE" value="100.0%" sublabel="Zero Failed Webhook Deliveries" valueColor="#A855F7" />
        <MetricTile label="AVG DISPATCH LATENCY" value="1.2s" sublabel="Instant Executive Alerts" valueColor="#F59E0B" />
      </div>

      {/* Schedules Table */}
      <Card style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ fontSize: '1rem', fontWeight: 800, color: '#FFFFFF' }}>Active Intelligence Distribution Schedules</span>
          <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Cron Orchestrator</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {schedules.map((s) => (
            <div
              key={s.id}
              style={{
                background: 'rgba(15, 23, 42, 0.6)',
                border: '1px solid #1E293B',
                borderRadius: '10px',
                padding: '18px 20px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '14px',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '0.98rem', fontWeight: 800, color: '#FFFFFF' }}>{s.title}</span>
                  <Badge variant="emerald" size="sm">
                    {s.status}
                  </Badge>
                </div>
                <div style={{ fontSize: '0.78rem', color: '#94A3B8', marginTop: '4px' }}>
                  Cadence: <strong style={{ color: '#FFFFFF' }}>{s.cadence}</strong> • Channels: {s.channels} • Recipients: {s.recipients}
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Button
                  variant="secondary"
                  size="sm"
                  icon={<Send size={12} />}
                  onClick={() => handleTest(s.id)}
                  disabled={dispatchedId === s.id}
                >
                  {dispatchedId === s.id ? 'Delivered!' : 'Send Test Brief'}
                </Button>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
