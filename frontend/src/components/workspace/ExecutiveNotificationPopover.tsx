import React, { useState } from 'react';
import { Bell, AlertTriangle, CheckCircle, Info, ArrowUpRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const ExecutiveNotificationPopover: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();

  const [notifications, setNotifications] = useState([
    {
      id: '1',
      type: 'ALERT',
      title: 'Critical Retention Drift Fired',
      message: 'Retention dropped to 79.5% (-7.3% vs target) in Southeastern corridors.',
      severity: 'CRITICAL',
      is_read: false,
      time: '12m ago',
      link: '/monitoring',
    },
    {
      id: '2',
      type: 'DECISION_REQUIRED',
      title: 'Decision Session Awaiting Ratification',
      message: 'Recovery Path A (Carrier Rebalancing) is awaiting executive board approval.',
      severity: 'WARNING',
      is_read: false,
      time: '45m ago',
      link: '/decision-copilot',
    },
    {
      id: '3',
      type: 'AI_INSIGHT',
      title: 'Forecast Accuracy Improved',
      message: 'Rolling 3-cycle forecast accuracy increased to 88.4% (+7.15%).',
      severity: 'INFO',
      is_read: true,
      time: '2h ago',
      link: '/ai-analyst',
    },
    {
      id: '4',
      type: 'REPORT_READY',
      title: 'Q4 Board Report Generated',
      message: 'Executive Briefing and Recovery Plan ready for PDF export.',
      severity: 'INFO',
      is_read: true,
      time: '5h ago',
      link: '/reports',
    },
  ]);

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  const markAllAsRead = () => {
    setNotifications(notifications.map((n) => ({ ...n, is_read: true })));
  };

  return (
    <div style={{ position: 'relative' }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'relative',
          background: 'rgba(15, 23, 42, 0.8)',
          border: '1px solid #1E293B',
          color: unreadCount > 0 ? '#38BDF8' : '#94A3B8',
          borderRadius: '6px',
          padding: '6px 8px',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
        title="Executive Notification Inbox"
      >
        <Bell size={14} />
        {unreadCount > 0 && (
          <span
            style={{
              position: 'absolute',
              top: '-4px',
              right: '-4px',
              width: '16px',
              height: '16px',
              borderRadius: '50%',
              backgroundColor: '#EF4444',
              color: '#FFFFFF',
              fontSize: '10px',
              fontWeight: 800,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div
          style={{
            position: 'absolute',
            top: '100%',
            right: 0,
            marginTop: '8px',
            width: '360px',
            backgroundColor: '#090D14',
            border: '1px solid #1E293B',
            borderRadius: '10px',
            boxShadow: '0 20px 40px rgba(0,0,0,0.9)',
            padding: '12px',
            zIndex: 100,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #1E293B', paddingBottom: '8px', marginBottom: '8px' }}>
            <div style={{ fontSize: '0.82rem', fontWeight: 800, color: '#FFFFFF' }}>
              Executive Notifications ({unreadCount} unread)
            </div>
            {unreadCount > 0 && (
              <button
                onClick={markAllAsRead}
                style={{ background: 'transparent', border: 'none', color: '#38BDF8', fontSize: '0.72rem', cursor: 'pointer', fontWeight: 600 }}
              >
                Mark all read
              </button>
            )}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: '320px', overflowY: 'auto' }}>
            {notifications.map((item) => (
              <div
                key={item.id}
                onClick={() => {
                  navigate(item.link);
                  setIsOpen(false);
                }}
                style={{
                  padding: '10px',
                  borderRadius: '6px',
                  backgroundColor: item.is_read ? 'rgba(15, 23, 42, 0.4)' : 'rgba(56, 189, 248, 0.08)',
                  border: `1px solid ${item.is_read ? '#1E293B' : 'rgba(56, 189, 248, 0.25)'}`,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2px' }}>
                  <span
                    style={{
                      fontSize: '0.68rem',
                      fontWeight: 700,
                      textTransform: 'uppercase',
                      color: item.severity === 'CRITICAL' ? '#EF4444' : item.severity === 'WARNING' ? '#F59E0B' : '#38BDF8',
                    }}
                  >
                    {item.type}
                  </span>
                  <span style={{ fontSize: '0.68rem', color: '#64748B' }}>{item.time}</span>
                </div>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#FFFFFF' }}>{item.title}</div>
                <div style={{ fontSize: '0.74rem', color: '#94A3B8', marginTop: '2px', lineHeight: 1.3 }}>{item.message}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
