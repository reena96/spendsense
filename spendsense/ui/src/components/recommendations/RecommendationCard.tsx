/**
 * Recommendation Card Component
 * Displays a single recommendation with type badge and CTA
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';

export type RecommendationType = 'article' | 'guide' | 'template' | 'calculator' | 'partner_offer';

export interface RecommendationData {
  id: string;
  title: string;
  description: string;
  type: RecommendationType;
  icon: string;
  savingsEstimate?: string;
  eligibility?: boolean;
}

interface RecommendationCardProps {
  recommendation: RecommendationData;
  onClick?: () => void;
}

const RecommendationCard: React.FC<RecommendationCardProps> = ({ recommendation, onClick }) => {
  const navigate = useNavigate();

  const getTypeLabel = (type: RecommendationType) => {
    switch (type) {
      case 'article':
        return 'Article';
      case 'guide':
        return 'Guide';
      case 'template':
        return 'Template';
      case 'calculator':
        return 'Calculator';
      case 'partner_offer':
        return 'Partner Offer';
      default:
        return 'Resource';
    }
  };

  const getCTAText = (type: RecommendationType) => {
    switch (type) {
      case 'article':
      case 'guide':
        return 'Read More';
      case 'template':
        return 'Download';
      case 'calculator':
        return 'Use Tool';
      case 'partner_offer':
        return 'Learn More';
      default:
        return 'View';
    }
  };

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else {
      navigate(`/dashboard/recommendations/${recommendation.id}`);
    }
  };

  return (
    <div
      onClick={handleClick}
      className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-all cursor-pointer border border-gray-100 hover:border-cyan-200"
      role="button"
      tabIndex={0}
      onKeyPress={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          handleClick();
        }
      }}
      aria-label={`View recommendation: ${recommendation.title}`}
    >
      <div className="flex items-start gap-3">
        <span className="text-3xl flex-shrink-0" aria-hidden="true">{recommendation.icon}</span>
        <div className="flex-1 min-w-0">
          {/* Type Badge */}
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <span className={`
              px-2 py-1 rounded-full text-xs font-semibold
              ${recommendation.type === 'partner_offer' ? 'bg-purple-100 text-purple-800' : 'bg-cyan-50 text-cyan-700'}
            `}>
              {getTypeLabel(recommendation.type)}
            </span>
            {recommendation.eligibility && (
              <span className="px-2 py-1 bg-green-50 text-green-700 rounded-full text-xs font-semibold">
                ✓ Eligible
              </span>
            )}
          </div>

          {/* Title */}
          <h3 className="font-semibold text-gray-900 mb-2">{recommendation.title}</h3>

          {/* Description */}
          <p className="text-gray-600 text-sm mb-3 line-clamp-2">{recommendation.description}</p>

          {/* Savings Estimate */}
          {recommendation.savingsEstimate && (
            <p className="text-sm text-green-600 font-medium mb-3">
              💰 {recommendation.savingsEstimate}
            </p>
          )}

          {/* CTA */}
          <button className="text-cyan-600 hover:text-cyan-700 text-sm font-medium inline-flex items-center gap-1 focus:outline-none focus:underline">
            {getCTAText(recommendation.type)}
            <span>→</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default RecommendationCard;
