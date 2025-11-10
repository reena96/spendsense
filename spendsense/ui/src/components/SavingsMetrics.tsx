/**
 * Savings Metrics Display (Story 6.2 - Task 4, AC #3)
 */

import type { SavingsMetrics } from '../types/signals';
import { formatCurrency, formatPercent } from '../utils/format';

interface SavingsMetricsProps {
  metrics: SavingsMetrics;
  timeWindow: string;
}

export function SavingsMetricsDisplay({ metrics, timeWindow }: SavingsMetricsProps) {
  const emergencyFundStatus =
    metrics.emergency_fund_months >= 6 ? 'excellent' :
    metrics.emergency_fund_months >= 3 ? 'good' :
    metrics.emergency_fund_months >= 1 ? 'warning' : 'critical';

  const statusColors = {
    excellent: 'bg-green-50 text-green-700 border-green-200',
    good: 'bg-blue-50 text-blue-700 border-blue-200',
    warning: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    critical: 'bg-red-50 text-red-700 border-red-200',
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Savings Metrics</h3>
        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">{timeWindow}</span>
      </div>

      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Net Inflow
            <span className="ml-2" title="Net change in savings balance">ⓘ</span>
          </div>
          <div className={`text-lg font-semibold ${metrics.net_inflow >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {formatCurrency(metrics.net_inflow)}
          </div>
        </div>

        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Growth Rate
            <span className="ml-2" title="Percentage growth of savings">ⓘ</span>
          </div>
          <div className={`text-lg font-semibold ${metrics.growth_rate_pct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {formatPercent(metrics.growth_rate_pct)}
            {metrics.growth_rate_pct > 0 && ' ↑'}
            {metrics.growth_rate_pct < 0 && ' ↓'}
          </div>
        </div>

        <div className={`p-4 rounded-lg border ${statusColors[emergencyFundStatus]}`}>
          <div className="text-sm font-medium mb-1">Emergency Fund Coverage</div>
          <div className="text-2xl font-bold">
            {metrics.emergency_fund_months.toFixed(1)} months
          </div>
          <div className="text-xs mt-1 opacity-80">
            Goal: 3-6 months of expenses
          </div>
        </div>

        <div className="pt-4 border-t border-gray-200 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Total Balance</span>
            <span className="font-medium">{formatCurrency(metrics.total_balance)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Avg Monthly Expenses</span>
            <span className="font-medium">{formatCurrency(metrics.avg_monthly_expenses)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Has Savings Accounts</span>
            <span className={`font-medium ${metrics.has_savings_accounts ? 'text-green-600' : 'text-gray-400'}`}>
              {metrics.has_savings_accounts ? 'Yes' : 'No'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
