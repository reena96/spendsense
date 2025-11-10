/**
 * Signal Dashboard Page (Story 6.2 - Main Page Component)
 * Comprehensive view of user behavioral signals
 */

import { useState } from 'react';
import { UserSearch } from '../components/UserSearch';
import { TimeWindowToggle } from '../components/TimeWindowToggle';
import { SubscriptionMetricsDisplay } from '../components/SubscriptionMetrics';
import { SavingsMetricsDisplay } from '../components/SavingsMetrics';
import { CreditMetricsDisplay } from '../components/CreditMetrics';
import { IncomeMetricsDisplay } from '../components/IncomeMetrics';
import { SignalComparison } from '../components/SignalComparison';
import { SignalExport } from '../components/SignalExport';
import { useSignalData } from '../hooks/useSignalData';
import { formatDate } from '../utils/format';
import type { UserSearchResult, TimeWindow } from '../types/signals';

export function SignalDashboard() {
  const [selectedUser, setSelectedUser] = useState<UserSearchResult | null>(null);
  const [timeWindow, setTimeWindow] = useState<TimeWindow>('both');

  const { data: signals, isLoading, error } = useSignalData(
    selectedUser?.user_id ?? null,
    timeWindow
  );

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            📊 User Signal Dashboard
          </h1>
          <p className="mt-2 text-gray-600">
            Comprehensive view of behavioral signals and persona insights
          </p>
        </div>

        {/* User Search */}
        <div className="mb-8">
          <UserSearch onSelectUser={setSelectedUser} />
        </div>

        {/* Selected User Info */}
        {selectedUser && (
          <div className="mb-6 p-4 bg-white rounded-lg shadow border border-gray-200">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">{selectedUser.name}</h2>
                <p className="text-sm text-gray-600">{selectedUser.user_id}</p>
              </div>
              <div className="flex items-center space-x-4">
                <span className="px-4 py-2 bg-blue-100 text-blue-800 rounded-lg font-medium">
                  {selectedUser.persona.replace(/_/g, ' ')}
                </span>
                <span className={`px-4 py-2 rounded-lg font-medium ${
                  selectedUser.consent_status === 'opted_in'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {selectedUser.consent_status === 'opted_in' ? '✓ Opted In' : '✗ Opted Out'}
                </span>
                <TimeWindowToggle selected={timeWindow} onChange={setTimeWindow} />
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center items-center py-12">
            <div className="text-center">
              <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
              <p className="text-gray-600">Loading signal data...</p>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="p-6 bg-red-50 border border-red-200 rounded-lg text-red-700">
            <p className="font-semibold mb-1">Error loading signals</p>
            <p className="text-sm">{error.message}</p>
          </div>
        )}

        {/* Signal Data Display */}
        {signals && !isLoading && (
          <>
            {/* Computed At Timestamp */}
            {(signals.data_30d || signals.data_180d) && (
              <div className="mb-4 text-sm text-gray-600">
                Last computed: {formatDate((signals.data_30d || signals.data_180d)!.computed_at)}
              </div>
            )}

            {/* Side-by-Side Comparison */}
            {timeWindow === 'both' && signals.data_30d && signals.data_180d && (
              <div className="mb-8">
                <SignalComparison data30d={signals.data_30d} data180d={signals.data_180d} />
              </div>
            )}

            {/* 30-Day Signals */}
            {(timeWindow === '30d' || timeWindow === 'both') && signals.data_30d && (
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  30-Day Signals
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <SubscriptionMetricsDisplay
                    metrics={signals.data_30d.subscription}
                    timeWindow="30 days"
                  />
                  <SavingsMetricsDisplay
                    metrics={signals.data_30d.savings}
                    timeWindow="30 days"
                  />
                  <CreditMetricsDisplay
                    metrics={signals.data_30d.credit}
                    timeWindow="30 days"
                  />
                  <IncomeMetricsDisplay
                    metrics={signals.data_30d.income}
                    timeWindow="30 days"
                  />
                </div>
              </div>
            )}

            {/* 180-Day Signals */}
            {(timeWindow === '180d' || timeWindow === 'both') && signals.data_180d && (
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  180-Day Signals
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <SubscriptionMetricsDisplay
                    metrics={signals.data_180d.subscription}
                    timeWindow="180 days"
                  />
                  <SavingsMetricsDisplay
                    metrics={signals.data_180d.savings}
                    timeWindow="180 days"
                  />
                  <CreditMetricsDisplay
                    metrics={signals.data_180d.credit}
                    timeWindow="180 days"
                  />
                  <IncomeMetricsDisplay
                    metrics={signals.data_180d.income}
                    timeWindow="180 days"
                  />
                </div>
              </div>
            )}

            {/* Raw Data View */}
            {(signals.data_30d || signals.data_180d) && (
              <div className="mb-8">
                <details className="bg-white rounded-lg shadow p-6 border border-gray-200">
                  <summary className="text-lg font-semibold text-gray-900 cursor-pointer hover:text-blue-600">
                    🔍 View Raw Signal Data
                  </summary>
                  <div className="mt-4 p-4 bg-gray-50 rounded-lg overflow-x-auto">
                    <pre className="text-xs text-gray-700">
                      {JSON.stringify(signals, null, 2)}
                    </pre>
                  </div>
                </details>
              </div>
            )}

            {/* Export Options */}
            <div className="max-w-md">
              <SignalExport userId={signals.user_id} />
            </div>
          </>
        )}

        {/* Empty State */}
        {!selectedUser && !isLoading && !error && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Search for a User
            </h3>
            <p className="text-gray-600">
              Enter a User ID or name in the search bar above to view their behavioral signals
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
