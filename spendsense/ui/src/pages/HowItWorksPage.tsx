/**
 * How SpendSense Works Page
 * Explains the system architecture, data flow, and persona assignment process
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Database, Brain, Target, Shield, TrendingUp, Eye } from 'lucide-react';

const HowItWorksPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4 focus:outline-none focus:ring-2 focus:ring-cyan-500 rounded px-2 py-1"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back</span>
          </button>
          <h1 className="text-4xl font-bold text-gray-900">How SpendSense Works</h1>
          <p className="text-lg text-gray-600 mt-2">
            Understanding how we analyze your finances and protect your privacy
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-12">
        {/* Overview */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Overview</h2>
          <p className="text-gray-700 mb-4">
            SpendSense is a financial literacy platform that analyzes your transaction patterns to provide
            personalized education and recommendations. We use behavioral signal detection and persona matching
            to deliver insights that are relevant to your unique financial situation.
          </p>
        </section>

        {/* Step-by-Step Process */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">The Process</h2>
          <div className="space-y-8">
            {/* Step 1 */}
            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-cyan-100 rounded-full flex items-center justify-center">
                  <Database className="w-6 h-6 text-cyan-600" />
                </div>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">1. Secure Data Connection</h3>
                <p className="text-gray-700">
                  After you provide consent, SpendSense securely connects to your financial accounts through
                  bank-level encryption. Your login credentials are never stored—we use read-only access
                  tokens that can be revoked at any time.
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-cyan-100 rounded-full flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-cyan-600" />
                </div>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">2. Transaction Analysis</h3>
                <p className="text-gray-700 mb-3">
                  We analyze your transaction history (minimum 30 days) to detect behavioral signals such as:
                </p>
                <ul className="list-disc list-inside text-gray-700 space-y-1 ml-4">
                  <li>Credit utilization patterns</li>
                  <li>Recurring subscriptions and their cost</li>
                  <li>Savings balance and emergency fund coverage</li>
                  <li>Income stability and payment frequency</li>
                  <li>Cash flow trends and spending categories</li>
                </ul>
              </div>
            </div>

            {/* Step 3 */}
            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-cyan-100 rounded-full flex items-center justify-center">
                  <Brain className="w-6 h-6 text-cyan-600" />
                </div>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">3. Persona Matching</h3>
                <p className="text-gray-700 mb-3">
                  Based on your behavioral signals, our algorithm matches you to one of six financial personas:
                </p>
                <ul className="list-disc list-inside text-gray-700 space-y-1 ml-4">
                  <li><strong>High Utilization Manager</strong> - High credit card utilization needs attention</li>
                  <li><strong>Variable Income Budgeter</strong> - Irregular income requires special budgeting</li>
                  <li><strong>Subscription Heavy Spender</strong> - Many recurring subscriptions to optimize</li>
                  <li><strong>Savings Builder</strong> - Low emergency fund, focus on savings growth</li>
                  <li><strong>Cash Flow Optimizer</strong> - Healthy finances, optimize for efficiency</li>
                  <li><strong>Young Professional</strong> - New to credit, building financial foundation</li>
                </ul>
              </div>
            </div>

            {/* Step 4 */}
            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-cyan-100 rounded-full flex items-center justify-center">
                  <Target className="w-6 h-6 text-cyan-600" />
                </div>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">4. Personalized Recommendations</h3>
                <p className="text-gray-700">
                  You receive educational content, tools, and partner offers tailored to your persona. This includes
                  articles about your specific challenges, calculators for your financial goals, and actionable
                  checklists to improve your financial health.
                </p>
              </div>
            </div>

            {/* Step 5 */}
            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-cyan-100 rounded-full flex items-center justify-center">
                  <Eye className="w-6 h-6 text-cyan-600" />
                </div>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">5. Ongoing Monitoring</h3>
                <p className="text-gray-700">
                  As your financial situation evolves, SpendSense continuously analyzes your transactions
                  and may reassign your persona if your patterns change significantly. You're always in control
                  and can adjust your preferences or revoke access at any time.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Privacy & Security */}
        <section className="mb-12">
          <div className="bg-cyan-50 border border-cyan-200 rounded-lg p-6">
            <div className="flex items-start gap-3 mb-4">
              <Shield className="w-6 h-6 text-cyan-600 flex-shrink-0 mt-1" />
              <div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Privacy & Security</h3>
                <p className="text-gray-700 mb-3">
                  Your financial data is never sold or shared with third parties for marketing purposes. We use:
                </p>
                <ul className="list-disc list-inside text-gray-700 space-y-1 ml-4">
                  <li>Bank-level 256-bit encryption for all data in transit and at rest</li>
                  <li>Anonymized identifiers to protect your personal information</li>
                  <li>Aggregated analytics that cannot be traced back to individuals</li>
                  <li>Regular security audits and compliance with financial industry standards</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* What We Don't Do */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">What We Don't Do</h2>
          <div className="bg-gray-100 rounded-lg p-6">
            <ul className="space-y-3 text-gray-700">
              <li className="flex items-start gap-2">
                <span className="text-red-600 font-bold mt-1">✗</span>
                <span>We <strong>never</strong> store your bank login credentials</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-red-600 font-bold mt-1">✗</span>
                <span>We <strong>never</strong> sell your data to third parties</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-red-600 font-bold mt-1">✗</span>
                <span>We <strong>never</strong> make transactions or move money on your behalf</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-red-600 font-bold mt-1">✗</span>
                <span>We <strong>never</strong> share your individual data without your explicit consent</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-red-600 font-bold mt-1">✗</span>
                <span>We <strong>never</strong> provide financial advice—only educational content</span>
              </li>
            </ul>
          </div>
        </section>

        {/* Transparency */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Transparency Commitment</h2>
          <p className="text-gray-700 mb-4">
            We believe in complete transparency about how your data is used:
          </p>
          <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
            <li>You can view exactly which signals were detected in your transaction history</li>
            <li>You can see why you were assigned to a specific persona</li>
            <li>You can export all your data at any time</li>
            <li>You can delete your account and all associated data</li>
            <li>You receive notifications when your persona changes</li>
          </ul>
        </section>

        {/* CTA */}
        <div className="text-center bg-white rounded-lg shadow-md p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Ready to Get Started?</h2>
          <p className="text-gray-700 mb-6">
            Join thousands of users who are improving their financial literacy with personalized insights.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate('/onboarding/welcome')}
              className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 text-white font-semibold rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2"
            >
              Get Started
            </button>
            <button
              onClick={() => navigate('/faq')}
              className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2"
            >
              View FAQ
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HowItWorksPage;
