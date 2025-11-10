/**
 * Persona Assignment Review Page (Story 6.3)
 * Comprehensive view of persona assignments with decision trace
 */

import { useState } from 'react';
import { usePersonaAssignments, usePersonaDefinitions } from '../hooks/usePersonaData';
import { UserSearch } from '../components/UserSearch';
import type { UserSearchResult } from '../types/signals';
import { formatDate } from '../utils/format';

export function PersonaAssignmentView() {
  const [selectedUser, setSelectedUser] = useState<UserSearchResult | null>(null);

  const { data: assignments, isLoading, error } = usePersonaAssignments(selectedUser?.user_id ?? null);
  const { data: definitions } = usePersonaDefinitions();

  const getPersonaColor = (personaId: string) => {
    const persona = definitions?.find(d => d.persona_id === personaId);
    return persona?.color || 'gray';
  };

  const renderAssignment = (assignment: any, window: string) => {
    if (!assignment) return null;

    const colorClass = `border-l-4 border-${getPersonaColor(assignment.assigned_persona_id)}-500`;

    return (
      <div className={`bg-white rounded-lg shadow p-6 ${colorClass}`}>
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-2xl font-bold text-gray-900">
              {assignment.assigned_persona_name}
            </h3>
            <p className="text-sm text-gray-500">
              {window} Window • Priority Rank: {assignment.priority_rank || 'N/A'}
            </p>
          </div>
          {assignment.is_override && (
            <span className="px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-semibold rounded-full">
              Manual Override
            </span>
          )}
        </div>

        {/* Prioritization Reason */}
        <div className="mb-4 p-3 bg-blue-50 rounded-lg">
          <div className="text-sm font-medium text-blue-900 mb-1">Prioritization Logic:</div>
          <div className="text-sm text-blue-800">{assignment.prioritization_reason}</div>
        </div>

        {/* Qualifying Personas */}
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">
            Qualifying Personas ({assignment.qualifying_personas.length})
          </h4>
          <div className="space-y-2">
            {assignment.qualifying_personas.map((qp: any) => (
              <div
                key={qp.persona_id}
                className={`p-3 rounded border ${
                  qp.persona_id === assignment.assigned_persona_id
                    ? 'bg-green-50 border-green-300'
                    : 'bg-gray-50 border-gray-200'
                }`}
              >
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-medium text-gray-900">
                      {qp.persona_name}
                      {qp.persona_id === assignment.assigned_persona_id && (
                        <span className="ml-2 text-green-600">✓ Selected</span>
                      )}
                    </div>
                    <div className="text-xs text-gray-600">Rank: {qp.priority_rank}</div>
                  </div>
                </div>

                {/* Match Evidence */}
                {Object.keys(qp.match_evidence).length > 0 && (
                  <details className="mt-2">
                    <summary className="text-xs text-gray-600 cursor-pointer hover:text-gray-900">
                      View Match Evidence
                    </summary>
                    <div className="mt-2 text-xs space-y-1">
                      {Object.entries(qp.match_evidence).map(([key, value]: [string, any]) => (
                        <div key={key} className="flex justify-between text-gray-700">
                          <span>{key}:</span>
                          <span className="font-mono">
                            {JSON.stringify(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </details>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Timestamp */}
        <div className="text-xs text-gray-500 border-t pt-2">
          Assigned: {formatDate(assignment.assigned_at)}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            👤 Persona Assignment Review
          </h1>
          <p className="mt-2 text-gray-600">
            View persona assignments with complete decision trace and match evidence
          </p>
        </div>

        {/* User Search */}
        <div className="mb-8">
          <UserSearch onSelectUser={setSelectedUser} />
        </div>

        {/* Selected User Info */}
        {selectedUser && (
          <div className="mb-6 p-4 bg-white rounded-lg shadow border border-gray-200">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">{selectedUser.name}</h2>
                <p className="text-sm text-gray-600">{selectedUser.user_id}</p>
              </div>
              <button
                onClick={() => console.log('Override modal not implemented yet')}
                className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors font-medium text-sm"
              >
                Override Persona (Admin)
              </button>
            </div>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center py-12">
            <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full"></div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="p-6 bg-red-50 border border-red-200 rounded-lg text-red-700">
            <p className="font-semibold mb-1">Error loading persona assignments</p>
            <p className="text-sm">{error.message}</p>
          </div>
        )}

        {/* Assignments Display */}
        {assignments && !isLoading && (
          <>
            {/* 30-day and 180-day Side by Side */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">30-Day Assignment</h3>
                {renderAssignment(assignments.assignments["30d"], "30-day")}
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">180-Day Assignment</h3>
                {renderAssignment(assignments.assignments["180d"], "180-day")}
              </div>
            </div>

            {/* Change History */}
            {assignments.change_history.length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  📜 Persona Change History
                </h3>
                <div className="space-y-3">
                  {assignments.change_history.map((change, idx) => (
                    <div key={idx} className="border-l-2 border-gray-300 pl-4 py-2">
                      <div className="flex items-center gap-2 text-sm">
                        <span className="font-medium text-gray-900">
                          {change.previous_persona_name}
                        </span>
                        <span className="text-gray-500">→</span>
                        <span className="font-medium text-gray-900">
                          {change.new_persona_name}
                        </span>
                        {change.is_override && (
                          <span className="px-2 py-0.5 bg-yellow-100 text-yellow-800 text-xs rounded">
                            Override
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-gray-600 mt-1">
                        {formatDate(change.changed_at)} • {change.time_window}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">{change.reason}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {/* Empty State */}
        {!selectedUser && !isLoading && !error && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Search for a User
            </h3>
            <p className="text-gray-600">
              Enter a User ID or name above to view their persona assignments
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
