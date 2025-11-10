import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { CreditCard, Repeat, PiggyBank, TrendingUp, BookOpen, Building2 } from 'lucide-react';
import DashboardTour from '../components/onboarding/DashboardTour';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import PersonaCard from '../components/dashboard/PersonaCard';
import { TimeWindow } from '../components/dashboard/TimeWindowToggle';
import { fetchUserProfile, extractSignalData, SignalData, UserProfile, fetchRecommendations, Recommendation } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const EndUserDashboard: React.FC = () => {
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const showTour = searchParams.get('tour') === 'true';
  const [personaData, setPersonaData] = useState<any>(null);
  const [timeWindow, setTimeWindow] = useState<TimeWindow>('30d');
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [signalData, setSignalData] = useState<SignalData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [recsLoading, setRecsLoading] = useState(true);
  const [recsError, setRecsError] = useState<string | null>(null);
  const [disclaimer, setDisclaimer] = useState<string>('');

  // Load user profile data from API
  useEffect(() => {
    const loadUserProfile = async () => {
      try {
        // Check consent status
        const userId = localStorage.getItem('spendsense_user_id');
        if (!userId) {
          navigate('/onboarding/welcome');
          return;
        }

        // Load persona data from localStorage (for persona name)
        const stored = localStorage.getItem('spendsense_persona_data');
        if (stored) {
          try {
            const data = JSON.parse(stored);
            setPersonaData(data);
          } catch (error) {
            console.error('Failed to parse persona data:', error);
            localStorage.clear();
            navigate('/onboarding/welcome');
            return;
          }
        } else {
          console.warn('No persona data found, redirecting to onboarding');
          localStorage.clear();
          navigate('/onboarding/welcome');
          return;
        }

        // Fetch full profile from API
        const profile = await fetchUserProfile(userId);
        setUserProfile(profile);

        // Fetch master signals endpoint which has both 30d and 180d data
        const signalsResponse = await fetch(`/api/signals/${userId}`);
        const allSignals = await signalsResponse.json();

        // Use 30d data for initial load
        const window = '30d';
        const signals: SignalData[] = [];
        const creditData = allSignals.credit?.[window];
        const subsData = allSignals.subscriptions?.[window];
        const savingsData = allSignals.savings?.[window];
        const incomeData = allSignals.income?.[window];

        // Credit Utilization
        if (creditData) {
          const pct = Math.round((creditData.aggregate_utilization || 0) * 100);
          signals.push({
            name: 'Credit Utilization',
            metric: `${pct}%`,
            value: pct,
            status: pct > 70 ? 'attention' : pct > 50 ? 'warning' : 'good',
            path: '/dashboard/signals/credit',
          });
        }

        // Subscriptions
        if (subsData) {
          const count = subsData.subscription_count || 0;
          signals.push({
            name: 'Subscriptions',
            metric: `${count} active`,
            value: count,
            status: subsData.subscription_share > 0.15 ? 'warning' : 'neutral',
            path: '/dashboard/signals/subscriptions',
          });
        }

        // Savings
        if (savingsData) {
          const months = savingsData.emergency_fund_months || 0;
          signals.push({
            name: 'Savings',
            metric: `${months.toFixed(1)} months`,
            value: months,
            status: months < 3 ? 'attention' : months < 6 ? 'warning' : 'good',
            path: '/dashboard/signals/savings',
          });
        }

        // Income
        if (incomeData) {
          const isStable = incomeData.has_regular_income;
          signals.push({
            name: 'Income',
            metric: isStable ? 'Stable' : 'Variable',
            value: incomeData.median_pay_gap_days,
            status: isStable ? 'good' : 'attention',
            path: '/dashboard/signals/income',
          });
        }

        setSignalData(signals);
        setLoading(false);
      } catch (err) {
        console.error('Error loading user profile:', err);
        setError(err instanceof Error ? err.message : 'Failed to load profile');
        setLoading(false);
      }
    };

    loadUserProfile();
  }, [navigate]);

  // Refresh signal data when time window changes
  useEffect(() => {
    const loadSignalData = async () => {
      if (!userProfile) return;

      const userId = localStorage.getItem('spendsense_user_id');
      if (!userId) return;

      // Skip if timeWindow is 'compare' mode
      if (timeWindow === 'compare') return;

      try {
        const signals: SignalData[] = [];

        // Fetch master signals endpoint which has both 30d and 180d data
        const response = await fetch(`/api/signals/${userId}`);
        if (!response.ok) {
          throw new Error('Failed to load signals');
        }

        const allSignals = await response.json();

        // Select the appropriate time window
        const creditData = allSignals.credit?.[timeWindow];
        const subsData = allSignals.subscriptions?.[timeWindow];
        const savingsData = allSignals.savings?.[timeWindow];
        const incomeData = allSignals.income?.[timeWindow];

        // Credit Utilization
        if (creditData) {
          const pct = Math.round((creditData.aggregate_utilization || 0) * 100);
          signals.push({
            name: 'Credit Utilization',
            metric: `${pct}%`,
            value: pct,
            status: pct > 70 ? 'attention' : pct > 50 ? 'warning' : 'good',
            path: '/dashboard/signals/credit',
          });
        }

        // Subscriptions
        if (subsData) {
          const count = subsData.subscription_count || 0;
          signals.push({
            name: 'Subscriptions',
            metric: `${count} active`,
            value: count,
            status: subsData.subscription_share > 0.15 ? 'warning' : 'neutral',
            path: '/dashboard/signals/subscriptions',
          });
        }

        // Savings
        if (savingsData) {
          const months = savingsData.emergency_fund_months || 0;
          signals.push({
            name: 'Savings',
            metric: `${months.toFixed(1)} months`,
            value: months,
            status: months < 3 ? 'attention' : months < 6 ? 'warning' : 'good',
            path: '/dashboard/signals/savings',
          });
        }

        // Income
        if (incomeData) {
          const isStable = incomeData.has_regular_income;
          signals.push({
            name: 'Income',
            metric: isStable ? 'Stable' : 'Variable',
            value: incomeData.median_pay_gap_days,
            status: isStable ? 'good' : 'attention',
            path: '/dashboard/signals/income',
          });
        }

        setSignalData(signals);
      } catch (err) {
        console.error('Error loading signal data:', err);
        // Fall back to extracted data from persona assignment
        const assignment = timeWindow === '30d' ? userProfile.assignments['30d'] : userProfile.assignments['180d'];
        const signals = extractSignalData(assignment);
        setSignalData(signals);
      }
    };

    loadSignalData();
  }, [timeWindow, userProfile]);

  // Load recommendations from API
  useEffect(() => {
    const loadRecommendations = async () => {
      const userId = localStorage.getItem('spendsense_user_id');
      if (!userId) return;

      // Skip if timeWindow is 'compare' mode (not supported for recommendations API)
      if (timeWindow === 'compare') return;

      setRecsLoading(true);
      setRecsError(null);
      try {
        const data = await fetchRecommendations(userId, timeWindow);
        setRecommendations(data.recommendations.slice(0, 4)); // First 4 for dashboard
        setDisclaimer(data.disclaimer);
      } catch (err) {
        console.error('Error loading recommendations:', err);
        setRecsError(err instanceof Error ? err.message : 'Failed to load recommendations');
      } finally {
        setRecsLoading(false);
      }
    };

    loadRecommendations();
  }, [timeWindow]);

  const handleTimeWindowChange = (window: TimeWindow) => {
    setTimeWindow(window);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600 mx-auto mb-4"></div>
          <p className="text-gray-700">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="text-6xl mb-6" role="img" aria-label="error">
            ⚠️
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Error Loading Dashboard</h1>
          <p className="text-gray-700 mb-8">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 text-white font-semibold rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!personaData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-700">Loading...</p>
      </div>
    );
  }

  const personaKey = personaData.persona_name || 'young_professional';

  // Icon mapping for signals
  const signalIcons: Record<string, typeof CreditCard> = {
    'Credit Utilization': CreditCard,
    'Subscriptions': Repeat,
    'Savings': PiggyBank,
    'Income': TrendingUp,
  };

  return (
    <DashboardLayout showBottomNav={true} showFloatingChat={true} chatUnreadCount={0}>
      {/* Welcome Section */}
      {user && (
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user.name}!
          </h1>
          <p className="text-gray-600 mt-1">
            Here's your personalized financial overview
          </p>
        </div>
      )}

      {/* Persona Card */}
      <div className="mb-8">
        <PersonaCard
          personaKey={personaKey}
          onTimeWindowChange={handleTimeWindowChange}
          currentTimeWindow={timeWindow}
        />
      </div>

      {/* Signals Section */}
      <div id="signals-section" className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Your Behavioral Signals</h2>
          <span className="text-sm text-gray-600">
            {timeWindow === '30d' ? 'Last 30 Days' : 'Last 180 Days'}
          </span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {signalData.map((signal) => {
            const Icon = signalIcons[signal.name] || TrendingUp;
            return (
              <div
                key={signal.name}
                onClick={() => navigate(signal.path)}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-all cursor-pointer border border-gray-100 hover:border-cyan-200"
              >
                <div className="flex items-start justify-between mb-3">
                  <Icon className="w-8 h-8 text-cyan-600" aria-hidden="true" />
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
            );
          })}
        </div>
      </div>

      {/* Recommendations Section */}
      <div id="recommendations-section" className="mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Your Personalized Recommendations</h2>
          <button
            onClick={() => navigate('/dashboard/tips')}
            className="mt-2 sm:mt-0 text-sm text-cyan-600 hover:text-cyan-700 font-medium"
          >
            View All →
          </button>
        </div>

        {/* Loading State */}
        {recsLoading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading recommendations...</p>
          </div>
        )}

        {/* Error State */}
        {recsError && !recsLoading && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <p className="text-red-800 mb-4">{recsError}</p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium"
            >
              Retry
            </button>
          </div>
        )}

        {/* Empty State */}
        {!recsLoading && !recsError && recommendations.length === 0 && (
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
            <p className="text-gray-700 mb-2">No recommendations available yet</p>
            <p className="text-gray-600 text-sm">Check back after more transactions are processed</p>
          </div>
        )}

        {/* Recommendations Grid */}
        {!recsLoading && !recsError && recommendations.length > 0 && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recommendations.map((rec) => {
                const Icon = rec.item_type === 'education' ? BookOpen : Building2;
                return (
                  <div
                    key={rec.item_id}
                    onClick={() => navigate(`/dashboard/recommendations/${rec.item_id}`)}
                    className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-all cursor-pointer border border-gray-100 hover:border-cyan-200"
                  >
                    <div className="flex items-start gap-3">
                      <Icon className="w-8 h-8 text-cyan-600 flex-shrink-0" aria-hidden="true" />
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                            rec.item_type === 'partner_offer'
                              ? 'bg-purple-100 text-purple-800'
                              : 'bg-cyan-50 text-cyan-700'
                          }`}>
                            {rec.content.type}
                          </span>
                        </div>
                        <h3 className="font-semibold text-gray-900 mb-2">{rec.content.title}</h3>
                        <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                          {rec.content.description}
                        </p>
                        <button className="text-cyan-600 hover:text-cyan-700 text-sm font-medium">
                          Learn more →
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Disclaimer */}
            {disclaimer && (
              <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-3">
                <span className="text-yellow-600 text-xl flex-shrink-0">⚠️</span>
                <p className="text-sm text-yellow-800">{disclaimer}</p>
              </div>
            )}
          </>
        )}
      </div>

      {/* Dashboard Tour */}
      {showTour && <DashboardTour />}
    </DashboardLayout>
  );
};

export default EndUserDashboard;
