/**
 * Credit Utilization Detail Page
 * Shows detailed credit utilization breakdown with trends and explanations
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '../../components/dashboard/DashboardLayout';
import TimeWindowToggle, { TimeWindow } from '../../components/dashboard/TimeWindowToggle';
import TrendChart from '../../components/signals/TrendChart';

const CreditUtilizationDetail: React.FC = () => {
  const navigate = useNavigate();
  const [timeWindow, setTimeWindow] = useState<TimeWindow>('30d');

  // Mock data - in real app, would come from API
  const trendData = [
    { label: 'Week 1', value: 62 },
    { label: 'Week 2', value: 65 },
    { label: 'Week 3', value: 68 },
    { label: 'Week 4', value: 68 },
  ];

  const cardBreakdown = [
    { name: 'Visa ****4523', balance: 3400, limit: 5000, utilization: 68 },
    { name: 'Mastercard ****8921', balance: 1200, limit: 3000, utilization: 40 },
    { name: 'Amex ****1234', balance: 500, limit: 10000, utilization: 5 },
  ];

  const getUtilizationColor = (util: number) => {
    if (util >= 70) return 'bg-red-500';
    if (util >= 50) return 'bg-yellow-500';
    if (util >= 30) return 'bg-cyan-500';
    return 'bg-green-500';
  };

  return (
    <DashboardLayout>
      {/* Header with Back Button */}
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
            <h1 className="text-3xl font-bold text-gray-900">Credit Utilization Details</h1>
            <p className="text-gray-600 mt-1">Understanding your credit card usage patterns</p>
          </div>
          <TimeWindowToggle onChange={setTimeWindow} />
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
          <p className="text-sm text-gray-600 mb-1">Current Balance</p>
          <p className="text-2xl font-bold text-gray-900">$5,100</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
          <p className="text-sm text-gray-600 mb-1">Total Credit Limit</p>
          <p className="text-2xl font-bold text-gray-900">$18,000</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
          <p className="text-sm text-gray-600 mb-1">Overall Utilization</p>
          <p className="text-2xl font-bold text-yellow-600">28%</p>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
          <p className="text-sm text-gray-600 mb-1">vs. Last Period</p>
          <p className="text-2xl font-bold text-red-600">↑ 6%</p>
        </div>
      </div>

      {/* Trend Chart */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8 border border-gray-100">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Utilization Trend</h2>
        <TrendChart
          data={trendData}
          type="line"
          color="#0891b2"
          height={250}
          formatValue={(v) => `${v}%`}
        />
      </div>

      {/* Per-Card Breakdown */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8 border border-gray-100">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Per-Card Breakdown</h2>
        <div className="space-y-4">
          {cardBreakdown.map((card, index) => (
            <div key={index} className="border-b border-gray-200 pb-4 last:border-b-0 last:pb-0">
              <div className="flex items-center justify-between mb-2">
                <p className="font-medium text-gray-900">{card.name}</p>
                <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                  card.utilization >= 70 ? 'bg-red-100 text-red-800' :
                  card.utilization >= 50 ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {card.utilization}%
                </span>
              </div>
              <div className="flex items-center gap-3 text-sm text-gray-600 mb-2">
                <span>Balance: ${card.balance.toLocaleString()}</span>
                <span>•</span>
                <span>Limit: ${card.limit.toLocaleString()}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${getUtilizationColor(card.utilization)}`}
                  style={{ width: `${card.utilization}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* What This Means */}
      <div className="bg-cyan-50 rounded-lg p-6 mb-8 border border-cyan-100">
        <h2 className="text-xl font-semibold text-gray-900 mb-3">What This Means</h2>
        <div className="space-y-2 text-gray-700">
          <p>
            <strong>Credit utilization</strong> is the percentage of your available credit that you're currently using.
            Financial experts recommend keeping your utilization below 30% to maintain a healthy credit score.
          </p>
          <p>
            Your Visa ****4523 is at 68% utilization, which may negatively impact your credit score.
            Consider paying down this balance or requesting a credit limit increase to improve your utilization ratio.
          </p>
        </div>
      </div>

      {/* Related Recommendations */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Related Recommendations</h2>
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
            <span className="text-2xl">📘</span>
            <div className="flex-1">
              <p className="font-medium text-gray-900">Understanding Credit Utilization</p>
              <p className="text-sm text-gray-600">Learn how utilization affects your credit score</p>
            </div>
            <span className="text-cyan-600">→</span>
          </div>
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
            <span className="text-2xl">🧮</span>
            <div className="flex-1">
              <p className="font-medium text-gray-900">Balance Payoff Calculator</p>
              <p className="text-sm text-gray-600">See how quickly you can pay down your balance</p>
            </div>
            <span className="text-cyan-600">→</span>
          </div>
        </div>
      </div>

      {/* Ask Chat About This Button */}
      <div className="mt-8 text-center">
        <button
          onClick={() => navigate('/dashboard/chat?context=credit-utilization')}
          className="inline-flex items-center gap-2 bg-cyan-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-cyan-700 transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2"
        >
          <span>💬</span>
          <span>Ask Chat About This</span>
        </button>
      </div>
    </DashboardLayout>
  );
};

export default CreditUtilizationDetail;
