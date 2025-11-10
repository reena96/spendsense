/**
 * Custom hooks for API calls with authenticated user
 */

import { useAuth } from '../contexts/AuthContext';
import { useQuery, useMutation } from '@tanstack/react-query';
import { API_BASE_URL } from '../config/api';

// Generic fetch wrapper
async function fetchApi<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// Hook to get user profile
export function useUserProfile() {
  const { user } = useAuth();

  return useQuery({
    queryKey: ['profile', user?.userId],
    queryFn: () => fetchApi(`/api/profile/${user?.userId}`),
    enabled: !!user?.userId,
  });
}

// Hook to get user recommendations
export function useRecommendations(timeWindow: string = '30d') {
  const { user } = useAuth();

  return useQuery({
    queryKey: ['recommendations', user?.userId, timeWindow],
    queryFn: () => fetchApi(`/api/recommendations/${user?.userId}?time_window=${timeWindow}`),
    enabled: !!user?.userId,
  });
}

// Hook to get behavioral signals
export function useSignals(signalType?: 'credit' | 'savings' | 'subscriptions' | 'income') {
  const { user } = useAuth();

  const url = signalType
    ? `/api/signals/${user?.userId}/${signalType}`
    : `/api/signals/${user?.userId}`;

  return useQuery({
    queryKey: ['signals', user?.userId, signalType],
    queryFn: () => fetchApi(url),
    enabled: !!user?.userId,
  });
}

// Hook to get specific signal type
export function useCreditSignal() {
  return useSignals('credit');
}

export function useSavingsSignal() {
  return useSignals('savings');
}

export function useSubscriptionsSignal() {
  return useSignals('subscriptions');
}

export function useIncomeSignal() {
  return useSignals('income');
}

// Hook to record consent
export function useRecordConsent() {
  const { user } = useAuth();

  return useMutation({
    mutationFn: async () => {
      // Store consent locally for demo
      if (user) {
        localStorage.setItem('spendsense_consent_status', 'opted_in');
        localStorage.setItem('spendsense_consent_timestamp', new Date().toISOString());
        localStorage.setItem('spendsense_consent_version', '1.0');
      }
      return Promise.resolve();
    },
  });
}

// Get current user ID (utility)
export function useUserId() {
  const { user } = useAuth();
  return user?.userId || null;
}
