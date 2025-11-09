import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import DashboardTour from '../components/onboarding/DashboardTour';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import PersonaCard from '../components/dashboard/PersonaCard';
import { TimeWindow } from '../components/dashboard/TimeWindowToggle';

const EndUserDashboard: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const showTour = searchParams.get('tour') === 'true';
  const [personaData, setPersonaData] = useState<any>(null);
  const [timeWindow, setTimeWindow] = useState<TimeWindow>('30d');

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

  const handleTimeWindowChange = (window: TimeWindow) => {
    setTimeWindow(window);
    // In real app, this would trigger data refresh for all dashboard sections
    console.log('Time window changed to:', window, 'Current window:', timeWindow);
  };

  if (!personaData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-700">Loading...</p>
      </div>
    );
  }

  const personaKey = personaData.persona_name || 'young_professional';

  return (
    <DashboardLayout showBottomNav={true} showFloatingChat={true} chatUnreadCount={0}>
      {/* Persona Card */}
      <div className="mb-8">
        <PersonaCard personaKey={personaKey} onTimeWindowChange={handleTimeWindowChange} />
      </div>

      {/* Signals Section */}
      <div id="signals-section" className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Your Behavioral Signals</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { name: 'Credit Utilization', icon: '💳', metric: '68%', status: 'warning', path: '/dashboard/signals/credit' },
            { name: 'Subscriptions', icon: '📱', metric: '7 active', status: 'neutral', path: '/dashboard/signals/subscriptions' },
            { name: 'Savings', icon: '💰', metric: '2.3 months', status: 'attention', path: '/dashboard/signals/savings' },
            { name: 'Income', icon: '💵', metric: 'Stable', status: 'good', path: '/dashboard/signals/income' },
          ].map((signal) => (
            <div
              key={signal.name}
              onClick={() => navigate(signal.path)}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-all cursor-pointer border border-gray-100 hover:border-cyan-200"
            >
              <div className="flex items-start justify-between mb-3">
                <span className="text-3xl" aria-hidden="true">{signal.icon}</span>
                <span
                  className={`
                    px-2 py-1 rounded-full text-xs font-semibold
                    ${signal.status === 'good' ? 'bg-green-100 text-green-800' : ''}
                    ${signal.status === 'warning' ? 'bg-yellow-100 text-yellow-800' : ''}
                    ${signal.status === 'attention' ? 'bg-red-100 text-red-800' : ''}
                    ${signal.status === 'neutral' ? 'bg-gray-100 text-gray-800' : ''}
                  `}
                >
                  {signal.status}
                </span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">{signal.name}</h3>
              <p className="text-2xl font-bold text-cyan-600 mb-2">{signal.metric}</p>
              <p className="text-gray-600 text-sm">View details →</p>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendations Section */}
      <div id="recommendations-section" className="mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Your Personalized Recommendations</h2>
          <div className="mt-2 sm:mt-0 flex gap-2 text-sm">
            <button className="px-3 py-1 bg-cyan-600 text-white rounded-full font-medium">All</button>
            <button className="px-3 py-1 text-gray-600 hover:bg-gray-100 rounded-full">Education</button>
            <button className="px-3 py-1 text-gray-600 hover:bg-gray-100 rounded-full">Tools</button>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            { title: 'Understanding Credit Utilization', type: 'Article', icon: '📘' },
            { title: 'Subscription Audit Checklist', type: 'Template', icon: '📋' },
            { title: 'Emergency Fund Calculator', type: 'Tool', icon: '🧮' },
            { title: 'High-Yield Savings Accounts', type: 'Partner Offer', icon: '🏦' },
          ].map((rec, index) => (
            <div
              key={index}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-all cursor-pointer border border-gray-100 hover:border-cyan-200"
            >
              <div className="flex items-start gap-3">
                <span className="text-3xl" aria-hidden="true">{rec.icon}</span>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-2 py-1 bg-cyan-50 text-cyan-700 text-xs font-semibold rounded-full">
                      {rec.type}
                    </span>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">{rec.title}</h3>
                  <p className="text-gray-600 text-sm mb-3">
                    Personalized for your financial persona
                  </p>
                  <button className="text-cyan-600 hover:text-cyan-700 text-sm font-medium">
                    Learn more →
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Dashboard Tour */}
      {showTour && <DashboardTour />}
    </DashboardLayout>
  );
};

export default EndUserDashboard;
