/**
 * Dashboard Header Component
 * Logo, user greeting, and settings access
 * Can be used standalone or as part of DashboardLayout
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';

interface HeaderProps {
  userName?: string;
  showSettings?: boolean;
}

const Header: React.FC<HeaderProps> = ({ userName = 'there', showSettings = true }) => {
  const navigate = useNavigate();

  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="text-cyan-600 font-bold text-2xl">SS</div>
          <h1 className="text-2xl font-bold text-cyan-900">SpendSense</h1>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-gray-700 text-sm md:text-base">
            Welcome back{userName !== 'there' ? `, ${userName}` : ''}!
          </span>
          {showSettings && (
            <button
              id="settings-button"
              onClick={() => navigate('/dashboard/settings')}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500"
              aria-label="Settings"
            >
              <span className="text-xl">⚙️</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
