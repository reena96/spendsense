import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface ProcessingLoaderProps {
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
}

const ProcessingLoader: React.FC<ProcessingLoaderProps> = ({
  onSuccess,
  onError
}) => {
  const { user } = useAuth();
  const userId = user?.userId || localStorage.getItem('spendsense_user_id') || 'user_MASKED_000';
  const navigate = useNavigate();
  const [messageIndex, setMessageIndex] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [errorType, setErrorType] = useState<'insufficient_data' | 'system_error' | null>(null);

  const messages = [
    'Analyzing your transaction patterns...',
    'Detecting behavioral signals...',
    'Identifying your financial persona...',
    'Generating personalized recommendations...'
  ];

  useEffect(() => {
    // Rotate messages every 2.5 seconds
    const messageInterval = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % messages.length);
    }, 2500);

    // Fetch profile data (triggers processing on backend)
    const fetchProfile = async () => {
      try {
        const response = await fetch(`/api/profile/${userId}`);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));

          // Check for insufficient data error
          if (response.status === 400 && errorData.detail?.includes('30 days')) {
            setErrorType('insufficient_data');
            setError('Not enough transaction history');
          } else {
            setErrorType('system_error');
            setError(errorData.detail || 'System error occurred');
          }

          if (onError) {
            onError(new Error(errorData.detail || 'Failed to fetch profile'));
          }
          return;
        }

        const apiData = await response.json();

        // Transform API response to match expected format
        // API returns: { user_id, assignments: { "30d": { assigned_persona_id, match_evidence, ... } } }
        // Frontend expects: { persona_name, signals: { ... } }
        const assignment30d = apiData.assignments?.['30d'];
        const transformedData = {
          user_id: apiData.user_id,
          persona_name: assignment30d?.assigned_persona_id || 'young_professional',
          signals: assignment30d?.match_evidence || {},
          all_qualifying_personas: assignment30d?.all_qualifying_personas || [],
          prioritization_reason: assignment30d?.prioritization_reason || ''
        };

        // Store transformed persona data
        localStorage.setItem('spendsense_persona_data', JSON.stringify(transformedData));

        if (onSuccess) {
          onSuccess(transformedData);
        }

        // Navigate to persona reveal
        setTimeout(() => {
          navigate('/onboarding/persona');
        }, 1000); // Small delay for smooth transition
      } catch (err) {
        console.error('Processing error:', err);
        setErrorType('system_error');
        setError('Connection error');

        if (onError) {
          onError(err instanceof Error ? err : new Error('Unknown error'));
        }
      }
    };

    // Start fetching after a brief delay
    const fetchTimeout = setTimeout(fetchProfile, 1000);

    return () => {
      clearInterval(messageInterval);
      clearTimeout(fetchTimeout);
    };
  }, [userId, navigate, onSuccess, onError]);

  const handleRetry = () => {
    setError(null);
    setErrorType(null);
    window.location.reload(); // Simple retry: reload the page
  };

  const handleReturn = () => {
    navigate('/');
  };

  // Insufficient Data Error Screen
  if (errorType === 'insufficient_data') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="text-6xl mb-6" role="img" aria-label="warning">
            ⚠️
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            We need at least 30 days of transaction history
          </h1>
          <p className="text-gray-700 mb-8">
            Check back soon! We'll notify you when you have enough data.
          </p>
          <div className="flex flex-col gap-4">
            <button
              onClick={() => alert('Email notification feature coming soon')}
              className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 text-white font-semibold rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2"
            >
              Notify Me When Ready
            </button>
            <button
              onClick={handleReturn}
              className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2"
            >
              Return to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  // System Error Screen
  if (errorType === 'system_error') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="text-6xl mb-6" role="img" aria-label="error">
            😞
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Something went wrong on our end
          </h1>
          <p className="text-gray-700 mb-2">We're looking into it.</p>
          {error && (
            <p className="text-sm text-gray-500 mb-8">{error}</p>
          )}
          <div className="flex flex-col gap-4">
            <button
              onClick={handleRetry}
              className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 text-white font-semibold rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2"
            >
              Try Again
            </button>
            <button
              onClick={() => alert('Contact support feature coming soon')}
              className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2"
            >
              Contact Support
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Loading Screen
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="text-center">
        {/* Animated Spinner */}
        <div className="mb-8 flex justify-center">
          <div
            className="w-16 h-16 border-4 border-cyan-200 border-t-cyan-600 rounded-full animate-spin"
            role="status"
            aria-label="Processing"
          ></div>
        </div>

        {/* Status Message */}
        <p
          className="text-xl text-gray-700 transition-opacity duration-500"
          aria-live="polite"
          aria-atomic="true"
        >
          {messages[messageIndex]}
        </p>

        {/* Expected Duration Hint */}
        <p className="text-sm text-gray-500 mt-4">This usually takes 5-10 seconds</p>
      </div>
    </div>
  );
};

export default ProcessingLoader;
