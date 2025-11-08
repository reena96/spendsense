/**
 * Savings Detail Page
 * Shows savings patterns, goals, and high-yield opportunities
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '../../components/dashboard/DashboardLayout';
import TimeWindowToggle, { TimeWindow } from '../../components/dashboard/TimeWindowToggle';
import TrendChart from '../../components/signals/TrendChart';

const SavingsDetail: React.FC = () => {
  const navigate = useNavigate();
  const [timeWindow, setTimeWindow] = useState<TimeWindow>('30d');

  const trendData = [
    { label: 'Jan', value: 8500 },
    { label: 'Feb', value: 9200 },
    { label: 'Mar', value: 9600 },
    { label: 'Apr', value: 9800 },
  ];

  const currentSavings = 9800;
  const monthlyIncome = 4200;
  const monthlyExpenses = 3500;
  const monthsCovered = (currentSavings / monthlyExpenses).toFixed(1);
  const goalMonths = 6;
  const goalAmount = monthlyExpenses * goalMonths;
  const progressPercent = ((currentSavings / goalAmount) * 100).toFixed(0);

  const highYieldAnnualEarnings = ((currentSavings * 0.045) - (currentSavings * 0.005)).toFixed(2);

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
            <h1 className="text-3xl font-bold text-gray-900">Savings Pattern</h1>
            <p className="text-gray-600 mt-1">Your emergency fund and savings growth</p>
          </div>
          <TimeWindowToggle onChange={setTimeWindow} />
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
          <p className="text-sm text-gray-600 mb-1">Current Savings</p>
          <p className="text-2xl font-bold text-gray-900">${currentSavings.toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
          <p className="text-sm text-gray-600 mb-1">Monthly Income</p>
          <p className="text-2xl font-bold text-gray-900">${monthlyIncome.toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
          <p className="text-sm text-gray-600 mb-1">Months Covered</p>
          <p className="text-2xl font-bold text-yellow-600">{monthsCovered}</p>
        </div>
      </div>

      {/* Savings Goal Progress */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8 border border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">6-Month Emergency Fund Goal</h2>
          <span className="text-2xl font-bold text-cyan-600">{progressPercent}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-6 overflow-hidden mb-3">
          <div
            className="h-full bg-gradient-to-r from-cyan-500 to-cyan-600 rounded-full transition-all flex items-center justify-end pr-2"
            style={{ width: `${progressPercent}%` }}
          >
            {parseInt(progressPercent) > 15 && (
              <span className="text-white text-xs font-semibold">{progressPercent}%</span>
            )}
          </div>
        </div>
        <div className="flex justify-between text-sm text-gray-600">
          <span>Current: ${currentSavings.toLocaleString()}</span>
          <span>Goal: ${goalAmount.toLocaleString()}</span>
        </div>
        <p className="text-sm text-gray-600 mt-3">
          You're ${(goalAmount - currentSavings).toLocaleString()} away from your 6-month emergency fund goal.
        </p>
      </div>

      {/* Trend Chart */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8 border border-gray-100">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Savings Growth Over Time</h2>
        <TrendChart
          data={trendData}
          type="line"
          color="#10b981"
          height={250}
          formatValue={(v) => `$${v.toLocaleString()}`}
        />
      </div>

      {/* High-Yield Opportunity */}
      <div className="bg-green-50 rounded-lg p-6 mb-8 border border-green-200">
        <h2 className="text-xl font-semibold text-gray-900 mb-3">💡 High-Yield Savings Opportunity</h2>
        <div className="space-y-2 text-gray-700">
          <p>
            Your current savings account earns approximately <strong>0.5% APY</strong>. High-yield savings accounts
            are currently offering up to <strong>4.5% APY</strong>.
          </p>
          <p className="text-sm text-gray-600 mt-3">
            By moving your ${currentSavings.toLocaleString()} to a high-yield account, you could earn an additional{' '}
            <strong>${highYieldAnnualEarnings}/year</strong> in interest.
          </p>
        </div>
      </div>

      {/* What This Means */}
      <div className="bg-cyan-50 rounded-lg p-6 mb-8 border border-cyan-100">
        <h2 className="text-xl font-semibold text-gray-900 mb-3">What This Means</h2>
        <p className="text-gray-700">
          You currently have {monthsCovered} months of expenses saved. Financial experts recommend saving 3-6 months
          of expenses as an emergency fund. You're making good progress toward this goal!
        </p>
      </div>

      {/* Related Recommendations */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Related Recommendations</h2>
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
            <span className="text-2xl">📘</span>
            <div className="flex-1">
              <p className="font-medium text-gray-900">Emergency Fund Guide</p>
              <p className="text-sm text-gray-600">Learn how to build and maintain your safety net</p>
            </div>
            <span className="text-cyan-600">→</span>
          </div>
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
            <span className="text-2xl">🏦</span>
            <div className="flex-1">
              <p className="font-medium text-gray-900">High-Yield Savings Accounts</p>
              <p className="text-sm text-gray-600">Compare top-rated savings accounts</p>
            </div>
            <span className="text-cyan-600">→</span>
          </div>
        </div>
      </div>

      {/* Ask Chat Button */}
      <div className="mt-8 text-center">
        <button
          onClick={() => navigate('/dashboard/chat?context=savings')}
          className="inline-flex items-center gap-2 bg-cyan-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-cyan-700 transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2"
        >
          <span>💬</span>
          <span>Ask Chat About This</span>
        </button>
      </div>
    </DashboardLayout>
  );
};

export default SavingsDetail;
