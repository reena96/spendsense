/**
 * Recommendation Detail Page
 * Full detail view with rationale transparency, content, and feedback
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import { ExternalLink } from 'lucide-react';

// Map internal content URLs to real external educational articles
const CONTENT_URL_MAP: Record<string, string> = {
  '/content/budgeting-basics': 'https://www.consumerfinance.gov/an-essential-guide-to-building-an-emergency-fund/',
  '/content/credit-101': 'https://www.consumerfinance.gov/consumer-tools/credit-reports-and-scores/',
  '/content/emergency-fund': 'https://www.consumerfinance.gov/an-essential-guide-to-building-an-emergency-fund/',
  '/content/debt-snowball': 'https://www.consumerfinance.gov/paying-for-college/repay-student-debt/',
  '/content/savings-strategies': 'https://www.consumerfinance.gov/consumer-tools/money-as-you-grow/',
  '/content/subscription-management': 'https://www.consumerfinance.gov/consumer-tools/bank-accounts/',
  '/content/income-optimization': 'https://www.consumerfinance.gov/consumer-tools/money-as-you-grow/',
  '/content/credit-utilization': 'https://www.consumerfinance.gov/ask-cfpb/what-is-a-credit-utilization-rate-en-1997/',
};

interface RecommendationData {
  item_type: 'education' | 'partner_offer';
  item_id: string;
  content: {
    id: string;
    type: string;
    title: string;
    description: string;
    category?: string;
    priority: number;
    content_url?: string;
    offer_url?: string;
    key_benefits?: string[];
    provider?: string;
    difficulty?: string;
    time_commitment?: string;
    estimated_impact?: string;
  };
  rationale: string;
  persona_match_reason: string;
  signal_citations: string[];
}

const RecommendationDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [recommendation, setRecommendation] = useState<RecommendationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(null);
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);

  useEffect(() => {
    const fetchRecommendation = async () => {
      const userId = user?.userId || localStorage.getItem('spendsense_user_id');
      if (!userId || !id) {
        setError('Missing user or recommendation ID');
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(`/api/recommendations/${userId}?time_window=30d`);
        if (!response.ok) {
          throw new Error('Failed to load recommendations');
        }

        const data = await response.json();
        const rec = data.recommendations.find((r: RecommendationData) => r.item_id === id);

        if (!rec) {
          throw new Error('Recommendation not found');
        }

        setRecommendation(rec);
      } catch (err) {
        console.error('Error loading recommendation:', err);
        setError(err instanceof Error ? err.message : 'Failed to load recommendation');
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendation();
  }, [id, user]);

  const handleFeedback = (type: 'up' | 'down') => {
    setFeedback(type);
    if (type === 'down') {
      setShowFeedbackForm(true);
    } else {
      setTimeout(() => {
        alert('Thanks for your feedback!');
      }, 300);
    }
  };

  const getExternalUrl = (internalUrl: string): string => {
    return CONTENT_URL_MAP[internalUrl] || internalUrl;
  };

  const handleExternalLink = (url: string) => {
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="max-w-4xl mx-auto py-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading recommendation...</p>
        </div>
      </DashboardLayout>
    );
  }

  if (error || !recommendation) {
    return (
      <DashboardLayout>
        <div className="max-w-4xl mx-auto py-12">
          <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
            <h2 className="text-2xl font-bold text-red-900 mb-4">Error</h2>
            <p className="text-red-700 mb-6">{error || 'Recommendation not found'}</p>
            <button
              onClick={() => navigate('/dashboard/tips')}
              className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg"
            >
              Back to Recommendations
            </button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  const isEducation = recommendation.item_type === 'education';
  const externalUrl = isEducation && recommendation.content.content_url
    ? getExternalUrl(recommendation.content.content_url)
    : recommendation.content.offer_url;

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/dashboard/tips')}
            className="inline-flex items-center gap-2 text-gray-600 hover:text-cyan-600 mb-6 transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 rounded-lg px-3 py-2 hover:bg-gray-50"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <span className="font-medium">Back to Recommendations</span>
          </button>

          <div className="flex items-start gap-6">
            <div className="flex-shrink-0">
              <div className="w-20 h-20 bg-gradient-to-br from-cyan-50 to-cyan-100 rounded-2xl flex items-center justify-center">
                <span className="text-5xl" aria-hidden="true">{isEducation ? '📘' : '💼'}</span>
              </div>
            </div>
            <div className="flex-1 pt-2">
              <div className="flex items-center gap-3 mb-3">
                <span className={`px-4 py-1.5 text-white text-sm font-semibold rounded-full shadow-sm ${
                  isEducation ? 'bg-cyan-600' : 'bg-purple-600'
                }`}>
                  {recommendation.content.type}
                </span>
                {recommendation.content.difficulty && (
                  <span className="px-3 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-full">
                    {recommendation.content.difficulty}
                  </span>
                )}
                {recommendation.content.estimated_impact && (
                  <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                    {recommendation.content.estimated_impact} impact
                  </span>
                )}
              </div>
              <h1 className="text-4xl font-bold text-gray-900 leading-tight">{recommendation.content.title}</h1>
            </div>
          </div>
        </div>

        {/* External Link Button */}
        {externalUrl && (
          <div className="mb-8">
            <button
              onClick={() => handleExternalLink(externalUrl)}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2"
            >
              <ExternalLink className="w-5 h-5" />
              <span>{isEducation ? 'Read Full Article' : 'View Offer'}</span>
            </button>
            {!isEducation && recommendation.content.provider && (
              <p className="text-sm text-gray-600 mt-2">
                Provided by {recommendation.content.provider}
              </p>
            )}
          </div>
        )}

        {/* Why You're Seeing This */}
        <div className="bg-gradient-to-br from-cyan-50 to-blue-50 rounded-xl p-8 mb-8 border border-cyan-200 shadow-sm">
          <div className="flex items-start gap-3 mb-5">
            <div className="flex-shrink-0 w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-sm">
              <span className="text-2xl">💡</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mt-1">Why You're Seeing This</h2>
          </div>
          <div className="space-y-4 text-gray-700">
            <div className="bg-white/70 rounded-lg p-4 backdrop-blur-sm">
              <p className="font-semibold text-gray-900 mb-1">Personalized for you:</p>
              <p className="text-gray-700">{recommendation.persona_match_reason}</p>
            </div>
            <div className="bg-white/70 rounded-lg p-4 backdrop-blur-sm">
              <p className="font-semibold text-gray-900 mb-1">Why this matters:</p>
              <p className="text-gray-700">{recommendation.rationale}</p>
            </div>
            {recommendation.signal_citations && recommendation.signal_citations.length > 0 && (
              <div className="bg-white/70 rounded-lg p-4 backdrop-blur-sm">
                <p className="font-semibold text-gray-900 mb-3">Based on your data:</p>
                <ul className="space-y-2">
                  {recommendation.signal_citations.map((citation, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <span className="flex-shrink-0 w-6 h-6 bg-cyan-600 text-white rounded-full flex items-center justify-center text-xs font-semibold mt-0.5">
                        {index + 1}
                      </span>
                      <span className="text-gray-700 pt-0.5">{citation}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8 border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Overview</h2>
          <div className="prose prose-lg max-w-none">
            <p className="text-gray-700 leading-relaxed">{recommendation.content.description}</p>
          </div>

          {/* Key Benefits for Partner Offers */}
          {!isEducation && recommendation.content.key_benefits && recommendation.content.key_benefits.length > 0 && (
            <div className="mt-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Key Benefits</h3>
              <ul className="space-y-2">
                {recommendation.content.key_benefits.map((benefit, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <span className="text-cyan-600 text-xl mt-0.5">✓</span>
                    <span className="text-gray-700">{benefit}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Time Commitment */}
          {recommendation.content.time_commitment && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">
                <span className="font-semibold text-gray-900">Time Commitment:</span> {recommendation.content.time_commitment}
              </p>
            </div>
          )}
        </div>

        {/* Feedback Section */}
        <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Was this helpful?</h2>
          <div className="flex gap-4 mb-6">
            <button
              onClick={() => handleFeedback('up')}
              className={`flex-1 px-6 py-3 rounded-lg font-medium transition-all focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 ${
                feedback === 'up'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-green-50 hover:text-green-700'
              }`}
            >
              👍 Yes, helpful
            </button>
            <button
              onClick={() => handleFeedback('down')}
              className={`flex-1 px-6 py-3 rounded-lg font-medium transition-all focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 ${
                feedback === 'down'
                  ? 'bg-red-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-red-50 hover:text-red-700'
              }`}
            >
              👎 Not helpful
            </button>
          </div>

          {showFeedbackForm && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <p className="text-gray-700 mb-3">Help us improve! What would make this more useful?</p>
              <textarea
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
                rows={3}
                placeholder="Your feedback (optional)"
              />
              <button className="mt-3 px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white font-medium rounded-lg">
                Submit Feedback
              </button>
            </div>
          )}

          <p className="text-sm text-gray-600 mt-4 italic border-t border-gray-200 pt-4">
            This is educational content, not financial advice. Consult a licensed financial advisor for personalized guidance.
          </p>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default RecommendationDetail;
