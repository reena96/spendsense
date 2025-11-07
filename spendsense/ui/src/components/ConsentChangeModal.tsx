/**
 * ConsentChangeModal - Modal for changing user consent status
 * Story 6.6 - Consent Management Interface
 */

import React, { useState } from 'react';
import { useChangeConsent } from '../hooks/useConsent';

interface ConsentChangeModalProps {
  isOpen: boolean;
  onClose: () => void;
  userId: string;
  userName: string;
  currentStatus: string;
}

export const ConsentChangeModal: React.FC<ConsentChangeModalProps> = ({
  isOpen,
  onClose,
  userId,
  userName,
  currentStatus,
}) => {
  const [newStatus, setNewStatus] = useState(currentStatus);
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');

  const changeConsentMutation = useChangeConsent();

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate reason
    if (reason.length < 20) {
      setError('Reason must be at least 20 characters');
      return;
    }

    if (newStatus === currentStatus) {
      setError('Please select a different consent status');
      return;
    }

    try {
      await changeConsentMutation.mutateAsync({
        userId,
        consentStatus: newStatus,
      });

      // Success - close modal
      onClose();
      setReason('');
    } catch (err: any) {
      setError(err.message || 'Failed to change consent status');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h2 className="text-xl font-bold mb-4">Change Consent Status</h2>

        <div className="mb-4 p-3 bg-gray-50 rounded">
          <p className="text-sm text-gray-600">User:</p>
          <p className="font-medium">{userName}</p>
          <p className="text-xs text-gray-500">{userId}</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Current Status
            </label>
            <div
              className={`px-3 py-2 rounded ${
                currentStatus === 'opted_in'
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              }`}
            >
              {currentStatus === 'opted_in' ? 'Opted In' : 'Opted Out'}
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              New Status *
            </label>
            <select
              value={newStatus}
              onChange={(e) => setNewStatus(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="opted_in">Opted In</option>
              <option value="opted_out">Opted Out</option>
            </select>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Reason for Change * (min 20 characters)
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={4}
              placeholder="Enter reason for consent change (for audit trail)..."
              required
              minLength={20}
            />
            <p className="text-xs text-gray-500 mt-1">
              {reason.length} / 20 characters minimum
            </p>
          </div>

          {newStatus !== currentStatus && (
            <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
              <p className="text-sm text-yellow-800">
                ⚠️ This will change consent from{' '}
                <strong>{currentStatus === 'opted_in' ? 'Opted In' : 'Opted Out'}</strong>
                {' '}to{' '}
                <strong>{newStatus === 'opted_in' ? 'Opted In' : 'Opted Out'}</strong>
                {newStatus === 'opted_out' && (
                  <span> and will affect recommendations for this user</span>
                )}
              </p>
            </div>
          )}

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={changeConsentMutation.isPending}
              className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {changeConsentMutation.isPending ? 'Updating...' : 'Confirm Change'}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
