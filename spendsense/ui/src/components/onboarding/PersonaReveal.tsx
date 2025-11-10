import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import * as LucideIcons from 'lucide-react';
import { getPersonaContent, PERSONA_CONTENT } from '../../config/personaContent';

interface PersonaRevealProps {
  personaData?: any;
}

const PersonaReveal: React.FC<PersonaRevealProps> = ({ personaData }) => {
  const navigate = useNavigate();
  const [showAllPersonas, setShowAllPersonas] = useState(false);
  const [data, setData] = useState(personaData);

  useEffect(() => {
    if (!data) {
      // Try to load from localStorage
      const stored = localStorage.getItem('spendsense_persona_data');
      if (stored) {
        setData(JSON.parse(stored));
      }
    }
  }, [data]);

  if (!data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center">
          <p className="text-gray-700">Loading persona data...</p>
        </div>
      </div>
    );
  }

  const personaKey = data.persona_name || data.persona?.name || 'young_professional';
  const persona = getPersonaContent(personaKey);
  const signals = data.signals || data.behavioral_signals || [];

  // Dynamically get the Lucide icon component
  const IconComponent = LucideIcons[persona.icon as keyof typeof LucideIcons] as React.FC<{ className?: string }>;

  // Format signal citations
  const getSignalCitations = () => {
    const citations = [];

    if (signals.credit_utilization) {
      const util = signals.credit_utilization;
      citations.push(
        `Your credit card ending in ****${util.last4 || '0000'} is at ${Math.round(util.utilization_rate * 100)}% utilization`
      );
    }

    if (signals.subscriptions) {
      const subs = signals.subscriptions;
      citations.push(
        `You have ${subs.count || 0} active subscriptions totaling $${Math.round(subs.monthly_cost || 0)}/month`
      );
    }

    if (signals.savings) {
      const savings = signals.savings;
      citations.push(
        `You have $${Math.round(savings.balance || 0)} in savings (${savings.months_coverage || 0} months of coverage)`
      );
    }

    return citations.length > 0 ? citations : [
      'Analyzing your transaction patterns',
      'Building your financial profile',
      'Identifying key behavioral signals'
    ];
  };

  const handleExploreDashboard = () => {
    navigate('/dashboard?tour=true');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-50 to-blue-50 flex items-center justify-center p-4">
      <div className="max-w-3xl w-full bg-white rounded-2xl shadow-xl p-8 md:p-12">
        {/* Persona Icon */}
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4" role="img" aria-label={persona.name}>
            {IconComponent && <IconComponent className="w-32 h-32 text-cyan-600" />}
          </div>

          {/* Headline */}
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Your Financial Persona: {persona.name}
          </h1>

          {/* Description */}
          <p className="text-xl text-gray-700 max-w-2xl mx-auto">
            {persona.description}
          </p>
        </div>

        {/* Why This Persona */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Based on your transaction patterns, we noticed:
          </h2>
          <ul className="space-y-3">
            {getSignalCitations().map((citation, index) => (
              <li key={index} className="flex items-start bg-cyan-50 rounded-lg p-4">
                <span className="text-cyan-600 mr-3 mt-1">•</span>
                <span className="text-gray-700">{citation}</span>
              </li>
            ))}
          </ul>
          <p className="mt-4 text-gray-600 italic">
            These patterns suggest you'd benefit most from {persona.name.toLowerCase()} education.
          </p>
        </div>

        {/* What This Means */}
        <div className="mb-10">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            You'll receive personalized recommendations for:
          </h2>
          <ul className="space-y-3">
            {persona.focusAreas.map((area, index) => (
              <li key={index} className="flex items-start">
                <span className="text-green-600 mr-3 mt-1">✓</span>
                <span className="text-gray-700">{area}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col items-center gap-4">
          <button
            onClick={handleExploreDashboard}
            className="w-full max-w-md bg-cyan-600 hover:bg-cyan-700 text-white font-bold px-8 py-4 rounded-lg text-lg transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2"
          >
            Explore My Dashboard
          </button>

          <button
            onClick={() => setShowAllPersonas(true)}
            className="text-cyan-700 hover:text-cyan-800 font-medium underline focus:outline-none focus:ring-2 focus:ring-cyan-500 rounded px-2"
          >
            Learn about other personas
          </button>
        </div>
      </div>

      {/* All Personas Modal */}
      {showAllPersonas && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setShowAllPersonas(false)}
        >
          <div
            className="bg-white rounded-lg p-8 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-start mb-6">
              <h2 className="text-3xl font-bold text-gray-900">
                All Financial Personas
              </h2>
              <button
                onClick={() => setShowAllPersonas(false)}
                className="text-gray-500 hover:text-gray-700 text-3xl leading-none focus:outline-none focus:ring-2 focus:ring-cyan-500 rounded p-1"
              >
                ×
              </button>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {Object.entries(PERSONA_CONTENT).map(([key, content]) => {
                const PersonaIcon = LucideIcons[content.icon as keyof typeof LucideIcons] as React.FC<{ className?: string }>;
                return (
                  <div
                    key={key}
                    className={`border-2 rounded-lg p-6 ${
                      key === personaKey ? 'border-cyan-600 bg-cyan-50' : 'border-gray-200'
                    }`}
                  >
                    <div className="mb-3">
                      {PersonaIcon && <PersonaIcon className="w-12 h-12 text-cyan-600" />}
                    </div>
                    <h3 className="text-xl font-bold text-gray-900 mb-2">
                      {content.name}
                      {key === personaKey && (
                        <span className="ml-2 text-sm font-normal text-cyan-600">(You)</span>
                      )}
                    </h3>
                    <p className="text-gray-700 text-sm">{content.description}</p>
                  </div>
                );
              })}
            </div>

            <div className="mt-6 text-center">
              <button
                onClick={() => setShowAllPersonas(false)}
                className="bg-cyan-600 hover:bg-cyan-700 text-white font-semibold px-6 py-3 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PersonaReveal;
