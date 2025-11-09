import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import WelcomeScreen from '../../components/onboarding/WelcomeScreen';
import ConsentScreen from '../../components/onboarding/ConsentScreen';
import ProcessingLoader from '../../components/onboarding/ProcessingLoader';
import PersonaReveal from '../../components/onboarding/PersonaReveal';

const OnboardingFlow: React.FC = () => {
  return (
    <Routes>
      <Route path="welcome" element={<WelcomeScreen />} />
      <Route path="consent" element={<ConsentScreen />} />
      <Route path="processing" element={<ProcessingLoader />} />
      <Route path="persona" element={<PersonaReveal />} />
      <Route path="*" element={<Navigate to="/onboarding/welcome" replace />} />
    </Routes>
  );
};

export default OnboardingFlow;
