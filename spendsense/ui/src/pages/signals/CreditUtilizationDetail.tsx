/**
 * Credit Utilization Detail Page
 * Shows detailed credit utilization breakdown with trends and explanations
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '../../components/dashboard/DashboardLayout';
import TimeWindowToggle, { TimeWindow } from '../../components/dashboard/TimeWindowToggle';
import TrendChart from '../../components/signals/TrendChart';
import { fetchCreditSignal, CreditSignalResponse } from '../../services/api';

const CreditUtilizationDetail: React.FC = () => {
  const navigate = useNavigate();
  const [_timeWindow, setTimeWindow] = useState<TimeWindow>('30d');
  const [creditData, setCreditData] = useState<CreditSignalResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadCreditData = async () => {
      const userId = localStorage.getItem('spendsense_user_id');
      if (!userId) {
        navigate('/onboarding/welcome');
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const data = await fetchCreditSignal(userId);
        setCreditData(data);
      } catch (err) {
        console.error('Error loading credit data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load credit data');
      } finally {
        setLoading(false);
      }
    };

    loadCreditData();
  }, [navigate]);

  const trendData = [
    { label: 'Week 1', value: 62 },
    { label: 'Week 2', value: 65 },
    { label: 'Week 3', value: 68 },
    { label: 'Week 4', value: 68 },
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

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading credit data...</p>
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
      {!loading && !error && creditData && (
        <>
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
              <p className="text-sm text-gray-600 mb-1">Number of Cards</p>
              <p className="text-2xl font-bold text-gray-900">{creditData.num_credit_cards}</p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
              <p className="text-sm text-gray-600 mb-1">Overall Utilization</p>
              <p className={`text-2xl font-bold ${
                creditData.aggregate_utilization >= 0.7 ? 'text-red-600' :
                creditData.aggregate_utilization >= 0.5 ? 'text-yellow-600' :
                'text-green-600'
              }`}>
                {(creditData.aggregate_utilization * 100).toFixed(0)}%
              </p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
              <p className="text-sm text-gray-600 mb-1">High Utilization Cards</p>
              <p className="text-2xl font-bold text-gray-900">{creditData.high_utilization_count}</p>
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
            {creditData.per_card_details.length > 0 ? (
              <div className="space-y-4">
                {creditData.per_card_details.map((card, index) => {
                  const utilizationPct = (card.utilization * 100).toFixed(0);
                  return (
                    <div key={index} className="border-b border-gray-200 pb-4 last:border-b-0 last:pb-0">
                      <div className="flex items-center justify-between mb-2">
                        <p className="font-medium text-gray-900">{card.account_id}</p>
                        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                          card.utilization >= 0.7 ? 'bg-red-100 text-red-800' :
                          card.utilization >= 0.5 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {utilizationPct}%
                        </span>
                      </div>
                      <div className="flex items-center gap-3 text-sm text-gray-600 mb-2">
                        <span>Balance: ${card.balance.toLocaleString()}</span>
                        <span>•</span>
                        <span>Limit: ${card.limit.toLocaleString()}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all ${getUtilizationColor(card.utilization * 100)}`}
                          style={{ width: `${utilizationPct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-gray-600 text-center py-8">No credit cards found</p>
            )}
          </div>

          {/* What This Means */}
          <div className="bg-cyan-50 rounded-lg p-6 mb-8 border border-cyan-100">
            <h2 className="text-xl font-semibold text-gray-900 mb-3">What This Means</h2>
            <div className="space-y-2 text-gray-700">
              <p>
                <strong>Credit utilization</strong> is the percentage of your available credit that you're currently using.
                Financial experts recommend keeping your utilization below 30% to maintain a healthy credit score.
              </p>
              {creditData.per_card_details.length > 0 && creditData.per_card_details.some(card => card.utilization >= 0.5) && (
                <p>
                  You have {creditData.per_card_details.filter(card => card.utilization >= 0.5).length} card(s) with utilization above 50%,
                  which may negatively impact your credit score. Consider paying down these balances or requesting credit limit increases
                  to improve your utilization ratio.
                </p>
              )}
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
        </>
      )}
    </DashboardLayout>
  );
};

export default CreditUtilizationDetail;
