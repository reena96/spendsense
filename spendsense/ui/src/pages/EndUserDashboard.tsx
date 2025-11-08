import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import DashboardTour from '../components/onboarding/DashboardTour';
import { getPersonaContent } from '../config/personaContent';

const EndUserDashboard: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const showTour = searchParams.get('tour') === 'true';
  const [personaData, setPersonaData] = useState<any>(null);

  useEffect(() => {
    // Check consent status
    const userId = localStorage.getItem('spendsense_user_id');
    if (!userId) {
      // No consent, redirect to onboarding
      navigate('/onboarding/welcome');
      return;
    }

    // Load persona data
    const stored = localStorage.getItem('spendsense_persona_data');
    if (stored) {
      setPersonaData(JSON.parse(stored));
    }
  }, [navigate]);

  if (!personaData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-700">Loading...</p>
      </div>
    );
  }

  const personaKey = personaData.persona_name || 'young_professional';
  const persona = getPersonaContent(personaKey);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-cyan-900">SpendSense</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-700">Welcome back!</span>
            <button
              id="settings-button"
              className="p-2 text-gray-600 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-cyan-500 rounded"
              aria-label="Settings"
            >
              ⚙️
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Persona Card */}
        <div id="persona-card" className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex items-center gap-4">
            <div className="text-6xl">{persona.icon}</div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{persona.name}</h2>
              <p className="text-gray-700">{persona.description}</p>
            </div>
          </div>
        </div>

        {/* Signals Section */}
        <div id="signals-section" className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Your Behavioral Signals</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {['Credit Utilization', 'Subscriptions', 'Savings', 'Income'].map((signal) => (
              <div key={signal} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer">
                <h3 className="font-semibold text-gray-900 mb-2">{signal}</h3>
                <p className="text-gray-600 text-sm">Click to view details</p>
              </div>
            ))}
          </div>
        </div>

        {/* Recommendations Section */}
        <div id="recommendations-section" className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Your Personalized Recommendations</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {persona.focusAreas.map((area, index) => (
              <div key={index} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer">
                <h3 className="font-semibold text-gray-900 mb-2">{area}</h3>
                <p className="text-gray-600 text-sm">Educational resource</p>
              </div>
            ))}
          </div>
        </div>

        {/* Chat Sidebar Placeholder */}
        <div id="chat-sidebar" className="fixed bottom-4 right-4 bg-cyan-600 text-white rounded-full p-4 shadow-lg cursor-pointer hover:bg-cyan-700 transition-colors">
          <span className="text-2xl">💬</span>
        </div>
      </main>

      {/* Dashboard Tour */}
      {showTour && <DashboardTour />}
    </div>
  );
};

export default EndUserDashboard;
