/**
 * ConsentStatus component - Displays consent status badge
 * Story 6.6 - Consent Management Interface
 */

import React from 'react';

interface ConsentStatusProps {
  status: string;
  timestamp?: string | null;
  version?: string;
  showDetails?: boolean;
}

export const ConsentStatus: React.FC<ConsentStatusProps> = ({
  status,
  timestamp,
  version,
  showDetails = false,
}) => {
  const isOptedIn = status === 'opted_in';

  return (
    <div className="flex items-center gap-2">
      <span
        className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
          isOptedIn
            ? 'bg-green-100 text-green-800'
            : 'bg-red-100 text-red-800'
        }`}
      >
        {isOptedIn ? '✓ Opted In' : '✗ Opted Out'}
      </span>

      {showDetails && timestamp && (
        <span className="text-sm text-gray-600">
          Last changed: {new Date(timestamp).toLocaleString()}
        </span>
      )}

      {showDetails && version && (
        <span className="text-xs text-gray-500">
          Version {version}
        </span>
      )}
    </div>
  );
};
