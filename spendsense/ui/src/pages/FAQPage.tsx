/**
 * Frequently Asked Questions Page
 * Comprehensive FAQ covering common user questions
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, ChevronDown, ChevronUp } from 'lucide-react';

interface FAQItem {
  question: string;
  answer: string | React.ReactNode;
  category: string;
}

const FAQPage: React.FC = () => {
  const navigate = useNavigate();
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggleQuestion = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  const faqs: FAQItem[] = [
    // How It Works
    {
      category: 'How SpendSense Works',
      question: 'How does SpendSense analyze my financial data?',
      answer: (
        <div>
          <p className="mb-2">
            SpendSense uses behavioral signal detection to analyze your transaction patterns over the past 30-180 days.
            We look for specific indicators like credit utilization, subscription spending, savings levels, and income
            stability.
          </p>
          <p>
            Based on these signals, our algorithm matches you to one of six financial personas, each with tailored
            educational content and recommendations. For more details, see our{' '}
            <button
              onClick={() => navigate('/how-it-works')}
              className="text-cyan-600 hover:text-cyan-700 underline font-medium"
            >
              How It Works
            </button>{' '}
            page.
          </p>
        </div>
      ),
    },
    {
      category: 'How SpendSense Works',
      question: 'What are the six financial personas?',
      answer: (
        <ul className="space-y-2">
          <li><strong>High Utilization Manager:</strong> You have high credit card utilization that needs attention</li>
          <li><strong>Variable Income Budgeter:</strong> Your irregular income requires special budgeting strategies</li>
          <li><strong>Subscription Heavy Spender:</strong> You have many recurring subscriptions that could be optimized</li>
          <li><strong>Savings Builder:</strong> You have a low emergency fund and should focus on savings growth</li>
          <li><strong>Cash Flow Optimizer:</strong> You have healthy finances and can optimize for efficiency</li>
          <li><strong>Young Professional:</strong> You\'re new to credit and building your financial foundation</li>
        </ul>
      ),
    },
    {
      category: 'How SpendSense Works',
      question: 'How accurate is the persona matching?',
      answer:
        'Our persona matching algorithm uses rule-based logic that evaluates multiple financial signals simultaneously. ' +
        'If you qualify for multiple personas, we assign you to the one with the highest priority based on which ' +
        'financial challenge requires the most immediate attention. The system is transparent—you can see exactly ' +
        'which signals triggered your persona assignment.',
    },
    {
      category: 'How SpendSense Works',
      question: 'Will my persona change over time?',
      answer:
        'Yes! As your financial situation improves or changes, SpendSense will reassign you to a different persona ' +
        'if your behavioral signals shift significantly. For example, if you reduce your credit utilization from 80% ' +
        'to 30%, you might move from "High Utilization Manager" to "Cash Flow Optimizer." You\'ll receive a notification ' +
        'when your persona changes.',
    },

    // Privacy & Security
    {
      category: 'Privacy & Security',
      question: 'Is my financial data safe?',
      answer:
        'Yes. We use bank-level 256-bit encryption for all data in transit and at rest. Your data is stored with ' +
        'anonymized identifiers, and we never store your bank login credentials. We use read-only access tokens ' +
        'that you can revoke at any time through your settings.',
    },
    {
      category: 'Privacy & Security',
      question: 'Do you sell my data to third parties?',
      answer:
        'No, never. We do not sell your individual financial data to anyone. We may share aggregated, anonymized ' +
        'statistics that cannot be traced back to you (e.g., "30% of users have subscription spending over 10% of income"), ' +
        'but your personal information remains completely private.',
    },
    {
      category: 'Privacy & Security',
      question: 'Can I delete my account and data?',
      answer:
        'Yes. You can delete your account at any time from the Settings page. This will permanently remove all your ' +
        'transaction data, persona assignments, and personal information from our servers within 30 days. You can also ' +
        'export all your data before deletion.',
    },
    {
      category: 'Privacy & Security',
      question: 'How do you comply with privacy regulations?',
      answer:
        'SpendSense complies with GDPR, CCPA, and financial industry privacy standards. We maintain detailed audit logs, ' +
        'provide transparent data usage policies, and give you full control over your consent preferences. You can review ' +
        'our full privacy policy for details.',
    },

    // Account & Setup
    {
      category: 'Account & Setup',
      question: 'How do I connect my bank accounts?',
      answer:
        'During onboarding, you\'ll be prompted to securely connect your accounts through our banking partner. ' +
        'We use read-only access, which means we can view your transactions but cannot move money or make changes ' +
        'to your accounts. The connection uses the same security standards as your bank\'s mobile app.',
    },
    {
      category: 'Account & Setup',
      question: 'What if I don\'t have 30 days of transaction history?',
      answer:
        'SpendSense requires a minimum of 30 days of transaction data to accurately detect behavioral signals. ' +
        'If you don\'t have enough history when you first connect, we\'ll notify you and ask you to check back later. ' +
        'You can set up an email notification to be alerted when you have sufficient data.',
    },
    {
      category: 'Account & Setup',
      question: 'Can I use SpendSense without connecting my bank?',
      answer:
        'No, SpendSense requires read-only access to your transaction data to perform behavioral analysis. ' +
        'However, you can disconnect your accounts at any time from the Settings page if you no longer wish to use the service.',
    },
    {
      category: 'Account & Setup',
      question: 'How often is my data updated?',
      answer:
        'We refresh your transaction data daily to detect new patterns and update your behavioral signals. ' +
        'Your persona assignment is re-evaluated weekly, and you\'ll be notified if any significant changes occur.',
    },

    // Recommendations & Content
    {
      category: 'Recommendations & Content',
      question: 'Are the recommendations personalized to me?',
      answer:
        'Yes! Every recommendation is filtered based on your assigned persona. For example, someone with the ' +
        '"High Utilization Manager" persona will see content about debt paydown strategies, while a "Subscription ' +
        'Heavy Spender" will see subscription audit tools and guides.',
    },
    {
      category: 'Recommendations & Content',
      question: 'Can I mark recommendations as "not interested"?',
      answer:
        'Yes. You can dismiss individual recommendations, and our system will learn your preferences over time. ' +
        'You can also provide feedback on whether recommendations were helpful to improve future suggestions.',
    },
    {
      category: 'Recommendations & Content',
      question: 'Do you offer financial advice?',
      answer:
        'No. SpendSense is an educational platform, not a financial advisor. We provide information, tools, and ' +
        'resources to help you make informed decisions, but we do not provide personalized financial advice or ' +
        'investment recommendations. Always consult a licensed financial advisor for specific advice.',
    },
    {
      category: 'Recommendations & Content',
      question: 'What are "partner offers"?',
      answer:
        'Partner offers are products or services from trusted financial institutions that may benefit your persona. ' +
        'For example, "Savings Builder" users might see high-yield savings account offers. We are transparent about ' +
        'which recommendations come from partners and may receive a referral fee if you choose to sign up.',
    },

    // Troubleshooting
    {
      category: 'Troubleshooting',
      question: 'Why isn\'t my persona showing up?',
      answer:
        'This usually happens if you skipped the onboarding flow or if your localStorage data is corrupted. ' +
        'Try clearing your browser cache and going through the onboarding process again. If the issue persists, ' +
        'contact our support team.',
    },
    {
      category: 'Troubleshooting',
      question: 'My behavioral signals seem inaccurate. Why?',
      answer:
        'Signal detection depends on the quality and completeness of your transaction data. Common issues include: ' +
        'incomplete transaction categorization, pending transactions not yet posted, or accounts not fully synced. ' +
        'You can manually refresh your data from the Settings page or contact support if specific signals seem wrong.',
    },
    {
      category: 'Troubleshooting',
      question: 'I was assigned to the wrong persona. Can I change it?',
      answer:
        'The persona assignment is algorithmic and based on your actual behavioral signals. However, if you believe ' +
        'the assignment is incorrect, you can view the detailed match evidence on your persona card to see which ' +
        'signals triggered the assignment. If there\'s a data error, contact support. Otherwise, as your financial ' +
        'habits change, your persona will automatically update.',
    },

    // Billing & Subscription
    {
      category: 'Billing & Subscription',
      question: 'Is SpendSense free to use?',
      answer:
        'SpendSense offers a free tier with basic persona insights and recommendations. Premium features like ' +
        'advanced analytics, unlimited recommendation history, and priority support require a paid subscription. ' +
        'Check our pricing page for current plans and features.',
    },
    {
      category: 'Billing & Subscription',
      question: 'Can I cancel my subscription anytime?',
      answer:
        'Yes. You can cancel your subscription at any time from the Settings page. You\'ll retain access to premium ' +
        'features until the end of your current billing period, after which you\'ll automatically revert to the free tier.',
    },
  ];

  // Group FAQs by category
  const categories = Array.from(new Set(faqs.map((faq) => faq.category)));

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
          <h1 className="text-4xl font-bold text-gray-900">Frequently Asked Questions</h1>
          <p className="text-lg text-gray-600 mt-2">Find answers to common questions about SpendSense</p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-12">
        {categories.map((category) => (
          <section key={category} className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">{category}</h2>
            <div className="space-y-4">
              {faqs
                .filter((faq) => faq.category === category)
                .map((faq) => {
                  const globalIndex = faqs.findIndex((f) => f === faq);
                  const isOpen = openIndex === globalIndex;

                  return (
                    <div key={globalIndex} className="bg-white rounded-lg shadow-sm border border-gray-200">
                      <button
                        onClick={() => toggleQuestion(globalIndex)}
                        className="w-full flex items-center justify-between p-6 text-left hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-inset rounded-lg"
                      >
                        <span className="font-semibold text-gray-900 pr-8">{faq.question}</span>
                        {isOpen ? (
                          <ChevronUp className="w-5 h-5 text-gray-500 flex-shrink-0" />
                        ) : (
                          <ChevronDown className="w-5 h-5 text-gray-500 flex-shrink-0" />
                        )}
                      </button>
                      {isOpen && (
                        <div className="px-6 pb-6">
                          <div className="text-gray-700 leading-relaxed">{faq.answer}</div>
                        </div>
                      )}
                    </div>
                  );
                })}
            </div>
          </section>
        ))}

        {/* Still Have Questions */}
        <div className="mt-12 bg-cyan-50 border border-cyan-200 rounded-lg p-8 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Still Have Questions?</h2>
          <p className="text-gray-700 mb-6">
            Can't find what you\'re looking for? Our support team is here to help.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => navigate('/how-it-works')}
              className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 text-white font-semibold rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2"
            >
              How SpendSense Works
            </button>
            <button
              onClick={() => alert('Contact support feature coming soon')}
              className="px-6 py-3 bg-white hover:bg-gray-50 text-gray-700 font-semibold rounded-lg border border-gray-300 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2"
            >
              Contact Support
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FAQPage;
