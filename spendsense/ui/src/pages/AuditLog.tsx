/**
 * Audit Log Page - Epic 6 Story 6.5
 *
 * Comprehensive audit trail viewer for compliance officers with filtering,
 * search, and export capabilities. Requires admin or compliance role.
 */

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';

interface AuditLogEntry {
  log_id: string;
  event_type: string;
  user_id: string | null;
  operator_id: string | null;
  recommendation_id: string | null;
  timestamp: string;
  event_data: Record<string, any>;
  ip_address: string | null;
  user_agent: string | null;
}

interface AuditLogResponse {
  entries: AuditLogEntry[];
  total_count: number;
  page: number;
  page_size: number;
}

interface FilterState {
  event_type: string;
  user_id: string;
  operator_id: string;
  start_date: string;
  end_date: string;
  page: number;
  page_size: number;
}

const EVENT_TYPES = [
  'all',
  'recommendation_generated',
  'consent_changed',
  'eligibility_checked',
  'tone_validated',
  'operator_action',
  'persona_assigned',
  'persona_overridden',
  'login_attempt',
  'unauthorized_access',
];

const EVENT_TYPE_COLORS: Record<string, string> = {
  recommendation_generated: 'bg-blue-100 text-blue-800',
  consent_changed: 'bg-purple-100 text-purple-800',
  eligibility_checked: 'bg-yellow-100 text-yellow-800',
  tone_validated: 'bg-orange-100 text-orange-800',
  operator_action: 'bg-green-100 text-green-800',
  persona_assigned: 'bg-indigo-100 text-indigo-800',
  persona_overridden: 'bg-red-100 text-red-800',
  login_attempt: 'bg-gray-100 text-gray-800',
  unauthorized_access: 'bg-red-100 text-red-800',
};

