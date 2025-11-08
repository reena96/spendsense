/**
 * Income Stability Detail Page
 * Shows income patterns, variability, and deposit history
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '../../components/dashboard/DashboardLayout';
import TimeWindowToggle, { TimeWindow } from '../../components/dashboard/TimeWindowToggle';
import TrendChart from '../../components/signals/TrendChart';

const IncomeDetail: React.FC = () => {
  const navigate = useNavigate();
  const [timeWindow, setTimeWindow] = useState<TimeWindow>('30d');

  const trendData = [
    { label: 'Week 1', value: 0 },
    { label: 'Week 2', value: 2100 },
    { label: 'Week 3', value: 0 },
    { label: 'Week 4', value: 2100 },
  ];

  const recentDeposits = [
    { date: '2025-11-01', amount: 2100, source: 'Employer Payroll', type: 'biweekly' },
    { date: '2025-10-18', amount: 2100, source: 'Employer Payroll', type: 'biweekly' },
    { date: '2025-10-04', amount: 2100, source: 'Employer Payroll', type: 'biweekly' },
    { date: '2025-09-20', amount: 2100, source: 'Employer Payroll', type: 'biweekly' },
  ];

  const avgMonthlyIncome = 4200;
  const incomePattern = 'Biweekly';
  const stabilityScore = 95; // 0-100

  const getStabilityColor = (score: number) => {
    if (score >= 80) return { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-200' };
    if (score >= 60) return { bg: 'bg-yellow-100', text: 'text-yellow-800', border: 'border-yellow-200' };
    return { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-200' };
  };

  const stabilityColors = getStabilityColor(stabilityScore);

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
            <h1 className="text-3xl font-bold text-gray-900">Income Stability</h1>
            <p className="text-gray-600 mt-1">Your income pattern and consistency</p>
          </div>
          <TimeWindowToggle onChange={setTimeWindow} />
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
          <p className="text-sm text-gray-600 mb-1">Avg. Monthly Income</p>
          <p className="text-2xl font-bold text-gray-900">${avgMonthlyIncome.toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
          <p className="text-sm text-gray-600 mb-1">Income Pattern</p>
          <p className="text-2xl font-bold text-gray-900">{incomePattern}</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
          <p className="text-sm text-gray-600 mb-1">Stability Score</p>
          <div className="flex items-center gap-2">
            <p className="text-2xl font-bold text-green-600">{stabilityScore}</p>
            <span className={`px-2 py-1 rounded-full text-xs font-semibold ${stabilityColors.bg} ${stabilityColors.text}`}>
              Stable
            </span>
          </div>
        </div>
      </div>

      {/* Trend Chart */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8 border border-gray-100">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Income Pattern (Last 30 Days)</h2>
        <TrendChart
          data={trendData}
          type="bar"
          color="#0891b2"
          height={250}
          formatValue={(v) => `$${v.toLocaleString()}`}
        />
      </div>

      {/* Stability Indicator */}
      <div className={`rounded-lg p-6 mb-8 border ${stabilityColors.bg} ${stabilityColors.border}`}>
        <h2 className="text-xl font-semibold text-gray-900 mb-3">Stability Assessment</h2>
        <div className="space-y-2 text-gray-700">
          <p>
            <strong>Pattern Detected:</strong> Biweekly payroll deposits
          </p>
          <p>
            <strong>Consistency:</strong> Your income arrives on a regular schedule with minimal variation in amounts.
          </p>
          <p>
            <strong>Variability:</strong> Low (±2% variance over last 6 months)
          </p>
        </div>
      </div>

      {/* Recent Deposits */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8 border border-gray-100">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Income Deposits</h2>
        <div className="space-y-3">
          {recentDeposits.map((deposit, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-cyan-100 rounded-full flex items-center justify-center">
                  <span className="text-cyan-600 font-semibold">💵</span>
                </div>
                <div>
                  <p className="font-medium text-gray-900">{deposit.source}</p>
                  <p className="text-sm text-gray-600">{new Date(deposit.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-semibold text-gray-900">${deposit.amount.toLocaleString()}</p>
                <span className="inline-block px-2 py-1 bg-cyan-50 text-cyan-700 text-xs font-medium rounded-full">
                  {deposit.type}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* What This Means */}
      <div className="bg-cyan-50 rounded-lg p-6 mb-8 border border-cyan-100">
        <h2 className="text-xl font-semibold text-gray-900 mb-3">What This Means</h2>
        <p className="text-gray-700">
          Your income follows a <strong>biweekly</strong> pattern with consistent deposit amounts. This regular income
          schedule makes budgeting predictable. Consider setting up automatic transfers to savings on the same schedule
          to build wealth consistently.
        </p>
      </div>

      {/* Related Recommendations */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Related Recommendations</h2>
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
            <span className="text-2xl">📋</span>
            <div className="flex-1">
              <p className="font-medium text-gray-900">Biweekly Budget Template</p>
              <p className="text-sm text-gray-600">Align your budget with your income schedule</p>
            </div>
            <span className="text-cyan-600">→</span>
          </div>
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
            <span className="text-2xl">💰</span>
            <div className="flex-1">
              <p className="font-medium text-gray-900">Auto-Save Strategy</p>
              <p className="text-sm text-gray-600">Set up automatic transfers on payday</p>
            </div>
            <span className="text-cyan-600">→</span>
          </div>
        </div>
      </div>

      {/* Ask Chat Button */}
      <div className="mt-8 text-center">
        <button
          onClick={() => navigate('/dashboard/chat?context=income')}
          className="inline-flex items-center gap-2 bg-cyan-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-cyan-700 transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2"
        >
          <span>💬</span>
          <span>Ask Chat About This</span>
        </button>
      </div>
    </DashboardLayout>
  );
};

export default IncomeDetail;
