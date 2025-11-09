import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface WelcomeScreenProps {
  onGetStarted?: () => void;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onGetStarted }) => {
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState(false);

  const handleGetStarted = () => {
    if (onGetStarted) {
      onGetStarted();
    } else {
      navigate('/onboarding/consent');
    }
  };

  return (
    <div className="min-h-screen bg-cyan-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full text-center">
        {/* Logo */}
        <div className="mb-8">
          <h1 className="text-5xl font-bold text-cyan-900 mb-2">SpendSense</h1>
          <div className="w-24 h-1 bg-cyan-600 mx-auto"></div>
        </div>

        {/* Headline */}
        <h2 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to SpendSense
        </h2>

        {/* Subheading */}
        <p className="text-xl text-gray-700 mb-12">
          Understand your financial behavior and get personalized education
        </p>

        {/* Value Propositions */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {/* Discover Patterns */}
          <div className="bg-white rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow">
            <div className="text-5xl mb-4" role="img" aria-label="chart">
              📊
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Discover your financial behavioral patterns
            </h3>
          </div>

          {/* Personalized Education */}
          <div className="bg-white rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow">
            <div className="text-5xl mb-4" role="img" aria-label="lightbulb">
              💡
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Receive personalized educational recommendations
            </h3>
          </div>

          {/* Your Control */}
          <div className="bg-white rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow">
            <div className="text-5xl mb-4" role="img" aria-label="lock">
              🔒
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Your data, your control – fully transparent
            </h3>
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col items-center gap-4">
          <button
            onClick={handleGetStarted}
            className="bg-cyan-600 hover:bg-cyan-700 text-white font-semibold px-8 py-4 rounded-lg text-lg transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 min-w-[200px]"
            aria-label="Get started with SpendSense"
          >
            Get Started
          </button>

          <button
            onClick={() => setShowModal(true)}
            className="text-cyan-700 hover:text-cyan-800 font-medium underline focus:outline-none focus:ring-2 focus:ring-cyan-500 rounded"
            aria-label="Learn more about how SpendSense works"
          >
            Learn more about how it works
          </button>
        </div>
      </div>

      {/* How It Works Modal */}
      {showModal && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setShowModal(false)}
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-title"
        >
          <div
            className="bg-white rounded-lg p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-start mb-6">
              <h2 id="modal-title" className="text-2xl font-bold text-gray-900">
                How SpendSense Works
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-500 hover:text-gray-700 text-2xl leading-none focus:outline-none focus:ring-2 focus:ring-cyan-500 rounded p-1"
                aria-label="Close modal"
              >
                ×
              </button>
            </div>

            <div className="space-y-6 text-left">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  What We Do
                </h3>
                <ul className="space-y-2 text-gray-700">
                  <li className="flex items-start">
                    <span className="text-cyan-600 mr-2">•</span>
                    <span>
                      Analyze your transaction patterns from the last 180 days to identify
                      behavioral signals
                    </span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-cyan-600 mr-2">•</span>
                    <span>
                      Assign you to a financial behavior persona based on your unique patterns
                    </span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-cyan-600 mr-2">•</span>
                    <span>
                      Provide personalized educational resources and tools to help you understand
                      your financial habits
                    </span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-cyan-600 mr-2">•</span>
                    <span>
                      Offer transparent explanations for every recommendation we make
                    </span>
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Your Privacy & Control
                </h3>
                <ul className="space-y-2 text-gray-700">
                  <li className="flex items-start">
                    <span className="text-green-600 mr-2">✓</span>
                    <span>You're always in control of your data</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-600 mr-2">✓</span>
                    <span>You can revoke consent anytime from settings</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-600 mr-2">✓</span>
                    <span>All processing is transparent and explainable</span>
                  </li>
                </ul>
              </div>

              <div className="pt-4">
                <button
                  onClick={() => {
                    setShowModal(false);
                    handleGetStarted();
                  }}
                  className="w-full bg-cyan-600 hover:bg-cyan-700 text-white font-semibold px-6 py-3 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2"
                >
                  Got it, let's get started!
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WelcomeScreen;
