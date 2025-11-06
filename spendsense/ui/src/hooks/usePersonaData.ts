/**
 * React Query hooks for Persona Assignment data (Story 6.3)
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import type {
  PersonaAssignmentsResponse,
  PersonaDefinition,
  PersonaChangeHistoryItem,
  PersonaOverrideRequest,
  PersonaOverrideResponse
} from '../types/personas';

const API_BASE = '/api/operator';

function getAuthToken(): string | null {
  return localStorage.getItem('operator_token');
}

/**
 * Hook to fetch persona definitions
 */
export function usePersonaDefinitions() {
  return useQuery<PersonaDefinition[]>({
    queryKey: ['persona-definitions'],
    queryFn: async () => {
      const token = getAuthToken();
      const response = await fetch(`${API_BASE}/personas/definitions`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch persona definitions: ${response.statusText}`);
      }

      return response.json();
    },
    staleTime: 300000, // 5 minutes (definitions rarely change)
  });
}

/**
 * Hook to fetch persona assignments for a user
 */
export function usePersonaAssignments(userId: string | null) {
  return useQuery<PersonaAssignmentsResponse>({
    queryKey: ['persona-assignments', userId],
    queryFn: async () => {
      if (!userId) throw new Error('User ID required');

      const token = getAuthToken();
      const response = await fetch(`${API_BASE}/personas/${userId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('No persona assignments found for this user');
        }
        throw new Error(`Failed to fetch assignments: ${response.statusText}`);
      }

      return response.json();
    },
    enabled: !!userId,
    staleTime: 60000, // 1 minute
  });
}

/**
 * Hook to fetch persona change history
 */
export function usePersonaHistory(userId: string | null, limit: number = 10) {
  return useQuery<PersonaChangeHistoryItem[]>({
    queryKey: ['persona-history', userId, limit],
    queryFn: async () => {
      if (!userId) throw new Error('User ID required');

      const token = getAuthToken();
      const response = await fetch(
        `${API_BASE}/personas/${userId}/history?limit=${limit}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch history: ${response.statusText}`);
      }

      return response.json();
    },
    enabled: !!userId,
    staleTime: 60000,
  });
}

/**
 * Hook to override persona assignment (admin only)
 */
export function usePersonaOverride(userId: string) {
  const queryClient = useQueryClient();

  return useMutation<PersonaOverrideResponse, Error, PersonaOverrideRequest>({
    mutationFn: async (request) => {
      const token = getAuthToken();
      const response = await fetch(`${API_BASE}/personas/${userId}/override`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `Override failed: ${response.statusText}`);
      }

      return response.json();
    },
    onSuccess: () => {
      // Invalidate assignments and history to refetch updated data
      queryClient.invalidateQueries({ queryKey: ['persona-assignments', userId] });
      queryClient.invalidateQueries({ queryKey: ['persona-history', userId] });
    }
  });
}
