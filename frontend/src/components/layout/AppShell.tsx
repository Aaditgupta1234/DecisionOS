import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { Sidebar } from './Sidebar';
import { TopNav } from './TopNav';
import { PageTransition } from '../../design-system/motion';

interface AppShellProps {
  onOpenSearch?: () => void;
  onOpenNotifications?: () => void;
  onOpenOnboarding?: () => void;
}

export const AppShell: React.FC<AppShellProps> = ({
  onOpenSearch,
  onOpenNotifications,
  onOpenOnboarding,
}) => {
  const location = useLocation();

  return (
    <div className="app-shell" style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      <Sidebar onOpenSearch={onOpenSearch} />
      <div className="main-content" style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, overflow: 'hidden' }}>
        <TopNav
          onOpenSearch={onOpenSearch}
          onOpenNotifications={onOpenNotifications}
          onOpenOnboarding={onOpenOnboarding}
        />
        <main
          style={{
            flex: 1,
            padding: '16px 20px 36px 20px',
            overflowY: 'auto',
            backgroundColor: '#040507',
            backgroundImage: 'radial-gradient(circle at 50% -12%, rgba(56, 189, 248, 0.08) 0%, transparent 60%)',
          }}
        >
          <AnimatePresence mode="wait" initial={false}>
            <PageTransition key={location.pathname}>
              <Outlet />
            </PageTransition>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
};

