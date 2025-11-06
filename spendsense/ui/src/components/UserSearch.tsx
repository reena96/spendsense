/**
 * User Search Component (Story 6.2 - Task 2, AC #1)
 * Allows operators to search for users by ID or name
 */

import React, { useState, useEffect } from 'react';
import { useUserSearch } from '../hooks/useSignalData';
import type { UserSearchResult } from '../types/signals';

interface UserSearchProps {
  onSelectUser: (user: UserSearchResult) => void;
}

export function UserSearch({ onSelectUser }: UserSearchProps) {
  const [query, setQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [showResults, setShowResults] = useState(true);

  // Debounce search query (500ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
      setShowResults(true);
    }, 500);

    return () => clearTimeout(timer);
  }, [query]);

  const { data, isLoading, error } = useUserSearch(debouncedQuery, debouncedQuery.length >= 2);

  const handleSelectUser = (user: UserSearchResult) => {
    onSelectUser(user);
    setQuery(''); // Clear search query
    setShowResults(false); // Hide dropdown
  };

  return (
    <div className="w-full max-w-2xl">
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by User ID or Name..."
          className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />

        {isLoading && (
          <div className="absolute right-3 top-3">
            <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full"></div>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error.message}
        </div>
      )}

      {data && data.users.length > 0 && showResults && (
        <div className="mt-2 bg-white border border-gray-200 rounded-lg shadow-lg max-h-96 overflow-y-auto">
          {data.users.map((user) => (
            <button
              key={user.user_id}
              onClick={() => handleSelectUser(user)}
              className="w-full px-4 py-3 text-left hover:bg-gray-50 border-b border-gray-100 last:border-b-0 transition-colors"
            >
              <div className="flex justify-between items-center">
                <div>
                  <div className="font-medium text-gray-900">{user.name}</div>
                  <div className="text-sm text-gray-500">{user.user_id}</div>
                </div>
                <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                  {user.persona.replace(/_/g, ' ')}
                </span>
              </div>
            </button>
          ))}
        </div>
      )}

      {data && data.users.length === 0 && debouncedQuery.length >= 2 && (
        <div className="mt-2 p-3 bg-gray-50 border border-gray-200 rounded-lg text-gray-600 text-sm">
          No users found matching "{debouncedQuery}"
        </div>
      )}
    </div>
  );
}
