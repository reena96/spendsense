/**
 * Income Metrics Display (Story 6.2 - Task 6, AC #5)
 */

import React from 'react';
import type { IncomeMetrics } from '../types/signals';
import { formatCurrency, getPaymentFrequencyLabel } from '../utils/format';

interface IncomeMetricsProps {
  metrics: IncomeMetrics;
  timeWindow: string;
}

export function IncomeMetricsDisplay({ metrics, timeWindow }: IncomeMetricsProps) {
  const bufferStatus =
    metrics.cash_flow_buffer_months >= 2 ? 'good' :
    metrics.cash_flow_buffer_months >= 1 ? 'warning' : 'critical';

  const statusColors = {
    good: 'bg-green-50 text-green-700 border-green-200',
    warning: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    critical: 'bg-red-50 text-red-700 border-red-200',
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Income Metrics</h3>
        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">{timeWindow}</span>
      </div>

      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Payroll Deposits
            <span className="ml-2" title="Number of income transactions detected">ⓘ</span>
          </div>
          <div className="text-lg font-semibold text-gray-900">
            {metrics.payroll_count}
          </div>
        </div>

        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Payment Frequency
            <span className="ml-2" title="Detected pay schedule based on gaps">ⓘ</span>
          </div>
          <div className="text-lg font-semibold text-gray-900">
            {getPaymentFrequencyLabel(metrics.payment_frequency)}
            {metrics.payment_frequency !== 'unknown' && (
              <span className="ml-2 text-sm text-gray-500">
                (≈{Math.round(metrics.median_pay_gap_days)} days)
              </span>
            )}
          </div>
        </div>

        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Income Stability
            <span className="ml-2" title="Based on payment regularity">ⓘ</span>
          </div>
          <div className="flex items-center">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              metrics.has_regular_income
                ? 'bg-green-100 text-green-800'
                : 'bg-yellow-100 text-yellow-800'
            }`}>
              {metrics.has_regular_income ? 'Regular' : 'Irregular'}
            </span>
          </div>
        </div>

        <div className={`p-4 rounded-lg border ${statusColors[bufferStatus]}`}>
          <div className="text-sm font-medium mb-1">
            Cash Flow Buffer
            <span className="ml-2" title="Months of expenses covered by liquid assets">ⓘ</span>
          </div>
          <div className="text-2xl font-bold">
            {metrics.cash_flow_buffer_months.toFixed(1)} months
          </div>
          <div className="text-xs mt-1 opacity-80">
            {bufferStatus === 'good' ? 'Good buffer (≥2 months)' :
             bufferStatus === 'warning' ? 'Moderate buffer (1-2 months)' :
             'Low buffer (<1 month)'}
          </div>
        </div>

        <div className="pt-4 border-t border-gray-200 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Total Income</span>
            <span className="font-medium text-green-600">{formatCurrency(metrics.total_income)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
