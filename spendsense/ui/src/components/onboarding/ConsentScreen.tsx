import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface ConsentScreenProps {
  onConsent?: (userId: string) => Promise<void>;
  onDecline?: () => void;
}

const ConsentScreen: React.FC<ConsentScreenProps> = ({
  onConsent,
  onDecline,
}) => {
  const { user } = useAuth();
  const userId = user?.userId || 'user_MASKED_000'; // Fallback for demo
  const navigate = useNavigate();
  const [isChecked, setIsChecked] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleConsent = async () => {
    if (!isChecked) return;

    setIsLoading(true);
    setError(null);

    try {
      if (onConsent) {
        await onConsent(userId);
      } else {
        // For end-user demo flow: Store consent locally
        // TODO: Backend needs public /api/consent endpoint for end-users (without operator auth)
        // Currently /api/consent requires admin token, which doesn't match end-user onboarding flow

        // Store user_id and consent status in localStorage
        localStorage.setItem('spendsense_user_id', userId);
        localStorage.setItem('spendsense_consent_status', 'opted_in');
        localStorage.setItem('spendsense_consent_timestamp', new Date().toISOString());
        localStorage.setItem('spendsense_consent_version', '1.0');
      }

      // Navigate to processing screen
      navigate('/onboarding/processing');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Consent error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDecline = () => {
    if (onDecline) {
      onDecline();
    } else {
      // Default: return to bank dashboard placeholder
      window.location.href = '/'; // Replace with actual bank dashboard URL
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full bg-white rounded-lg shadow-lg p-8 md:p-12">
        {/* Headline */}
        <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">
          Before we begin, here's what happens next
        </h1>

        {/* Transparent Data Usage Explanation */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            What We'll Do
          </h2>
          <ul className="space-y-3 text-gray-700">
            <li className="flex items-start">
              <span className="text-cyan-600 mr-3 mt-1">•</span>
              <span>We'll analyze your transaction data from the last 180 days</span>
            </li>
            <li className="flex items-start">
              <span className="text-cyan-600 mr-3 mt-1">•</span>
              <span>
                We'll look for patterns like subscription spending, credit utilization, and savings habits
              </span>
            </li>
            <li className="flex items-start">
              <span className="text-cyan-600 mr-3 mt-1">•</span>
              <span>Based on these patterns, we'll assign you to a financial behavior persona</span>
            </li>
            <li className="flex items-start">
              <span className="text-cyan-600 mr-3 mt-1">•</span>
              <span>You'll receive 3-5 personalized educational resources (no product sales)</span>
            </li>
          </ul>
        </div>

        {/* What We DON'T Do */}
        <div className="mb-8 bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            What We DON'T Do
          </h2>
          <ul className="space-y-3 text-gray-700">
            <li className="flex items-start">
              <span className="text-red-600 mr-3 mt-1" aria-label="no">❌</span>
              <span>Share your data with third parties without consent</span>
            </li>
            <li className="flex items-start">
              <span className="text-red-600 mr-3 mt-1" aria-label="no">❌</span>
              <span>Provide regulated financial advice</span>
            </li>
            <li className="flex items-start">
              <span className="text-red-600 mr-3 mt-1" aria-label="no">❌</span>
              <span>Judge or shame your financial choices</span>
            </li>
          </ul>
        </div>

        {/* Your Controls */}
        <div className="mb-8 bg-green-50 border border-green-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Your Controls
          </h2>
          <ul className="space-y-3 text-gray-700">
            <li className="flex items-start">
              <span className="text-green-600 mr-3 mt-1" aria-label="yes">✅</span>
              <span>Revoke consent anytime from settings</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-600 mr-3 mt-1" aria-label="yes">✅</span>
              <span>See exactly what data drives each recommendation</span>
            </li>
            <li className="flex items-start">
              <span className="text-green-600 mr-3 mt-1" aria-label="yes">✅</span>
              <span>Choose what to explore and when</span>
            </li>
          </ul>
        </div>

        {/* Consent Checkbox */}
        <div className="mb-6">
          <label className="flex items-start cursor-pointer group">
            <input
              type="checkbox"
              checked={isChecked}
              onChange={(e) => setIsChecked(e.target.checked)}
              className="mt-1 h-5 w-5 text-cyan-600 border-gray-300 rounded focus:ring-2 focus:ring-cyan-500 cursor-pointer"
              style={{ minWidth: '20px', minHeight: '20px' }} // Ensure 48px touch target with padding
              aria-label="I consent to SpendSense analyzing my transaction data"
            />
            <span className="ml-3 text-gray-900 group-hover:text-gray-700">
              I consent to SpendSense analyzing my transaction data to provide personalized financial education
            </span>
          </label>
        </div>

        {/* Disclaimer */}
        <p className="text-sm text-gray-600 mb-8 italic">
          This is educational content, not financial advice. Consult a licensed advisor for personalized guidance.
        </p>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded" role="alert">
            <p>{error}</p>
          </div>
        )}

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={handleConsent}
            disabled={!isChecked || isLoading}
            className={`
              px-8 py-4 rounded-lg font-semibold text-lg transition-all
              focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2
              min-h-[48px]
              ${
                isChecked && !isLoading
                  ? 'bg-cyan-600 hover:bg-cyan-700 text-white cursor-pointer'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }
            `}
            aria-label="I consent and continue"
          >
            {isLoading ? 'Processing...' : 'I Consent & Continue'}
          </button>

          <button
            onClick={handleDecline}
            disabled={isLoading}
            className="px-8 py-4 rounded-lg font-semibold text-lg bg-gray-200 hover:bg-gray-300 text-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 min-h-[48px]"
            aria-label="Not now, return to bank dashboard"
          >
            Not Now
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConsentScreen;
