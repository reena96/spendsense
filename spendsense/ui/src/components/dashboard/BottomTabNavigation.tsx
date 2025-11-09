/**
 * Bottom Tab Navigation Component
 * Mobile navigation bar with 5 tabs
 * Fixed at bottom, 48px minimum touch targets
 */

import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export type TabId = 'dashboard' | 'signals' | 'tips' | 'chat' | 'more';

interface Tab {
  id: TabId;
  label: string;
  icon: string;
  path: string;
}

const tabs: Tab[] = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊', path: '/dashboard' },
  { id: 'signals', label: 'Signals', icon: '📈', path: '/dashboard/signals' },
  { id: 'tips', label: 'Tips', icon: '💡', path: '/dashboard/tips' },
  { id: 'chat', label: 'Chat', icon: '💬', path: '/dashboard/chat' },
  { id: 'more', label: 'More', icon: '⚙️', path: '/dashboard/settings' },
];

const BottomTabNavigation: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const getActiveTab = (): TabId => {
    const path = location.pathname;
    if (path === '/dashboard') return 'dashboard';
    if (path.startsWith('/dashboard/signals')) return 'signals';
    if (path.startsWith('/dashboard/tips')) return 'tips';
    if (path.startsWith('/dashboard/chat')) return 'chat';
    if (path.startsWith('/dashboard/settings')) return 'more';
    return 'dashboard';
  };

  const activeTab = getActiveTab();

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg z-40 md:hidden"
      role="navigation"
      aria-label="Mobile bottom navigation"
    >
      <div className="flex justify-around items-center h-16 px-2">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => navigate(tab.path)}
              className={`
                flex flex-col items-center justify-center
                min-w-[48px] min-h-[48px] px-3 py-2 rounded-lg
                transition-colors
                focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-inset
                ${
                  isActive
                    ? 'text-cyan-600'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }
              `}
              aria-label={tab.label}
              aria-current={isActive ? 'page' : undefined}
            >
              <span className="text-2xl mb-1" aria-hidden="true">{tab.icon}</span>
              <span className={`text-xs font-medium ${isActive ? 'font-semibold' : ''}`}>
                {tab.label}
              </span>
              {isActive && (
                <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-12 h-1 bg-cyan-600 rounded-t-full" />
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
};

export default BottomTabNavigation;
