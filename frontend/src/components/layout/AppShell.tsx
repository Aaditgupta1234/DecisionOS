import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { TopNav } from './TopNav';

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
  return (
    <div className="app-shell" style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      <Sidebar onOpenSearch={onOpenSearch} />
      <div className="main-content" style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, overflow: 'hidden' }}>
        <TopNav
          onOpenSearch={onOpenSearch}
          onOpenNotifications={onOpenNotifications}
          onOpenOnboarding={onOpenOnboarding}
        />
        <main style={{ flex: 1, padding: '24px', overflowY: 'auto', backgroundColor: '#030712' }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
};
