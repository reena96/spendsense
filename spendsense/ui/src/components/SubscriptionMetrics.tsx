/**
 * Subscription Metrics Display (Story 6.2 - Task 3, AC #2)
 */

import React from 'react';
import type { SubscriptionMetrics } from '../types/signals';
import { formatCurrency, formatPercent } from '../utils/format';

interface SubscriptionMetricsProps {
  metrics: SubscriptionMetrics;
  timeWindow: string;
}

export function SubscriptionMetricsDisplay({ metrics, timeWindow }: SubscriptionMetricsProps) {
  const shareWarning = metrics.subscription_share_pct > 30;

  return (
    <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Subscription Metrics</h3>
        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">{timeWindow}</span>
      </div>

      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Recurring Merchants
            <span className="ml-2" title="Number of detected subscription merchants">ⓘ</span>
          </div>
          <div className="text-lg font-semibold text-gray-900">
            {metrics.recurring_merchants}
          </div>
        </div>

        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Monthly Spend
            <span className="ml-2" title="Average monthly subscription cost">ⓘ</span>
          </div>
          <div className="text-lg font-semibold text-gray-900">
            {formatCurrency(metrics.monthly_spend)}
          </div>
        </div>

        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Subscription Share
            <span className="ml-2" title="Percentage of total spending on subscriptions">ⓘ</span>
          </div>
          <div className={`text-lg font-semibold ${shareWarning ? 'text-red-600' : 'text-gray-900'}`}>
            {formatPercent(metrics.subscription_share_pct)}
            {shareWarning && (
              <span className="ml-2 text-xs text-red-600 bg-red-50 px-2 py-1 rounded">
                High
              </span>
            )}
          </div>
        </div>

        {metrics.detected_subscriptions.length > 0 && (
          <details className="mt-4 pt-4 border-t border-gray-200">
            <summary className="text-sm text-gray-600 cursor-pointer hover:text-gray-900">
              View {metrics.detected_subscriptions.length} Detected Subscriptions
            </summary>
            <div className="mt-2 space-y-2">
              {metrics.detected_subscriptions.slice(0, 5).map((sub, idx) => (
                <div key={idx} className="flex justify-between text-sm">
                  <span className="text-gray-600">{sub.merchant_name}</span>
                  <span className="font-medium">{formatCurrency(sub.monthly_amount)}</span>
                </div>
              ))}
            </div>
          </details>
        )}
      </div>
    </div>
  );
}
