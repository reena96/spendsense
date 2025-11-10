/**
 * Recommendations Feed Page
 * Full page view with filtering, sorting, and comprehensive recommendation cards
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, Building2 } from 'lucide-react';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import { fetchRecommendations, Recommendation } from '../services/api';

type FilterType = 'all' | 'education' | 'tools' | 'partner_offers';

const RecommendationsFeed: React.FC = () => {
  const navigate = useNavigate();
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [disclaimer, setDisclaimer] = useState<string>('');

  // Load recommendations from API
  useEffect(() => {
    const loadRecommendations = async () => {
      const userId = localStorage.getItem('spendsense_user_id');
      if (!userId) {
        navigate('/onboarding/welcome');
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const data = await fetchRecommendations(userId, '30d');
        setRecommendations(data.recommendations);
        setDisclaimer(data.disclaimer);
      } catch (err) {
        console.error('Error loading recommendations:', err);
        setError(err instanceof Error ? err.message : 'Failed to load recommendations');
      } finally {
        setLoading(false);
      }
    };

    loadRecommendations();
  }, [navigate]);

  const getFilteredRecommendations = () => {
    let filtered = recommendations;

    // Apply type filter
    if (activeFilter === 'education') {
      filtered = filtered.filter((rec) => rec.item_type === 'education');
    } else if (activeFilter === 'tools') {
      filtered = filtered.filter(
        (rec) =>
          rec.item_type === 'education' &&
          (rec.content.type === 'calculator' || rec.content.type === 'template')
      );
    } else if (activeFilter === 'partner_offers') {
      filtered = filtered.filter((rec) => rec.item_type === 'partner_offer');
    }

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (rec) =>
          rec.content.title.toLowerCase().includes(query) ||
          rec.content.description.toLowerCase().includes(query)
      );
    }

    return filtered;
  };

  const filteredRecommendations = getFilteredRecommendations();

  return (
    <DashboardLayout>
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4 focus:outline-none focus:ring-2 focus:ring-cyan-500 rounded px-2 py-1"
        >
          <span>←</span>
          <span>Back to Dashboard</span>
        </button>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Personalized Recommendations</h1>
        <p className="text-gray-600">Educational resources and offers tailored to your financial persona</p>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading recommendations...</p>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-800 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium"
          >
            Retry
          </button>
        </div>
      )}

      {/* Content */}
      {!loading && !error && (
        <>
          {/* Filter Tabs and Search */}
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
            {/* Filter Tabs */}
            <div className="flex gap-2 flex-wrap">
              {[
                { id: 'all' as FilterType, label: 'All' },
                { id: 'education' as FilterType, label: 'Education' },
                { id: 'tools' as FilterType, label: 'Tools' },
                { id: 'partner_offers' as FilterType, label: 'Partner Offers' },
              ].map((filter) => (
                <button
                  key={filter.id}
                  onClick={() => setActiveFilter(filter.id)}
                  className={`
                    px-4 py-2 rounded-full text-sm font-medium transition-colors
                    focus:outline-none focus:ring-2 focus:ring-cyan-500
                    ${
                      activeFilter === filter.id
                        ? 'bg-cyan-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }
                  `}
                >
                  {filter.label}
                </button>
              ))}
            </div>

            {/* Search Bar */}
            <div className="flex-1 md:max-w-md">
              <input
                type="text"
                placeholder="Search recommendations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Results Count */}
          <div className="mb-4 text-sm text-gray-600">
            Showing {filteredRecommendations.length} recommendation
            {filteredRecommendations.length !== 1 ? 's' : ''}
          </div>

          {/* Disclaimer */}
          {disclaimer && (
            <div className="mb-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start gap-3">
              <span className="text-yellow-600 text-xl flex-shrink-0">⚠️</span>
              <p className="text-sm text-yellow-800">{disclaimer}</p>
            </div>
          )}

          {/* Recommendations Grid */}
          {filteredRecommendations.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredRecommendations.map((rec) => {
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
                        {/* Type Badge */}
                        <div className="flex items-center gap-2 mb-2">
                          <span
                            className={`px-2 py-1 text-xs font-semibold rounded-full ${
                              rec.item_type === 'partner_offer'
                                ? 'bg-purple-100 text-purple-800'
                                : 'bg-cyan-50 text-cyan-700'
                            }`}
                          >
                            {rec.content.type}
                          </span>
                        </div>

                        {/* Title */}
                        <h3 className="font-semibold text-gray-900 mb-2">{rec.content.title}</h3>

                        {/* Description */}
                        <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                          {rec.content.description}
                        </p>

                        {/* Rationale */}
                        <p className="text-sm text-gray-700 mb-2 italic">{rec.rationale}</p>

                        {/* CTA */}
                        <button className="text-cyan-600 hover:text-cyan-700 text-sm font-medium inline-flex items-center gap-1 focus:outline-none focus:underline">
                          Learn more
                          <span>→</span>
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="bg-gray-50 rounded-lg p-12 text-center">
              <p className="text-gray-600 text-lg">No recommendations found matching your search.</p>
              <button
                onClick={() => {
                  setSearchQuery('');
                  setActiveFilter('all');
                }}
                className="mt-4 text-cyan-600 hover:text-cyan-700 font-medium"
              >
                Clear filters
              </button>
            </div>
          )}
        </>
      )}
    </DashboardLayout>
  );
};

export default RecommendationsFeed;
