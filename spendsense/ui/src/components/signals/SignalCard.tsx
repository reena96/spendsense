/**
 * Signal Card Component
 * Displays summary of a behavioral signal with status and metric
 * Clickable to open detailed view
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';

export type SignalType = 'credit' | 'subscriptions' | 'savings' | 'income';
export type SignalStatus = 'good' | 'warning' | 'attention' | 'neutral';

export interface SignalCardData {
  type: SignalType;
  name: string;
  icon: string;
  metric: string;
  status: SignalStatus;
  subtitle?: string;
}

interface SignalCardProps {
  signal: SignalCardData;
  onClick?: () => void;
}

const SignalCard: React.FC<SignalCardProps> = ({ signal, onClick }) => {
  const navigate = useNavigate();

  const getStatusColor = (status: SignalStatus) => {
    switch (status) {
      case 'good':
        return 'bg-green-100 text-green-800';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800';
      case 'attention':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else {
      navigate(`/dashboard/signals/${signal.type}`);
    }
  };

  return (
    <div
      onClick={handleClick}
      className="
        bg-white rounded-lg shadow-md p-6
        hover:shadow-lg hover:scale-[1.02]
        transition-all cursor-pointer
        border border-gray-100 hover:border-cyan-200
      "
      role="button"
      tabIndex={0}
      onKeyPress={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          handleClick();
        }
      }}
      aria-label={`View details for ${signal.name}`}
    >
      {/* Icon and Status */}
      <div className="flex items-start justify-between mb-3">
        <span className="text-3xl" aria-hidden="true">{signal.icon}</span>
        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(signal.status)}`}>
          {signal.status}
        </span>
      </div>

      {/* Signal Name */}
      <h3 className="font-semibold text-gray-900 mb-2">{signal.name}</h3>

      {/* Metric */}
      <p className="text-2xl font-bold text-cyan-600 mb-2">{signal.metric}</p>

      {/* Subtitle or CTA */}
      {signal.subtitle ? (
        <p className="text-gray-600 text-sm">{signal.subtitle}</p>
      ) : (
        <p className="text-gray-600 text-sm">View details →</p>
      )}
    </div>
  );
};

export default SignalCard;
