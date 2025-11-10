/**
 * Signal Export Component (Story 6.2 - Task 8, AC #10)
 */

import { useState } from 'react';
import { exportSignalData } from '../hooks/useSignalData';
import type { ExportFormat } from '../types/signals';

interface SignalExportProps {
  userId: string;
}

export function SignalExport({ userId }: SignalExportProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExport = async (format: ExportFormat) => {
    setIsExporting(true);
    setError(null);

    try {
      await exportSignalData(userId, format);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Export Data</h3>

      <div className="space-y-3">
        <button
          onClick={() => handleExport('csv')}
          disabled={isExporting}
          className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
        >
          {isExporting ? 'Exporting...' : '📊 Export as CSV'}
        </button>

        <button
          onClick={() => handleExport('json')}
          disabled={isExporting}
          className="w-full px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
        >
          {isExporting ? 'Exporting...' : '📄 Export as JSON'}
        </button>

        {error && (
          <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        <div className="text-xs text-gray-500 mt-2">
          CSV format includes: user_id, time_window, category, metric_name, metric_value, computed_at
        </div>
      </div>
    </div>
  );
}
