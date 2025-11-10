/**
 * Income Stability Detail Page
 * Shows income patterns, variability, and deposit history
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, FileText, DollarSign, MessageCircle } from 'lucide-react';
import DashboardLayout from '../../components/dashboard/DashboardLayout';
import TimeWindowToggle, { TimeWindow } from '../../components/dashboard/TimeWindowToggle';
import TrendChart from '../../components/signals/TrendChart';
import { fetchIncomeSignal, IncomeSignalResponse } from '../../services/api';

const IncomeDetail: React.FC = () => {
  const navigate = useNavigate();
  const [_timeWindow, setTimeWindow] = useState<TimeWindow>('30d');
  const [incomeData, setIncomeData] = useState<IncomeSignalResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadIncomeData = async () => {
      const userId = localStorage.getItem('spendsense_user_id');
      if (!userId) {
        navigate('/onboarding/welcome');
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const data = await fetchIncomeSignal(userId);
        setIncomeData(data);
      } catch (err) {
        console.error('Error loading income data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load income data');
      } finally {
        setLoading(false);
      }
    };

    loadIncomeData();
  }, [navigate]);

  const trendData = [
    { label: 'Week 1', value: 0 },
    { label: 'Week 2', value: 2100 },
    { label: 'Week 3', value: 0 },
    { label: 'Week 4', value: 2100 },
  ];

  const getStabilityColor = (isRegular: boolean, variability: number) => {
    // Regular income with low variability = stable
    if (isRegular && variability < 0.2) {
      return { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-200', label: 'Stable' };
    }
    // Regular but higher variability = moderately stable
    if (isRegular) {
      return { bg: 'bg-yellow-100', text: 'text-yellow-800', border: 'border-yellow-200', label: 'Moderate' };
    }
    // Irregular income = variable
    return { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-200', label: 'Variable' };
  };

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
            <h1 className="text-3xl font-bold text-gray-900">Income Stability</h1>
            <p className="text-gray-600 mt-1">Your income pattern and consistency</p>
          </div>
          <TimeWindowToggle onChange={setTimeWindow} />
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading income data...</p>
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
      {!loading && !error && incomeData && (() => {
        const stabilityColors = getStabilityColor(incomeData.has_regular_income, incomeData.income_variability_cv);
        const monthlyIncome = (incomeData.total_income / (incomeData.window_days / 30)).toFixed(0);

        return (
          <>
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
                <p className="text-sm text-gray-600 mb-1">Total Income</p>
                <p className="text-2xl font-bold text-gray-900">${incomeData.total_income.toLocaleString()}</p>
                <p className="text-xs text-gray-500 mt-1">~${monthlyIncome}/month</p>
              </div>
              <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
                <p className="text-sm text-gray-600 mb-1">Payment Frequency</p>
                <p className="text-2xl font-bold text-gray-900">{incomeData.payment_frequency}</p>
                <p className="text-xs text-gray-500 mt-1">{incomeData.median_pay_gap_days} day gap</p>
              </div>
              <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
                <p className="text-sm text-gray-600 mb-1">Income Stability</p>
                <div className="flex items-center gap-2">
                  <p className={`text-2xl font-bold ${incomeData.has_regular_income ? 'text-green-600' : 'text-yellow-600'}`}>
                    {(incomeData.income_variability_cv * 100).toFixed(0)}%
                  </p>
                  <span className={`px-2 py-1 rounded-full text-xs font-semibold ${stabilityColors.bg} ${stabilityColors.text}`}>
                    {stabilityColors.label}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">Variability</p>
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
                  <strong>Pattern Detected:</strong> {incomeData.payment_frequency} ({incomeData.num_income_transactions} deposits)
                </p>
                <p>
                  <strong>Consistency:</strong> {incomeData.has_regular_income
                    ? 'Your income arrives on a regular schedule'
                    : 'Your income schedule varies'}
                  {incomeData.has_regular_income && incomeData.income_variability_cv < 0.2
                    ? ' with minimal variation in amounts.'
                    : '.'}
                </p>
                <p>
                  <strong>Variability:</strong> {incomeData.income_variability_cv < 0.2 ? 'Low' : incomeData.income_variability_cv < 0.5 ? 'Moderate' : 'High'}
                  ({(incomeData.income_variability_cv * 100).toFixed(1)}% coefficient of variation)
                </p>
                <p>
                  <strong>Cash Flow Buffer:</strong> {incomeData.cash_flow_buffer_months.toFixed(1)} months of expenses covered
                </p>
              </div>
            </div>

            {/* Recent Deposits */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-8 border border-gray-100">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Income Deposits</h2>
              {incomeData.payroll_dates.length > 0 ? (
                <div className="space-y-3">
                  {incomeData.payroll_dates.slice(0, 6).map((date, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-cyan-100 rounded-full flex items-center justify-center">
                          <DollarSign className="w-5 h-5 text-cyan-600" />
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">Income Deposit</p>
                          <p className="text-sm text-gray-600">
                            {new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-gray-900">
                          ${incomeData.avg_income_per_payment.toLocaleString()}
                        </p>
                        <span className="inline-block px-2 py-1 bg-cyan-50 text-cyan-700 text-xs font-medium rounded-full">
                          {incomeData.payment_frequency}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-600 text-center py-8">No income deposits found</p>
              )}
            </div>

            {/* What This Means */}
            <div className="bg-cyan-50 rounded-lg p-6 mb-8 border border-cyan-100">
              <h2 className="text-xl font-semibold text-gray-900 mb-3">What This Means</h2>
              <p className="text-gray-700">
                Your income follows a <strong>{incomeData.payment_frequency}</strong> pattern
                {incomeData.has_regular_income && ' with consistent deposit amounts'}.
                {incomeData.has_regular_income ? (
                  <> This regular income schedule makes budgeting predictable. Consider setting up automatic transfers
                  to savings on the same schedule to build wealth consistently.</>
                ) : (
                  <> Variable income requires more careful cash flow planning. Consider building a larger emergency fund
                  (6-12 months) and using percentage-based budgeting instead of fixed amounts.</>
                )}
              </p>
              {incomeData.cash_flow_buffer_months > 0 && (
                <p className="text-gray-700 mt-2">
                  You currently have {incomeData.cash_flow_buffer_months.toFixed(1)} months of cash flow buffer available.
                </p>
              )}
            </div>

            {/* Related Recommendations */}
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Related Recommendations</h2>
              <div className="space-y-3">
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
                  <FileText className="w-6 h-6 text-cyan-600" />
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">
                      {incomeData.has_regular_income ? `${incomeData.payment_frequency} Budget Template` : 'Variable Income Budget Guide'}
                    </p>
                    <p className="text-sm text-gray-600">Align your budget with your income schedule</p>
                  </div>
                  <span className="text-cyan-600">→</span>
                </div>
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
                  <DollarSign className="w-6 h-6 text-cyan-600" />
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
                <MessageCircle className="w-5 h-5" />
                <span>Ask Chat About This</span>
              </button>
            </div>
          </>
        );
      })()}
    </DashboardLayout>
  );
};

export default IncomeDetail;
