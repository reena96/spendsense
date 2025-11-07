/**
 * ConsentHistory - Timeline of consent changes
 * Story 6.6 - Consent Management Interface
 */

import React from 'react';
import { useConsentHistory, ConsentHistoryEntry } from '../hooks/useConsent';

interface ConsentHistoryProps {
  userId: string;
}

export const ConsentHistory: React.FC<ConsentHistoryProps> = ({ userId }) => {
  const { data, isLoading, error } = useConsentHistory(userId);

  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded">
        <p className="text-red-800">Failed to load consent history</p>
      </div>
    );
  }

  const history: ConsentHistoryEntry[] = data?.history || [];
  const totalChanges = data?.total_changes || 0;

  if (totalChanges === 0) {
    return (
      <div className="p-4 bg-gray-50 rounded text-center">
        <p className="text-gray-600">No consent changes recorded</p>
      </div>
    );
  }

  const isRecent = (timestamp: string) => {
    const changeDate = new Date(timestamp);
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    return changeDate > sevenDaysAgo;
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Consent Change History</h3>
        <span className="text-sm text-gray-500">{totalChanges} changes</span>
      </div>

      <div className="space-y-4">
        {history.map((entry, index) => (
          <div
            key={index}
            className={`border-l-4 pl-4 py-3 ${
              isRecent(entry.timestamp)
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 bg-white'
            }`}
          >
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center gap-2">
                {entry.old_status && (
                  <>
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${
                        entry.old_status === 'opted_in'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {entry.old_status === 'opted_in' ? 'Opted In' : 'Opted Out'}
                    </span>
                    <span className="text-gray-400">→</span>
                  </>
                )}
                <span
                  className={`px-2 py-1 rounded text-xs font-medium ${
                    entry.new_status === 'opted_in'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {entry.new_status === 'opted_in' ? 'Opted In' : 'Opted Out'}
                </span>
              </div>

              <span className="text-xs text-gray-500">
                {new Date(entry.timestamp).toLocaleString()}
              </span>
            </div>

            <div className="text-sm text-gray-700">
              <p>
                <strong>Changed by:</strong>{' '}
                {entry.operator_name || entry.changed_by === 'user' ? 'User' : entry.changed_by}
              </p>
              {entry.reason && (
                <p className="mt-1">
                  <strong>Reason:</strong> {entry.reason}
                </p>
              )}
            </div>

            {isRecent(entry.timestamp) && (
              <span className="inline-block mt-2 text-xs text-blue-600 font-medium">
                Recent (last 7 days)
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
