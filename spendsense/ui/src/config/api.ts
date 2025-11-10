/**
 * API Configuration
 * Centralized API URL configuration for all environments
 */

// Get API URL from environment variable, fallback to localhost for development
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Helper to build full API URLs
export function getApiUrl(path: string): string {
  // Ensure path starts with /
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${cleanPath}`;
}
