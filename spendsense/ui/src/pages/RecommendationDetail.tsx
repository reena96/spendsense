/**
 * Recommendation Detail Page
 * Full detail view with rationale transparency, content, and feedback
 */

import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import DashboardLayout from '../components/dashboard/DashboardLayout';

const RecommendationDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(null);
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);

  // Mock recommendation data - in real app, would fetch from API
  const recommendation = {
    id: id || '1',
    title: 'Understanding Credit Utilization',
    type: 'Article',
    icon: '📘',
    content: `
# Understanding Credit Utilization

Credit utilization is one of the most important factors in your credit score, accounting for approximately 30% of your FICO score calculation.

## What is Credit Utilization?

Credit utilization is the ratio of your current credit card balances to your credit limits. For example, if you have a credit limit of $10,000 and a balance of $3,000, your utilization is 30%.

## Why It Matters

- **High utilization (>70%):** Signals to lenders that you may be overextended financially
- **Moderate utilization (30-70%):** Generally acceptable but can be improved
- **Low utilization (<30%):** Optimal range for maintaining a healthy credit score
- **Very low utilization (<10%):** Ideal, but still shows active credit use

## Strategies to Improve Your Utilization

1. **Pay down balances:** Focus on high-utilization cards first
2. **Request credit limit increases:** This improves your ratio without changing balances
3. **Make multiple payments per month:** Reduces the balance reported to credit bureaus
4. **Spread balances across cards:** Instead of maxing out one card, distribute spending

## Your Situation

Based on your current data:
- Total credit limit: $18,000
- Current balance: $5,100
- Overall utilization: 28% ✓

However, your Visa ****4523 is at 68% utilization, which may be negatively impacting your credit score. Consider focusing on paying down this specific card first.
    `,
    rationale: {
      signal: 'Your Visa ****4523 is currently at 68% utilization ($3,400 balance on $5,000 limit).',
      reason: 'High utilization on individual cards can negatively impact credit scores, even if overall utilization is acceptable.',
      data: [
        'Visa ****4523: 68% utilization',
        'Mastercard ****8921: 40% utilization',
        'Amex ****1234: 5% utilization',
      ],
    },
  };

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

  return (
    <DashboardLayout>
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/dashboard/tips')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4 focus:outline-none focus:ring-2 focus:ring-cyan-500 rounded px-2 py-1"
        >
          <span>←</span>
          <span>Back to Recommendations</span>
        </button>

        <div className="flex items-start gap-4">
          <span className="text-5xl" aria-hidden="true">{recommendation.icon}</span>
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="px-3 py-1 bg-cyan-50 text-cyan-700 text-sm font-semibold rounded-full">
                {recommendation.type}
              </span>
            </div>
            <h1 className="text-3xl font-bold text-gray-900">{recommendation.title}</h1>
          </div>
        </div>
      </div>

      {/* Why You're Seeing This */}
      <div className="bg-cyan-50 rounded-lg p-6 mb-8 border border-cyan-100">
        <h2 className="text-xl font-semibold text-gray-900 mb-3">💡 Why You're Seeing This</h2>
        <div className="space-y-3 text-gray-700">
          <p><strong>We noticed:</strong> {recommendation.rationale.signal}</p>
          <p><strong>Why this matters:</strong> {recommendation.rationale.reason}</p>
          <div>
            <p className="font-medium mb-2">Based on your data:</p>
            <ul className="space-y-1 ml-4">
              {recommendation.rationale.data.map((item, index) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="text-cyan-600">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="bg-white rounded-lg shadow-md p-8 mb-8 border border-gray-100">
        <div
          className="prose prose-cyan max-w-none"
          dangerouslySetInnerHTML={{
            __html: recommendation.content
              .split('\n')
              .map((line) => {
                if (line.startsWith('# ')) return `<h1 className="text-2xl font-bold text-gray-900 mb-4">${line.slice(2)}</h1>`;
                if (line.startsWith('## ')) return `<h2 className="text-xl font-semibold text-gray-900 mt-6 mb-3">${line.slice(3)}</h2>`;
                if (line.startsWith('- ')) return `<li className="ml-4 text-gray-700">${line.slice(2)}</li>`;
                if (line.startsWith('1. ')) return `<li className="ml-4 text-gray-700">${line.slice(3)}</li>`;
                if (line.trim()) return `<p className="text-gray-700 mb-3">${line}</p>`;
                return '';
              })
              .join(''),
          }}
        />
      </div>

      {/* Feedback Section */}
      <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Was this recommendation helpful?</h2>
        <div className="flex gap-3">
          <button
            onClick={() => handleFeedback('up')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 ${
              feedback === 'up'
                ? 'bg-green-50 border-green-300 text-green-700'
                : 'border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            <span>👍</span>
            <span>Yes, helpful</span>
          </button>
          <button
            onClick={() => handleFeedback('down')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 ${
              feedback === 'down'
                ? 'bg-red-50 border-red-300 text-red-700'
                : 'border-gray-300 text-gray-700 hover:bg-gray-50'
            }`}
          >
            <span>👎</span>
            <span>Not helpful</span>
          </button>
        </div>

        {/* Feedback Form */}
        {showFeedbackForm && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Why wasn't this helpful?
            </label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 mb-3">
              <option value="">Select a reason...</option>
              <option value="not-relevant">Not relevant to my situation</option>
              <option value="too-basic">Too basic</option>
              <option value="too-advanced">Too advanced</option>
              <option value="inaccurate">Information seems inaccurate</option>
              <option value="other">Other</option>
            </select>
            <button
              onClick={() => {
                alert('Thank you for your feedback!');
                setShowFeedbackForm(false);
              }}
              className="px-4 py-2 bg-cyan-600 text-white rounded-lg font-medium hover:bg-cyan-700 transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              Submit Feedback
            </button>
          </div>
        )}
      </div>

      {/* Ask Chat Button */}
      <div className="mt-8 text-center">
        <button
          onClick={() => navigate('/dashboard/chat?context=credit-utilization-article')}
          className="inline-flex items-center gap-2 bg-cyan-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-cyan-700 transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2"
        >
          <span>💬</span>
          <span>Ask Chat About This</span>
        </button>
      </div>
    </DashboardLayout>
  );
};

export default RecommendationDetail;
