/**
 * React Query hook for fetching signal data (Story 6.2 - Task 2)
 */

import { useQuery } from '@tanstack/react-query';
import type { UserSignals, UserSearchResult, TimeWindow } from '../types/signals';

const API_BASE = '/api/operator';

/**
 * Get auth token from localStorage
 * In production, this would use a more secure auth context
 */
function getAuthToken(): string | null {
  return localStorage.getItem('operator_token');
}

/**
 * Hook to search for users
 */
export function useUserSearch(query: string, enabled: boolean = true) {
  return useQuery<{ total: number; users: UserSearchResult[] }>({
    queryKey: ['user-search', query],
    queryFn: async () => {
      const token = getAuthToken();
      const response = await fetch(
        `${API_BASE}/users/search?q=${encodeURIComponent(query)}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication required. Please log in.');
        }
        if (response.status === 403) {
          throw new Error('Insufficient permissions. Viewer role required.');
        }
        throw new Error(`Search failed: ${response.statusText}`);
      }

      return response.json();
    },
    enabled: enabled && query.length >= 2, // Only search if query is 2+ characters
    staleTime: 30000, // 30 seconds
  });
}

/**
 * Hook to fetch signal data for a user
 */
export function useSignalData(userId: string | null, timeWindow: TimeWindow = 'both') {
  return useQuery<UserSignals>({
    queryKey: ['user-signals', userId, timeWindow],
    queryFn: async () => {
      if (!userId) {
        throw new Error('User ID is required');
      }

      const token = getAuthToken();
      const response = await fetch(
        `${API_BASE}/signals/${userId}?time_window=${timeWindow}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication required. Please log in.');
        }
        if (response.status === 403) {
          throw new Error('Insufficient permissions. Viewer role required.');
        }
        if (response.status === 404) {
          throw new Error(`User ${userId} not found`);
        }
        throw new Error(`Failed to fetch signals: ${response.statusText}`);
      }

      return response.json();
    },
    enabled: !!userId, // Only fetch if userId is provided
    staleTime: 60000, // 1 minute
  });
}

/**
 * Export signal data as CSV or JSON
 */
export async function exportSignalData(
  userId: string,
  format: 'csv' | 'json' = 'csv'
): Promise<void> {
  const token = getAuthToken();
  const response = await fetch(
    `${API_BASE}/signals/${userId}/export?format=${format}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Export failed: ${response.statusText}`);
  }

  // Trigger download
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `signals_${userId}.${format}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}
