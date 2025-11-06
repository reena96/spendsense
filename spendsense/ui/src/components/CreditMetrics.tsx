/**
 * Credit Metrics Display (Story 6.2 - Task 5, AC #4)
 */

import React from 'react';
import type { CreditMetrics } from '../types/signals';
import { formatPercent, getUtilizationColor } from '../utils/format';

interface CreditMetricsProps {
  metrics: CreditMetrics;
  timeWindow: string;
}

export function CreditMetricsDisplay({ metrics, timeWindow }: CreditMetricsProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Credit Metrics</h3>
        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">{timeWindow}</span>
      </div>

      <div className="space-y-4">
        <div className={`p-4 rounded-lg ${getUtilizationColor(metrics?.max_utilization_pct)}`}>
          <div className="text-sm font-medium mb-1">
            Max Credit Utilization
            <span className="ml-2" title="Healthy threshold: < 30%">ⓘ</span>
          </div>
          <div className="text-2xl font-bold">
            {formatPercent(metrics?.max_utilization_pct)}
          </div>
          <div className="text-xs mt-1 opacity-80">
            {!metrics?.max_utilization_pct ? 'No Data' :
             metrics.max_utilization_pct >= 70 ? 'Very High (>70%)' :
             metrics.max_utilization_pct >= 30 ? 'Moderate (30-70%)' :
             'Healthy (<30%)'}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className={`p-3 rounded-lg border ${metrics.has_interest_charges ? 'bg-yellow-50 border-yellow-200' : 'bg-gray-50 border-gray-200'}`}>
            <div className="text-xs text-gray-600 mb-1">Interest Charges</div>
            <div className={`text-lg font-semibold ${metrics.has_interest_charges ? 'text-yellow-700' : 'text-gray-900'}`}>
              {metrics.has_interest_charges ? 'Yes' : 'No'}
            </div>
          </div>

          <div className={`p-3 rounded-lg border ${metrics.minimum_payment_only ? 'bg-red-50 border-red-200' : 'bg-gray-50 border-gray-200'}`}>
            <div className="text-xs text-gray-600 mb-1">Min Payment Only</div>
            <div className={`text-lg font-semibold ${metrics.minimum_payment_only ? 'text-red-700' : 'text-gray-900'}`}>
              {metrics.minimum_payment_only ? 'Yes' : 'No'}
            </div>
          </div>
        </div>

        {metrics.overdue_status && (
          <div className="p-3 bg-red-100 border border-red-300 rounded-lg">
            <div className="flex items-center text-red-800">
              <span className="font-semibold mr-2">⚠️</span>
              <span className="font-medium">Overdue Payment Detected</span>
            </div>
          </div>
        )}

        <div className="pt-4 border-t border-gray-200 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Number of Cards</span>
            <span className="font-medium">{metrics.num_cards}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">High Utilization Count</span>
            <span className={`font-medium ${metrics.high_utilization_count > 0 ? 'text-red-600' : 'text-gray-900'}`}>
              {metrics.high_utilization_count}
            </span>
          </div>
        </div>

        {metrics.utilization_by_card && metrics.utilization_by_card.length > 0 && (
          <details className="mt-4 pt-4 border-t border-gray-200">
            <summary className="text-sm text-gray-600 cursor-pointer hover:text-gray-900">
              View Per-Card Utilization
            </summary>
            <div className="mt-2 space-y-2">
              {metrics.utilization_by_card.map((card, idx) => {
                const utilPct = card?.utilization_pct ?? 0;
                return (
                  <div key={idx} className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">{card?.card_name || 'Unknown Card'}</span>
                    <span className={`font-medium ${utilPct >= 70 ? 'text-red-600' : utilPct >= 30 ? 'text-yellow-600' : 'text-green-600'}`}>
                      {formatPercent(utilPct)}
                    </span>
                  </div>
                );
              })}
            </div>
          </details>
        )}
      </div>
    </div>
  );
}
