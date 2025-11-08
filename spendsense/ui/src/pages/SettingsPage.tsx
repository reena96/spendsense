/**
 * Settings & Consent Management Page
 * Complete settings with consent revocation, data download, and preferences
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '../components/dashboard/DashboardLayout';

const SettingsPage: React.FC = () => {
  const navigate = useNavigate();
  const [showRevokeModal, setShowRevokeModal] = useState(false);
  const [showAllPersonas, setShowAllPersonas] = useState(false);
  const [defaultTimeWindow, setDefaultTimeWindow] = useState('30d');

  // Mock user data
  const userId = localStorage.getItem('spendsense_user_id') || 'user-123';
  const personaData = JSON.parse(localStorage.getItem('spendsense_persona_data') || '{}');
  const consentDate = new Date('2025-11-01');

  const handleRevokeConsent = async () => {
    // TODO: API call to POST /api/consent with revoke action
    // await fetch(`/api/consent`, {
    //   method: 'POST',
    //   body: JSON.stringify({ user_id: userId, consent_status: false })
    // });

    localStorage.removeItem('spendsense_user_id');
    localStorage.removeItem('spendsense_persona_data');
    navigate('/onboarding/welcome');
  };

  const handleDataDownload = () => {
    const exportData = {
      user_id: userId,
      persona: personaData,
      consent_date: consentDate.toISOString(),
      exported_at: new Date().toISOString(),
      // In real app, would include signals, recommendations, etc.
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `spendsense_data_${userId}_${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleRestartTour = () => {
    navigate('/dashboard?tour=true');
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Settings</h1>

        {/* Account & Privacy */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6 border border-gray-100">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Account & Privacy</h2>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-600 mb-1">User ID</p>
              <p className="font-medium text-gray-900">{userId}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Financial Persona</p>
              <div className="flex items-center gap-2">
                <span className="px-3 py-1 bg-cyan-100 text-cyan-800 rounded-full text-sm font-semibold">
                  {personaData.persona_name || 'Young Professional'}
                </span>
              </div>
            </div>
            <div className="pt-4 border-t border-gray-200">
              <button
                onClick={() => alert('This feature displays all stored user data')}
                className="text-cyan-600 hover:text-cyan-700 font-medium focus:outline-none focus:underline"
              >
                View My Data
              </button>
            </div>
            <div>
              <button
                onClick={handleDataDownload}
                className="text-cyan-600 hover:text-cyan-700 font-medium focus:outline-none focus:underline"
              >
                Download My Data (JSON)
              </button>
            </div>
          </div>
        </div>

        {/* Data & Consent */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6 border border-gray-100">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Data & Consent</h2>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-600 mb-1">Consent Status</p>
              <p className="font-medium text-green-600">Active since {consentDate.toLocaleDateString()}</p>
            </div>
            <div>
              <button
                onClick={() => setShowAllPersonas(!showAllPersonas)}
                className="text-cyan-600 hover:text-cyan-700 font-medium focus:outline-none focus:underline"
              >
                {showAllPersonas ? 'Hide' : 'View'} What Data We Use
              </button>
              {showAllPersonas && (
                <div className="mt-3 p-4 bg-gray-50 rounded-lg text-sm text-gray-700">
                  <ul className="space-y-2 ml-4 list-disc">
                    <li>Transaction data from the last 180 days</li>
                    <li>Credit card balances and limits</li>
                    <li>Recurring payment patterns</li>
                    <li>Savings account balances</li>
                    <li>Income deposit patterns</li>
                  </ul>
                </div>
              )}
            </div>
            <div className="pt-4 border-t border-gray-200">
              <button
                onClick={() => setShowRevokeModal(true)}
                className="px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500"
              >
                Revoke Consent
              </button>
              <p className="text-xs text-gray-500 mt-2">
                This will stop all data processing and return you to the welcome screen
              </p>
            </div>
          </div>
        </div>

        {/* Preferences */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6 border border-gray-100">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Preferences</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Default Time Window
              </label>
              <select
                value={defaultTimeWindow}
                onChange={(e) => {
                  setDefaultTimeWindow(e.target.value);
                  localStorage.setItem('spendsense_time_window', e.target.value);
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
              >
                <option value="30d">30-Day View</option>
                <option value="180d">180-Day View</option>
                <option value="compare">Compare Both</option>
              </select>
            </div>
          </div>
        </div>

        {/* Help & Support */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6 border border-gray-100">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Help & Support</h2>
          <div className="space-y-3">
            <button
              onClick={handleRestartTour}
              className="block text-cyan-600 hover:text-cyan-700 font-medium focus:outline-none focus:underline"
            >
              Restart Dashboard Tour
            </button>
            <a
              href="#"
              onClick={(e) => {
                e.preventDefault();
                alert('FAQ page would open here');
              }}
              className="block text-cyan-600 hover:text-cyan-700 font-medium focus:outline-none focus:underline"
            >
              Frequently Asked Questions
            </a>
            <a
              href="mailto:support@spendsense.example.com"
              className="block text-cyan-600 hover:text-cyan-700 font-medium focus:outline-none focus:underline"
            >
              Contact Support
            </a>
            <a
              href="#"
              onClick={(e) => {
                e.preventDefault();
                alert('Privacy Policy would open here');
              }}
              className="block text-cyan-600 hover:text-cyan-700 font-medium focus:outline-none focus:underline"
            >
              Privacy Policy
            </a>
            <a
              href="#"
              onClick={(e) => {
                e.preventDefault();
                alert('Terms of Service would open here');
              }}
              className="block text-cyan-600 hover:text-cyan-700 font-medium focus:outline-none focus:underline"
            >
              Terms of Service
            </a>
          </div>
        </div>

        {/* About SpendSense */}
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">About SpendSense</h2>
          <div className="space-y-2 text-gray-700">
            <p className="text-sm">Version 1.0.0</p>
            <a
              href="#"
              onClick={(e) => {
                e.preventDefault();
                alert('How SpendSense Works explanation would open here');
              }}
              className="block text-cyan-600 hover:text-cyan-700 font-medium focus:outline-none focus:underline text-sm"
            >
              How SpendSense Works
            </a>
            <a
              href="#"
              onClick={(e) => {
                e.preventDefault();
                alert('All Personas explanation would open here');
              }}
              className="block text-cyan-600 hover:text-cyan-700 font-medium focus:outline-none focus:underline text-sm"
            >
              All Personas Explained
            </a>
          </div>
        </div>
      </div>

      {/* Revoke Consent Modal */}
      {showRevokeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" onClick={() => setShowRevokeModal(false)}>
          <div
            className="bg-white rounded-lg shadow-xl max-w-md w-full p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Revoke Consent?</h2>
            <p className="text-gray-700 mb-6">
              Are you sure? This will:
            </p>
            <ul className="space-y-2 mb-6 ml-4 list-disc text-gray-700">
              <li>Stop all data processing</li>
              <li>Delete your persona and recommendations</li>
              <li>Return you to the welcome screen</li>
              <li>You can opt back in anytime</li>
            </ul>
            <div className="flex gap-3">
              <button
                onClick={handleRevokeConsent}
                className="flex-1 px-4 py-3 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500"
              >
                Yes, Revoke Consent
              </button>
              <button
                onClick={() => setShowRevokeModal(false)}
                className="flex-1 px-4 py-3 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
};

export default SettingsPage;
