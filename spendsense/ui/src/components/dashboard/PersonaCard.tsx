/**
 * Persona Card Component
 * Displays user's financial persona with primary metric and view details option
 */

import React, { useState } from 'react';
import * as LucideIcons from 'lucide-react';
import { getPersonaContent } from '../../config/personaContent';
import TimeWindowToggle, { TimeWindow } from './TimeWindowToggle';
import PersonaDetailsModal from './PersonaDetailsModal';

interface PersonaCardProps {
  personaKey: string;
  onTimeWindowChange?: (window: TimeWindow) => void;
  currentTimeWindow?: TimeWindow;
}

const PersonaCard: React.FC<PersonaCardProps> = ({ personaKey, onTimeWindowChange, currentTimeWindow }) => {
  const [showModal, setShowModal] = useState(false);
  const [selectedWindow, setSelectedWindow] = useState<TimeWindow>(currentTimeWindow || '30d');
  const persona = getPersonaContent(personaKey);

  const handleTimeWindowChange = (window: TimeWindow) => {
    setSelectedWindow(window);
    if (onTimeWindowChange) {
      onTimeWindowChange(window);
    }
  };

  // Mock primary metric - in real app, would come from API
  const getPrimaryMetric = () => {
    switch (personaKey) {
      case 'high_utilization':
        return { label: 'Credit Utilization', value: '68%', status: 'warning' };
      case 'subscription_heavy':
        return { label: 'Active Subscriptions', value: '12', status: 'warning' };
      case 'saver':
        return { label: 'Savings Coverage', value: '8 months', status: 'good' };
      case 'irregular_income':
        return { label: 'Income Variability', value: 'High', status: 'attention' };
      case 'young_professional':
        return { label: 'Financial Health', value: 'Developing', status: 'neutral' };
      case 'building_credit':
        return { label: 'Credit Score Trend', value: '↑ Improving', status: 'good' };
      default:
        return { label: 'Status', value: 'Active', status: 'neutral' };
    }
  };

  const metric = getPrimaryMetric();

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'attention':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  // Dynamically get the Lucide icon component
  const IconComponent = LucideIcons[persona.icon as keyof typeof LucideIcons] as React.FC<{ className?: string }>;

  return (
    <>
      <div id="persona-card" className="bg-white rounded-lg shadow-md p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          {/* Persona Info */}
          <div className="flex items-center gap-4">
            <div className="flex-shrink-0" aria-hidden="true">
              {IconComponent && <IconComponent className="w-16 h-16 text-cyan-600" />}
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900">{persona.name}</h2>
              <p className="text-gray-700 mt-1">{persona.description}</p>

              {/* Primary Metric */}
              <div className="mt-3 inline-flex items-center gap-2">
                <span className="text-sm text-gray-600">{metric.label}:</span>
                <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${getStatusColor(metric.status)}`}>
                  {metric.value}
                </span>
              </div>

              {/* View Details Button */}
              <button
                onClick={() => setShowModal(true)}
                className="mt-3 block text-cyan-600 hover:text-cyan-700 text-sm font-medium focus:outline-none focus:underline"
              >
                View Full Details →
              </button>
            </div>
          </div>

          {/* Time Window Toggle */}
          <div className="flex flex-col items-start lg:items-end gap-2">
            <label className="text-sm font-medium text-gray-700">Time Period</label>
            <TimeWindowToggle onChange={handleTimeWindowChange} selected={selectedWindow} />
          </div>
        </div>
      </div>

      {/* Persona Details Modal */}
      {showModal && (
        <PersonaDetailsModal
          personaKey={personaKey}
          onClose={() => setShowModal(false)}
        />
      )}
    </>
  );
};

export default PersonaCard;
