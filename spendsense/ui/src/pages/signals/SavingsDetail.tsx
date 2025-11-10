/**
 * Savings Detail Page
 * Shows savings patterns, goals, and high-yield opportunities
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, BookOpen, Building2, MessageCircle } from 'lucide-react';
import DashboardLayout from '../../components/dashboard/DashboardLayout';
import TimeWindowToggle, { TimeWindow } from '../../components/dashboard/TimeWindowToggle';
import TrendChart from '../../components/signals/TrendChart';
import { fetchSavingsSignal, SavingsSignalResponse } from '../../services/api';

const SavingsDetail: React.FC = () => {
  const navigate = useNavigate();
  const [_timeWindow, setTimeWindow] = useState<TimeWindow>('30d');
  const [savingsData, setSavingsData] = useState<SavingsSignalResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadSavingsData = async () => {
      const userId = localStorage.getItem('spendsense_user_id');
      if (!userId) {
        navigate('/onboarding/welcome');
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const data = await fetchSavingsSignal(userId);
        setSavingsData(data);
      } catch (err) {
        console.error('Error loading savings data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load savings data');
      } finally {
        setLoading(false);
      }
    };

    loadSavingsData();
  }, [navigate]);

  const trendData = [
    { label: 'Jan', value: 8500 },
    { label: 'Feb', value: 9200 },
    { label: 'Mar', value: 9600 },
    { label: 'Apr', value: 9800 },
  ];

  return (
    <DashboardLayout>
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4 focus:outline-none focus:ring-2 focus:ring-cyan-500 rounded px-2 py-1"
        >
          <ArrowLeft className="w-4 h-4" />
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

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading savings data...</p>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-800 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium"
          >
            Retry
          </button>
        </div>
      )}

      {/* Content */}
      {!loading && !error && savingsData && (
        <>
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
              <p className="text-sm text-gray-600 mb-1">Total Savings Balance</p>
              <p className="text-2xl font-bold text-gray-900">${savingsData.total_savings_balance.toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
              <p className="text-sm text-gray-600 mb-1">Avg Monthly Expenses</p>
              <p className="text-2xl font-bold text-gray-900">${savingsData.avg_monthly_expenses.toLocaleString()}</p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
              <p className="text-sm text-gray-600 mb-1">Emergency Fund</p>
              <p className={`text-2xl font-bold ${
                savingsData.emergency_fund_months >= 6 ? 'text-green-600' :
                savingsData.emergency_fund_months >= 3 ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {savingsData.emergency_fund_months.toFixed(1)} months
              </p>
            </div>
          </div>

          {/* Savings Goal Progress */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-8 border border-gray-100">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">6-Month Emergency Fund Goal</h2>
              <span className="text-2xl font-bold text-cyan-600">
                {((savingsData.emergency_fund_months / 6) * 100).toFixed(0)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-6 overflow-hidden mb-3">
              <div
                className="h-full bg-gradient-to-r from-cyan-500 to-cyan-600 rounded-full transition-all flex items-center justify-end pr-2"
                style={{ width: `${Math.min(100, (savingsData.emergency_fund_months / 6) * 100)}%` }}
              >
                {savingsData.emergency_fund_months >= 0.9 && (
                  <span className="text-white text-xs font-semibold">
                    {((savingsData.emergency_fund_months / 6) * 100).toFixed(0)}%
                  </span>
                )}
              </div>
            </div>
            <div className="flex justify-between text-sm text-gray-600">
              <span>Current: ${savingsData.total_savings_balance.toLocaleString()}</span>
              <span>Goal: ${(savingsData.avg_monthly_expenses * 6).toLocaleString()}</span>
            </div>
            {savingsData.emergency_fund_months < 6 && (
              <p className="text-sm text-gray-600 mt-3">
                You're ${((savingsData.avg_monthly_expenses * 6) - savingsData.total_savings_balance).toLocaleString()} away from your 6-month emergency fund goal.
              </p>
            )}
            {savingsData.emergency_fund_months >= 6 && (
              <p className="text-sm text-green-600 mt-3 font-semibold">
                🎉 Congratulations! You've reached your 6-month emergency fund goal!
              </p>
            )}
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
                By moving your ${savingsData.total_savings_balance.toLocaleString()} to a high-yield account, you could earn an additional{' '}
                <strong>${((savingsData.total_savings_balance * 0.045) - (savingsData.total_savings_balance * 0.005)).toFixed(2)}/year</strong> in interest.
              </p>
            </div>
          </div>

          {/* What This Means */}
          <div className="bg-cyan-50 rounded-lg p-6 mb-8 border border-cyan-100">
            <h2 className="text-xl font-semibold text-gray-900 mb-3">What This Means</h2>
            <p className="text-gray-700">
              You currently have {savingsData.emergency_fund_months.toFixed(1)} months of expenses saved. Financial experts recommend saving 3-6 months
              of expenses as an emergency fund.
              {savingsData.emergency_fund_months >= 6 ? ' You\'ve reached this goal - excellent work!' :
               savingsData.emergency_fund_months >= 3 ? ' You\'re making good progress toward this goal!' :
               ' Building this safety net should be a priority.'}
            </p>
            {savingsData.savings_growth_rate > 0 && (
              <p className="text-gray-700 mt-2">
                Your savings are growing at a rate of {(savingsData.savings_growth_rate * 100).toFixed(1)}% over the analysis period.
              </p>
            )}
          </div>

          {/* Related Recommendations */}
          <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Related Recommendations</h2>
            <div className="space-y-3">
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
                <BookOpen className="w-6 h-6 text-cyan-600" />
                <div className="flex-1">
                  <p className="font-medium text-gray-900">Emergency Fund Guide</p>
                  <p className="text-sm text-gray-600">Learn how to build and maintain your safety net</p>
                </div>
                <span className="text-cyan-600">→</span>
              </div>
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
                <Building2 className="w-6 h-6 text-cyan-600" />
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
              <MessageCircle className="w-5 h-5" />
              <span>Ask Chat About This</span>
            </button>
          </div>
        </>
      )}
    </DashboardLayout>
  );
};

export default SavingsDetail;
