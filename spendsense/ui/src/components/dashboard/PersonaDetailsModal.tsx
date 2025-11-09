/**
 * Persona Details Modal
 * Shows full persona rationale with signal citations
 */

import React from 'react';
import { getPersonaContent } from '../../config/personaContent';

interface PersonaDetailsModalProps {
  personaKey: string;
  onClose: () => void;
}

const PersonaDetailsModal: React.FC<PersonaDetailsModalProps> = ({ personaKey, onClose }) => {
  const persona = getPersonaContent(personaKey);

  // Mock signal citations - in real app, would come from API
  const signalCitations = [
    'Credit card ****4523 at 68% utilization',
    'Average monthly spending $3,245 across 7 subscriptions',
    'Savings account balance covers 2.3 months of expenses',
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" onClick={onClose}>
      <div
        className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-4xl" aria-hidden="true">{persona.icon}</span>
            <h2 className="text-2xl font-bold text-gray-900">{persona.name}</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl leading-none focus:outline-none focus:ring-2 focus:ring-cyan-500 rounded p-1"
            aria-label="Close modal"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Description */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">About This Persona</h3>
            <p className="text-gray-700">{persona.description}</p>
          </div>

          {/* Why This Persona */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Why You're Seeing This</h3>
            <p className="text-gray-700 mb-3">
              Your persona was assigned based on analysis of your financial patterns over the last 180 days.
              Here are the key signals we identified:
            </p>
            <ul className="space-y-2">
              {signalCitations.map((citation, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="text-cyan-600 mt-1">•</span>
                  <span className="text-gray-700">{citation}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Focus Areas */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Your Focus Areas</h3>
            <p className="text-gray-700 mb-3">
              Based on your persona, we recommend focusing on these areas:
            </p>
            <div className="space-y-3">
              {persona.focusAreas.map((area, index) => (
                <div key={index} className="bg-cyan-50 rounded-lg p-4 border border-cyan-100">
                  <p className="text-gray-900 font-medium">{area}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Educational Note */}
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <p className="text-sm text-gray-600">
              <strong>Note:</strong> Personas are educational tools to help you understand your financial patterns.
              They are not judgments or credit scores. You can always improve your financial habits regardless of your current persona.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4">
          <button
            onClick={onClose}
            className="w-full bg-cyan-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-cyan-700 transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default PersonaDetailsModal;
