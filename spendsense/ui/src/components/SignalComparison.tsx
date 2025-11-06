/**
 * Signal Comparison Component (Story 6.2 - Task 7, AC #6)
 * Shows side-by-side comparison of 30-day vs 180-day signals
 */

import React from 'react';
import type { SignalMetrics } from '../types/signals';
import { formatCurrency, formatPercent } from '../utils/format';

interface SignalComparisonProps {
  data30d: SignalMetrics;
  data180d: SignalMetrics;
}

interface ComparisonRow {
  label: string;
  value30d: string | number;
  value180d: string | number;
  change?: string;
  changeDirection?: 'up' | 'down' | 'neutral';
}

export function SignalComparison({ data30d, data180d }: SignalComparisonProps) {
  const calculateChange = (val30: number, val180: number): { change: string; direction: 'up' | 'down' | 'neutral' } => {
    if (val180 === 0) return { change: '-', direction: 'neutral' };
    const pct = ((val30 - val180) / val180) * 100;
    return {
      change: `${pct > 0 ? '+' : ''}${pct.toFixed(1)}%`,
      direction: pct > 0 ? 'up' : pct < 0 ? 'down' : 'neutral'
    };
  };

  const rows: ComparisonRow[] = [
    {
      label: 'Subscription Merchants',
      value30d: data30d.subscription.recurring_merchants,
      value180d: data180d.subscription.recurring_merchants,
      ...calculateChange(data30d.subscription.recurring_merchants, data180d.subscription.recurring_merchants)
    },
    {
      label: 'Subscription Spend',
      value30d: formatCurrency(data30d.subscription.monthly_spend),
      value180d: formatCurrency(data180d.subscription.monthly_spend),
      ...calculateChange(data30d.subscription.monthly_spend, data180d.subscription.monthly_spend)
    },
    {
      label: 'Savings Net Inflow',
      value30d: formatCurrency(data30d.savings.net_inflow),
      value180d: formatCurrency(data180d.savings.net_inflow),
      ...calculateChange(data30d.savings.net_inflow, data180d.savings.net_inflow)
    },
    {
      label: 'Emergency Fund',
      value30d: `${data30d.savings.emergency_fund_months.toFixed(1)}mo`,
      value180d: `${data180d.savings.emergency_fund_months.toFixed(1)}mo`,
      ...calculateChange(data30d.savings.emergency_fund_months, data180d.savings.emergency_fund_months)
    },
    {
      label: 'Credit Utilization',
      value30d: formatPercent(data30d.credit.max_utilization_pct),
      value180d: formatPercent(data180d.credit.max_utilization_pct),
      ...calculateChange(data30d.credit.max_utilization_pct, data180d.credit.max_utilization_pct)
    },
    {
      label: 'Payroll Deposits',
      value30d: data30d.income.payroll_count,
      value180d: data180d.income.payroll_count,
      ...calculateChange(data30d.income.payroll_count, data180d.income.payroll_count)
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">30-Day vs 180-Day Comparison</h3>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4 font-medium text-gray-700">Metric</th>
              <th className="text-right py-3 px-4 font-medium text-gray-700">30 Days</th>
              <th className="text-right py-3 px-4 font-medium text-gray-700">180 Days</th>
              <th className="text-right py-3 px-4 font-medium text-gray-700">Change</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="py-3 px-4 text-gray-900">{row.label}</td>
                <td className="py-3 px-4 text-right font-medium text-gray-900">{row.value30d}</td>
                <td className="py-3 px-4 text-right font-medium text-gray-900">{row.value180d}</td>
                <td className="py-3 px-4 text-right">
                  <span className={`inline-flex items-center font-medium ${
                    row.changeDirection === 'up' ? 'text-green-600' :
                    row.changeDirection === 'down' ? 'text-red-600' :
                    'text-gray-500'
                  }`}>
                    {row.change}
                    {row.changeDirection === 'up' && ' ↑'}
                    {row.changeDirection === 'down' && ' ↓'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 p-3 bg-gray-50 rounded-lg text-xs text-gray-600">
        <strong>Note:</strong> Positive changes in credit utilization indicate worsening conditions.
        Increases in savings and income are generally positive.
      </div>
    </div>
  );
}