export default function AuditLog() {
  // Auto-populate operator_id from localStorage
  const loggedInOperatorId = localStorage.getItem('operator_id') || '';

  const [filters, setFilters] = useState<FilterState>({
    event_type: 'all',
    user_id: 'user_MASKED_000',
    operator_id: loggedInOperatorId,
    start_date: '',
    end_date: '',
    page: 1,
    page_size: 50,
  });

  const [selectedEntry, setSelectedEntry] = useState<AuditLogEntry | null>(null);
  const [showExportModal, setShowExportModal] = useState(false);

  // Fetch audit log entries
  const { data, isLoading, error } = useQuery<AuditLogResponse>({
    queryKey: ['auditLog', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.event_type !== 'all') params.append('event_type', filters.event_type);
      if (filters.user_id) params.append('user_id', filters.user_id);
      if (filters.operator_id) params.append('operator_id', filters.operator_id);
      if (filters.start_date) params.append('start_date', filters.start_date);
      if (filters.end_date) params.append('end_date', filters.end_date);
      params.append('page', filters.page.toString());
      params.append('page_size', filters.page_size.toString());

      const response = await fetch(`/api/operator/audit/log?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('operator_token')}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('AUTHENTICATION_REQUIRED');
        }
        throw new Error('Failed to fetch audit log');
      }

      return response.json();
    },
  });

  const handleExport = async (format: 'csv' | 'json') => {
    const params = new URLSearchParams();
    params.append('format', format);
    if (filters.event_type !== 'all') params.append('event_type', filters.event_type);
    if (filters.user_id) params.append('user_id', filters.user_id);
    if (filters.operator_id) params.append('operator_id', filters.operator_id);
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);

    const response = await fetch(`/api/operator/audit/export?${params}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('operator_token')}`,
      },
    });

    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit_log_${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    }

    setShowExportModal(false);
  };

  const totalPages = data ? Math.ceil(data.total_count / filters.page_size) : 0;

  // Handle authentication error
  if (error && (error as Error).message === 'AUTHENTICATION_REQUIRED') {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6">
            <h3 className="text-lg font-medium text-yellow-800 mb-3">Authentication Required</h3>
            <p className="text-sm text-yellow-700 mb-3">
              This page requires admin or compliance role authentication.
              To test, open your browser console (F12) and run:
            </p>
            <pre className="p-3 bg-yellow-100 rounded text-xs overflow-x-auto font-mono mb-3">
localStorage.setItem('operator_token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X2FkbWluIiwidXNlcm5hbWUiOiJhZG1pbl91c2VyIiwicm9sZSI6ImFkbWluIiwidHlwZSI6ImFjY2VzcyIsImV4cCI6MTc2MjQ1ODg0OCwiaWF0IjoxNzYyNDU1MjQ4fQ.rPA76eg6jrehg1cT4NrhOIXHpj3XkUHbSIiN6x-ebQ0')
            </pre>
            <p className="text-sm text-yellow-700">Then refresh the page.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Audit Log</h1>
        <p className="text-gray-600 mt-2">
          Comprehensive audit trail of system decisions and operator actions
        </p>
      </div>

      {/* Filters Panel */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <h2 className="text-lg font-semibold mb-4">Filters</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Event Type
            </label>
            <select
              value={filters.event_type}
              onChange={(e) => setFilters({ ...filters, event_type: e.target.value, page: 1 })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              {EVENT_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type === 'all' ? 'All Events' : type.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              User ID
            </label>
            <input
              type="text"
              value={filters.user_id}
              onChange={(e) => setFilters({ ...filters, user_id: e.target.value, page: 1 })}
              placeholder="Filter by user..."
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Operator ID
            </label>
            <input
              type="text"
              value={filters.operator_id}
              onChange={(e) => setFilters({ ...filters, operator_id: e.target.value, page: 1 })}
              placeholder="Filter by operator..."
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Start Date
            </label>
            <input
              type="date"
              value={filters.start_date}
              onChange={(e) => setFilters({ ...filters, start_date: e.target.value, page: 1 })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              End Date
            </label>
            <input
              type="date"
              value={filters.end_date}
              onChange={(e) => setFilters({ ...filters, end_date: e.target.value, page: 1 })}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={() => setShowExportModal(true)}
              className="w-full bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
            >
              Export
            </button>
          </div>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {isLoading && (
          <div className="p-8 text-center text-gray-500">Loading audit log...</div>
        )}

        {error && (
          <div className="p-8 text-center text-red-600">
            Error loading audit log: {(error as Error).message}
          </div>
        )}

        {data && data.entries.length === 0 && (
          <div className="p-8 text-center text-gray-500">
            No audit log entries found matching your filters
          </div>
        )}

        {data && data.entries.length > 0 && (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Timestamp
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Event Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      User ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Operator ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {data.entries.map((entry) => (
                    <tr key={entry.log_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {format(new Date(entry.timestamp), 'yyyy-MM-dd HH:mm:ss')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${EVENT_TYPE_COLORS[entry.event_type] || 'bg-gray-100 text-gray-800'}`}>
                          {entry.event_type.replace(/_/g, ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {entry.user_id || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {entry.operator_id || '-'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <button
                          onClick={() => setSelectedEntry(entry)}
                          className="text-indigo-600 hover:text-indigo-900"
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="bg-gray-50 px-6 py-4 flex items-center justify-between border-t border-gray-200">
              <div className="text-sm text-gray-700">
                Showing {(filters.page - 1) * filters.page_size + 1} to{' '}
                {Math.min(filters.page * filters.page_size, data.total_count)} of{' '}
                {data.total_count} results
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setFilters({ ...filters, page: filters.page - 1 })}
                  disabled={filters.page === 1}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Previous
                </button>
                <button
                  onClick={() => setFilters({ ...filters, page: filters.page + 1 })}
                  disabled={filters.page >= totalPages}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Details Modal */}
      {selectedEntry && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-semibold">Audit Log Details</h3>
                <button
                  onClick={() => setSelectedEntry(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-700">Log ID</label>
                  <p className="text-sm text-gray-900">{selectedEntry.log_id}</p>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-700">Event Type</label>
                  <p className="text-sm">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${EVENT_TYPE_COLORS[selectedEntry.event_type]}`}>
                      {selectedEntry.event_type.replace(/_/g, ' ')}
                    </span>
                  </p>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-700">Timestamp</label>
                  <p className="text-sm text-gray-900">
                    {format(new Date(selectedEntry.timestamp), 'PPpp')}
                  </p>
                </div>

                {selectedEntry.user_id && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">User ID</label>
                    <p className="text-sm text-gray-900">{selectedEntry.user_id}</p>
                  </div>
                )}

                {selectedEntry.operator_id && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">Operator ID</label>
                    <p className="text-sm text-gray-900">{selectedEntry.operator_id}</p>
                  </div>
                )}

                {selectedEntry.recommendation_id && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">Recommendation ID</label>
                    <p className="text-sm text-gray-900">{selectedEntry.recommendation_id}</p>
                  </div>
                )}

                {selectedEntry.ip_address && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">IP Address</label>
                    <p className="text-sm text-gray-900">{selectedEntry.ip_address}</p>
                  </div>
                )}

                <div>
                  <label className="text-sm font-medium text-gray-700 mb-2 block">Event Data</label>
                  <pre className="bg-gray-100 p-4 rounded text-xs overflow-x-auto">
                    {JSON.stringify(selectedEntry.event_data, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Export Modal */}
      {showExportModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-xl font-semibold mb-4">Export Audit Log</h3>
            <p className="text-sm text-gray-600 mb-4">
              Export will include all entries matching your current filters.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => handleExport('csv')}
                className="flex-1 bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
              >
                Export as CSV
              </button>
              <button
                onClick={() => handleExport('json')}
                className="flex-1 bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
              >
                Export as JSON
              </button>
            </div>
            <button
              onClick={() => setShowExportModal(false)}
              className="w-full mt-3 border border-gray-300 px-4 py-2 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
