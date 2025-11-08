/**
 * Recommendations Feed Page
 * Full page view with filtering, sorting, and comprehensive recommendation cards
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import RecommendationCard, { RecommendationData } from '../components/recommendations/RecommendationCard';

type FilterType = 'all' | 'education' | 'tools' | 'partner_offers';

const RecommendationsFeed: React.FC = () => {
  const navigate = useNavigate();
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Mock recommendations - in real app, would come from API
  const allRecommendations: RecommendationData[] = [
    {
      id: '1',
      title: 'Understanding Credit Utilization',
      description: 'Learn how credit utilization affects your credit score and strategies to optimize it.',
      type: 'article',
      icon: '📘',
    },
    {
      id: '2',
      title: 'Subscription Audit Checklist',
      description: 'Step-by-step guide to review your subscriptions and identify potential savings.',
      type: 'template',
      icon: '📋',
    },
    {
      id: '3',
      title: 'Emergency Fund Calculator',
      description: 'Calculate your personalized emergency fund target based on your expenses and income stability.',
      type: 'calculator',
      icon: '🧮',
    },
    {
      id: '4',
      title: 'High-Yield Savings Accounts',
      description: 'Compare top-rated high-yield savings accounts with up to 4.5% APY. Earn more on your emergency fund.',
      type: 'partner_offer',
      icon: '🏦',
      savingsEstimate: 'Save up to $400/year',
      eligibility: true,
    },
    {
      id: '5',
      title: 'Debt Avalanche vs. Debt Snowball',
      description: 'Compare two proven strategies for paying down credit card debt faster.',
      type: 'guide',
      icon: '📚',
    },
    {
      id: '6',
      title: 'Balance Transfer Credit Card',
      description: '0% APR balance transfer offers for 15-18 months. Save on interest while paying down your balance.',
      type: 'partner_offer',
      icon: '💳',
      savingsEstimate: 'Save up to $800 in interest',
      eligibility: true,
    },
  ];

  const getFilteredRecommendations = () => {
    let filtered = allRecommendations;

    // Apply type filter
    if (activeFilter === 'education') {
      filtered = filtered.filter((rec) => rec.type === 'article' || rec.type === 'guide');
    } else if (activeFilter === 'tools') {
      filtered = filtered.filter((rec) => rec.type === 'calculator' || rec.type === 'template');
    } else if (activeFilter === 'partner_offers') {
      filtered = filtered.filter((rec) => rec.type === 'partner_offer');
    }

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (rec) =>
          rec.title.toLowerCase().includes(query) || rec.description.toLowerCase().includes(query)
      );
    }

    return filtered;
  };

  const filteredRecommendations = getFilteredRecommendations();

  return (
    <DashboardLayout>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Personalized Recommendations</h1>
        <p className="text-gray-600">Educational resources and offers tailored to your financial persona</p>
      </div>

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
        Showing {filteredRecommendations.length} recommendation{filteredRecommendations.length !== 1 ? 's' : ''}
      </div>

      {/* Recommendations Grid */}
      {filteredRecommendations.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredRecommendations.map((rec) => (
            <RecommendationCard key={rec.id} recommendation={rec} />
          ))}
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
    </DashboardLayout>
  );
};

export default RecommendationsFeed;
