/**
 * ConsentManagement - Main consent management page
 * Story 6.6 - Consent Management Interface
 */

import React, { useState } from 'react';
import { useConsentUsers, ConsentUser } from '../hooks/useConsent';
import { ConsentStatus } from '../components/ConsentStatus';
import { ConsentChangeModal } from '../components/ConsentChangeModal';
import { ConsentHistory } from '../components/ConsentHistory';
import { BatchConsentModal } from '../components/BatchConsentModal';

export const ConsentManagement: React.FC = () => {
  const [consentFilter, setConsentFilter] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUser, setSelectedUser] = useState<ConsentUser | null>(null);
  const [showChangeModal, setShowChangeModal] = useState(false);
  const [showHistoryFor, setShowHistoryFor] = useState<string | null>(null);
  const [showBatchModal, setShowBatchModal] = useState(false);
  const [selectedUserIds, setSelectedUserIds] = useState<string[]>([]);
  const [page, setPage] = useState(0);
  const pageSize = 20;

  const { data, isLoading, error, refetch } = useConsentUsers(
    consentFilter,
    null,
    pageSize,
    page * pageSize
  );

  const users: ConsentUser[] = data?.users || [];
  const total = data?.total || 0;
  const totalPages = Math.ceil(total / pageSize);

  // Filter users by search term (client-side)
  const filteredUsers = users.filter((user) =>
    user.user_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSelectUser = (userId: string) => {
    setSelectedUserIds((prev) =>
      prev.includes(userId)
        ? prev.filter((id) => id !== userId)
        : [...prev, userId]
    );
  };

  const handleSelectAll = () => {
    if (selectedUserIds.length === filteredUsers.length) {
      setSelectedUserIds([]);
    } else {
      setSelectedUserIds(filteredUsers.map((u) => u.user_id));
    }
  };

  const handleChangeConsent = (user: ConsentUser) => {
    setSelectedUser(user);
    setShowChangeModal(true);
  };

  const handleViewHistory = (userId: string) => {
    setShowHistoryFor(userId);
  };

  const exportToCSV = () => {
    const headers = ['user_id', 'name', 'consent_status', 'consent_timestamp', 'consent_version'];
    const rows = filteredUsers.map((user) => [
      user.user_id,
      user.name,
      user.consent_status,
      user.consent_timestamp || '',
      user.consent_version,
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map((row) => row.join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `consent_report_${new Date().toISOString()}.csv`;
    a.click();
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Consent Management</h1>
        <p className="text-gray-600 mt-2">
          Manage user consent status and view consent change history
        </p>
      </div>

      {/* Filters and Actions */}
      <div className="mb-6 bg-white p-4 rounded-lg shadow">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Search Users
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by user ID or name..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Filter by Status
            </label>
            <select
              value={consentFilter || 'all'}
              onChange={(e) => {
                setConsentFilter(e.target.value === 'all' ? null : e.target.value);
                setPage(0);
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Users</option>
              <option value="opted_in">Opted In</option>
              <option value="opted_out">Opted Out</option>
            </select>
          </div>

          <div className="flex items-end gap-2">
            <button
              onClick={exportToCSV}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              Export CSV
            </button>
            {selectedUserIds.length > 0 && (
              <button
                onClick={() => setShowBatchModal(true)}
                className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
              >
                Batch ({selectedUserIds.length})
              </button>
            )}
          </div>
        </div>

        <div className="flex justify-between items-center text-sm text-gray-600">
          <span>
            Showing {filteredUsers.length} of {total} users
            {selectedUserIds.length > 0 && ` (${selectedUserIds.length} selected)`}
          </span>
          <button
            onClick={() => refetch()}
            className="text-blue-600 hover:text-blue-800"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* User List */}
      {isLoading && (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded">
          <p className="text-red-800">Failed to load users</p>
        </div>
      )}

      {!isLoading && !error && (
        <>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left">
                    <input
                      type="checkbox"
                      checked={selectedUserIds.length === filteredUsers.length && filteredUsers.length > 0}
                      onChange={handleSelectAll}
                      className="rounded"
                    />
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Consent Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Changed
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredUsers.map((user) => (
                  <tr key={user.user_id} className="hover:bg-gray-50">
                    <td className="px-4 py-4">
                      <input
                        type="checkbox"
                        checked={selectedUserIds.includes(user.user_id)}
                        onChange={() => handleSelectUser(user.user_id)}
                        className="rounded"
                      />
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{user.name}</div>
                        <div className="text-xs text-gray-500">{user.user_id}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <ConsentStatus status={user.consent_status} />
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {user.consent_timestamp
                        ? new Date(user.consent_timestamp).toLocaleDateString()
                        : 'N/A'}
                    </td>
                    <td className="px-6 py-4 text-right text-sm font-medium space-x-2">
                      <button
                        onClick={() => handleChangeConsent(user)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        Change
                      </button>
                      <button
                        onClick={() => handleViewHistory(user.user_id)}
                        className="text-purple-600 hover:text-purple-900"
                      >
                        History
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-4 flex justify-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
                className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
              >
                Previous
              </button>
              <span className="px-4 py-2">
                Page {page + 1} of {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                disabled={page >= totalPages - 1}
                className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}

      {/* Consent History Panel */}
      {showHistoryFor && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Consent History</h2>
              <button
                onClick={() => setShowHistoryFor(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            <ConsentHistory userId={showHistoryFor} />
          </div>
        </div>
      )}

      {/* Modals */}
      {selectedUser && (
        <ConsentChangeModal
          isOpen={showChangeModal}
          onClose={() => {
            setShowChangeModal(false);
            setSelectedUser(null);
          }}
          userId={selectedUser.user_id}
          userName={selectedUser.name}
          currentStatus={selectedUser.consent_status}
        />
      )}

      <BatchConsentModal
        isOpen={showBatchModal}
        onClose={() => {
          setShowBatchModal(false);
          setSelectedUserIds([]);
        }}
        selectedUserIds={selectedUserIds}
      />
    </div>
  );
};
