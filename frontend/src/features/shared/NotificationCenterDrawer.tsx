import React from 'react';
import { Drawer } from '../../design-system/Drawer';
import { Badge } from '../../design-system/Badge';
import { Bell, AlertTriangle, ShieldCheck, Play, CheckCircle2 } from 'lucide-react';
import { Link } from 'react-router-dom';

interface NotificationCenterDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const NotificationCenterDrawer: React.FC<NotificationCenterDrawerProps> = ({ isOpen, onClose }) => {
  const notifications = [
    {
      id: 'notif-1',
      title: '15-Min Critical SLA Alert: Courier Latency Surge',
      category: 'MONITORING',
      time: '4m ago',
      badge: 'CRITICAL',
      badgeVariant: 'rose' as const,
      route: '/monitoring',
    },
    {
      id: 'notif-2',
      title: 'Executive Governance Sign-Off Pending: DEC-2026-044',
      category: 'GOVERNANCE',
      time: '18m ago',
      badge: 'APPROVAL',
      badgeVariant: 'amber' as const,
      route: '/governance',
    },
    {
      id: 'notif-3',
      title: 'Autonomous Retention Playbook PBX-2026-Q1-001 Completed',
      category: 'PLAYBOOK',
      time: '1h ago',
      badge: 'SUCCESS',
      badgeVariant: 'emerald' as const,
      route: '/operating-system',
    },
  ];

  return (
    <Drawer isOpen={isOpen} onClose={onClose} title="Enterprise Notification Center" subtitle="Alerts, Escalations & Governance Approvals">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {notifications.map((n) => (
          <Link
            key={n.id}
            to={n.route}
            onClick={onClose}
            style={{
              padding: '16px',
              background: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid #1E293B',
              borderRadius: '10px',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
              textDecoration: 'none',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <span style={{ fontSize: '0.72rem', color: '#64748B', fontWeight: 800 }}>{n.category}</span>
              <Badge variant={n.badgeVariant} size="sm">
                {n.badge}
              </Badge>
            </div>
            <div style={{ fontSize: '0.84rem', fontWeight: 700, color: '#FFFFFF' }}>{n.title}</div>
            <div style={{ fontSize: '0.72rem', color: '#64748B' }}>{n.time}</div>
          </Link>
        ))}
      </div>
    </Drawer>
  );
};
