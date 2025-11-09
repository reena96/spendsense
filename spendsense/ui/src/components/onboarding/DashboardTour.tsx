import React, { useState, useEffect } from 'react';

interface TourStep {
  title: string;
  content: string;
  target: string; // CSS selector or ID
}

const TOUR_STEPS: TourStep[] = [
  {
    title: 'Your Persona Card',
    content: 'This is your assigned persona. You can always see why you received it by clicking "View Details".',
    target: '#persona-card'
  },
  {
    title: 'Behavioral Signals',
    content: 'These cards show the behavioral patterns we detected. Click any signal to see detailed breakdowns and trends.',
    target: '#signals-section'
  },
  {
    title: 'Personalized Recommendations',
    content: 'Your personalized educational resources. Each recommendation explains exactly why we\'re showing it to you based on your specific data.',
    target: '#recommendations-section'
  },
  {
    title: 'Chat Assistant',
    content: 'Ask me anything about your financial patterns or recommendations. I\'m here to help you understand and learn.',
    target: '#chat-sidebar'
  },
  {
    title: 'Settings & Controls',
    content: 'You\'re in control. Revoke consent, adjust privacy settings, or toggle between 30-day and 180-day views anytime.',
    target: '#settings-button'
  }
];

interface DashboardTourProps {
  onComplete?: () => void;
  onSkip?: () => void;
}

const DashboardTour: React.FC<DashboardTourProps> = ({ onComplete, onSkip }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    // Check if tour should be shown
    const tourCompleted = localStorage.getItem('spendsense_tour_completed');
    if (tourCompleted) {
      setIsVisible(false);
    }
  }, []);

  const handleNext = () => {
    if (currentStep < TOUR_STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleFinish();
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSkip = () => {
    localStorage.setItem('spendsense_tour_completed', 'skipped');
    setIsVisible(false);
    if (onSkip) onSkip();
  };

  const handleFinish = () => {
    localStorage.setItem('spendsense_tour_completed', 'completed');
    setIsVisible(false);
    if (onComplete) onComplete();
  };

  if (!isVisible) {
    return null;
  }

  const step = TOUR_STEPS[currentStep];

  return (
    <>
      {/* Dimmed Overlay */}
      <div className="fixed inset-0 bg-black bg-opacity-60 z-40" />

      {/* Tooltip */}
      <div className="fixed bottom-8 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-md px-4">
        <div className="bg-white rounded-lg shadow-2xl p-6">
          {/* Progress Indicator */}
          <div className="flex justify-center mb-4">
            {TOUR_STEPS.map((_, index) => (
              <div
                key={index}
                className={`h-2 w-2 rounded-full mx-1 ${
                  index === currentStep ? 'bg-cyan-600' : 'bg-gray-300'
                }`}
              />
            ))}
          </div>

          {/* Step Content */}
          <div className="mb-6">
            <h3 className="text-xl font-bold text-gray-900 mb-2">{step.title}</h3>
            <p className="text-gray-700">{step.content}</p>
            <p className="text-sm text-gray-500 mt-2">
              Step {currentStep + 1} of {TOUR_STEPS.length}
            </p>
          </div>

          {/* Navigation Buttons */}
          <div className="flex justify-between items-center">
            <button
              onClick={handleSkip}
              className="text-gray-600 hover:text-gray-800 font-medium focus:outline-none focus:ring-2 focus:ring-gray-400 rounded px-2 py-1"
            >
              Skip Tour
            </button>

            <div className="flex gap-2">
              {currentStep > 0 && (
                <button
                  onClick={handleBack}
                  className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2"
                >
                  Back
                </button>
              )}

              <button
                onClick={handleNext}
                className="px-6 py-2 bg-cyan-600 hover:bg-cyan-700 text-white font-semibold rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2"
              >
                {currentStep < TOUR_STEPS.length - 1 ? 'Next' : 'Finish Tour'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default DashboardTour;
