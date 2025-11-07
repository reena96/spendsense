/**
 * React Query hooks for consent management operations.
 * Story 6.6 - Consent Management Interface
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export interface ConsentUser {
  user_id: string;
  name: string;
  consent_status: string;
  consent_timestamp: string | null;
  consent_version: string;
}

export interface ConsentHistoryEntry {
  timestamp: string;
  old_status: string | null;
  new_status: string;
  changed_by: string;
  reason: string | null;
  operator_name: string | null;
}

export interface BatchConsentRequest {
  user_ids: string[];
  consent_status: string;
  reason: string;
  consent_version?: string;
}

export interface BatchConsentResponse {
  success_count: number;
  failure_count: number;
  failed_users: Array<{ user_id: string; error: string }>;
  message: string;
}

/**
 * Hook to fetch users with consent filters
 */
export function useConsentUsers(
  consentStatus?: string | null,
  changedSince?: string | null,
  limit: number = 50,
  offset: number = 0
) {
  return useQuery({
    queryKey: ['consent-users', consentStatus, changedSince, limit, offset],
    queryFn: async () => {
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: offset.toString(),
      });

      if (consentStatus) params.append('consent_status', consentStatus);
      if (changedSince) params.append('changed_since', changedSince);

      const token = localStorage.getItem('operator_token');
      const response = await fetch(`/api/operator/consent/users?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch consent users');
      }

      return response.json();
    },
  });
}

/**
 * Hook to fetch consent history for a user
 */
export function useConsentHistory(userId: string) {
  return useQuery({
    queryKey: ['consent-history', userId],
    queryFn: async () => {
      const token = localStorage.getItem('operator_token');
      const response = await fetch(`/api/operator/consent/${userId}/history`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch consent history');
      }

      return response.json();
    },
    enabled: !!userId,
  });
}

/**
 * Hook to change individual user consent
 */
export function useChangeConsent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      userId,
      consentStatus,
      consentVersion = '1.0',
    }: {
      userId: string;
      consentStatus: string;
      consentVersion?: string;
    }) => {
      const token = localStorage.getItem('operator_token');
      const response = await fetch('/api/consent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_id: userId,
          consent_status: consentStatus,
          consent_version: consentVersion,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to change consent');
      }

      return response.json();
    },
    onSuccess: () => {
      // Invalidate consent users query to refresh list
      queryClient.invalidateQueries({ queryKey: ['consent-users'] });
    },
  });
}

/**
 * Hook for batch consent operations (admin only)
 */
export function useBatchConsent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (request: BatchConsentRequest): Promise<BatchConsentResponse> => {
      const token = localStorage.getItem('operator_token');
      const response = await fetch('/api/operator/consent/batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to perform batch consent update');
      }

      return response.json();
    },
    onSuccess: () => {
      // Invalidate consent users query to refresh list
      queryClient.invalidateQueries({ queryKey: ['consent-users'] });
    },
  });
}
