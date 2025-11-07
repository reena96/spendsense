/**
 * BatchConsentModal - Bulk consent operations (admin only)
 * Story 6.6 - Consent Management Interface
 */

import React, { useState } from 'react';
import { useBatchConsent, BatchConsentResponse } from '../hooks/useConsent';

interface BatchConsentModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedUserIds: string[];
}

export const BatchConsentModal: React.FC<BatchConsentModalProps> = ({
  isOpen,
  onClose,
  selectedUserIds,
}) => {
  const [consentStatus, setConsentStatus] = useState<string>('opted_in');
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');
  const [result, setResult] = useState<BatchConsentResponse | null>(null);

  const batchConsentMutation = useBatchConsent();

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setResult(null);

    // Validate reason
    if (reason.length < 20) {
      setError('Reason must be at least 20 characters');
      return;
    }

    try {
      const response = await batchConsentMutation.mutateAsync({
        user_ids: selectedUserIds,
        consent_status: consentStatus,
        reason,
        consent_version: '1.0',
      });

      setResult(response);

      // If fully successful, close after 2 seconds
      if (response.failure_count === 0) {
        setTimeout(() => {
          onClose();
          setReason('');
          setResult(null);
        }, 2000);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to perform batch consent update');
    }
  };

  const handleClose = () => {
    onClose();
    setReason('');
    setError('');
    setResult(null);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">Batch Consent Update</h2>

        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
          <p className="text-sm text-yellow-800 font-medium">
            ⚠️ Admin Only Operation
          </p>
          <p className="text-xs text-yellow-700 mt-1">
            This will change consent for {selectedUserIds.length} users
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Selected Users: {selectedUserIds.length}
            </label>
            <div className="max-h-32 overflow-y-auto border border-gray-300 rounded p-2 text-xs">
              {selectedUserIds.map((id) => (
                <div key={id} className="py-1">{id}</div>
              ))}
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Consent Status *
            </label>
            <select
              value={consentStatus}
              onChange={(e) => setConsentStatus(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="opted_in">Opt In</option>
              <option value="opted_out">Opt Out</option>
            </select>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Reason for Batch Change * (min 20 characters)
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={4}
              placeholder="Enter reason for batch consent change (applies to all users)..."
              required
              minLength={20}
            />
            <p className="text-xs text-gray-500 mt-1">
              {reason.length} / 20 characters minimum
            </p>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {result && (
            <div className={`mb-4 p-3 rounded ${
              result.failure_count === 0
                ? 'bg-green-50 border border-green-200'
                : 'bg-yellow-50 border border-yellow-200'
            }`}>
              <p className={`text-sm font-medium ${
                result.failure_count === 0 ? 'text-green-800' : 'text-yellow-800'
              }`}>
                {result.message}
              </p>
              <div className="mt-2 text-xs">
                <p className="text-green-700">✓ Success: {result.success_count} users</p>
                {result.failure_count > 0 && (
                  <p className="text-red-700">✗ Failed: {result.failure_count} users</p>
                )}
              </div>

              {result.failed_users.length > 0 && (
                <div className="mt-2 text-xs">
                  <p className="font-medium text-gray-700">Failed users:</p>
                  <div className="max-h-20 overflow-y-auto mt-1">
                    {result.failed_users.map((failure, idx) => (
                      <div key={idx} className="text-red-700">
                        {failure.user_id}: {failure.error}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={batchConsentMutation.isPending || !!result}
              className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {batchConsentMutation.isPending ? 'Processing...' : 'Apply to All Users'}
            </button>
            <button
              type="button"
              onClick={handleClose}
              className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300"
            >
              {result ? 'Done' : 'Cancel'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
