/**
 * Subscriptions Detail Page
 * Shows active subscriptions with cost breakdown and overlap detection
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '../../components/dashboard/DashboardLayout';
import TimeWindowToggle, { TimeWindow } from '../../components/dashboard/TimeWindowToggle';
import TrendChart from '../../components/signals/TrendChart';

const SubscriptionsDetail: React.FC = () => {
  const navigate = useNavigate();
  const [timeWindow, setTimeWindow] = useState<TimeWindow>('30d');

  const trendData = [
    { label: 'Jan', value: 118 },
    { label: 'Feb', value: 124 },
    { label: 'Mar', value: 124 },
    { label: 'Apr', value: 131 },
  ];

  const subscriptions = [
    { name: 'Netflix', cost: 15.99, logo: '🎬', category: 'Entertainment' },
    { name: 'Spotify', cost: 10.99, logo: '🎵', category: 'Entertainment' },
    { name: 'Hulu', cost: 14.99, logo: '📺', category: 'Entertainment' },
    { name: 'Amazon Prime', cost: 14.99, logo: '📦', category: 'Shopping' },
    { name: 'iCloud Storage', cost: 9.99, logo: '☁️', category: 'Storage' },
    { name: 'Adobe Creative Cloud', cost: 54.99, logo: '🎨', category: 'Productivity' },
    { name: 'Gym Membership', cost: 39.99, logo: '💪', category: 'Health' },
  ];

  const totalCost = subscriptions.reduce((sum, sub) => sum + sub.cost, 0);
  const monthlyIncome = 4200; // Mock data
  const percentOfIncome = ((totalCost / monthlyIncome) * 100).toFixed(1);

  return (
    <DashboardLayout>
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4 focus:outline-none focus:ring-2 focus:ring-cyan-500 rounded px-2 py-1"
        >
          <span>←</span>
          <span>Back to Dashboard</span>
        </button>

        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Subscription Spending</h1>
            <p className="text-gray-600 mt-1">Your recurring monthly subscriptions</p>
          </div>
          <TimeWindowToggle onChange={setTimeWindow} />
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
          <p className="text-sm text-gray-600 mb-1">Active Subscriptions</p>
          <p className="text-2xl font-bold text-gray-900">{subscriptions.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
          <p className="text-sm text-gray-600 mb-1">Total Monthly Cost</p>
          <p className="text-2xl font-bold text-gray-900">${totalCost.toFixed(2)}</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
          <p className="text-sm text-gray-600 mb-1">% of Income</p>
          <p className="text-2xl font-bold text-yellow-600">{percentOfIncome}%</p>
        </div>
      </div>

      {/* Trend Chart */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8 border border-gray-100">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Monthly Subscription Cost Trend</h2>
        <TrendChart
          data={trendData}
          type="line"
          color="#0891b2"
          height={250}
          formatValue={(v) => `$${v}`}
        />
      </div>

      {/* Subscriptions List */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8 border border-gray-100">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Active Subscriptions</h2>
        <div className="space-y-3">
          {subscriptions.map((sub, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
              <div className="flex items-center gap-3">
                <span className="text-3xl">{sub.logo}</span>
                <div>
                  <p className="font-medium text-gray-900">{sub.name}</p>
                  <p className="text-sm text-gray-600">{sub.category}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-semibold text-gray-900">${sub.cost}</p>
                <p className="text-xs text-gray-500">/month</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Overlap Detection */}
      <div className="bg-yellow-50 rounded-lg p-6 mb-8 border border-yellow-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-3">Overlap Detected</h2>
        <div className="space-y-2 text-gray-700">
          <p>
            <strong>Netflix + Hulu:</strong> Both provide similar streaming content. Consider consolidating to one service and save $15/month.
          </p>
          <p className="text-sm text-gray-600 mt-3">
            Potential savings: <strong>$180/year</strong>
          </p>
        </div>
      </div>

      {/* What This Means */}
      <div className="bg-cyan-50 rounded-lg p-6 mb-8 border border-cyan-100">
        <h2 className="text-xl font-semibold text-gray-900 mb-3">What This Means</h2>
        <p className="text-gray-700">
          You're spending {percentOfIncome}% of your monthly income on subscriptions. Financial experts recommend keeping
          recurring expenses under 5% of income. Consider auditing your subscriptions quarterly to identify services you no longer use.
        </p>
      </div>

      {/* Related Recommendations */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Related Recommendations</h2>
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
            <span className="text-2xl">📋</span>
            <div className="flex-1">
              <p className="font-medium text-gray-900">Subscription Audit Checklist</p>
              <p className="text-sm text-gray-600">Step-by-step guide to review your subscriptions</p>
            </div>
            <span className="text-cyan-600">→</span>
          </div>
        </div>
      </div>

      {/* Ask Chat Button */}
      <div className="mt-8 text-center">
        <button
          onClick={() => navigate('/dashboard/chat?context=subscriptions')}
          className="inline-flex items-center gap-2 bg-cyan-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-cyan-700 transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2"
        >
          <span>💬</span>
          <span>Ask Chat About This</span>
        </button>
      </div>
    </DashboardLayout>
  );
};

export default SubscriptionsDetail;
