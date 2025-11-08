/**
 * Dashboard Layout Component
 * Responsive wrapper with header, main content, and navigation
 * Handles desktop (split-screen), tablet, and mobile layouts
 */

import React, { ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import BottomTabNavigation from './BottomTabNavigation';
import FloatingChatButton from './FloatingChatButton';

interface DashboardLayoutProps {
  children: ReactNode;
  showBottomNav?: boolean;
  showFloatingChat?: boolean;
  chatUnreadCount?: number;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  children,
  showBottomNav = true,
  showFloatingChat = true,
  chatUnreadCount = 0,
}) => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-cyan-900">SpendSense</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-700 text-sm md:text-base">Welcome back!</span>
            <button
              id="settings-button"
              onClick={() => navigate('/dashboard/settings')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500"
              aria-label="Settings"
            >
              <span className="text-xl">⚙️</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8 pb-20 md:pb-8">
        {children}
      </main>

      {/* Bottom Tab Navigation (Mobile) */}
      {showBottomNav && <BottomTabNavigation />}

      {/* Floating Chat Button (Tablet/Desktop) */}
      {showFloatingChat && <FloatingChatButton unreadCount={chatUnreadCount} />}
    </div>
  );
};

export default DashboardLayout;
