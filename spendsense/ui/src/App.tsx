/**
 * SpendSense UI - Main App Component
 * React 18 + TypeScript + React Router + React Query
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Link, useNavigate, Navigate, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './contexts/AuthContext';
import { SignalDashboard } from './pages/SignalDashboard';
import AuditLog from './pages/AuditLog';
import ComplianceMetrics from './pages/ComplianceMetrics';
import { ConsentManagement } from './pages/ConsentManagement';
import Login from './pages/Login';
import UserLogin from './pages/UserLogin';
import OnboardingFlow from './pages/onboarding/OnboardingFlow';
import EndUserDashboard from './pages/EndUserDashboard';
import CreditUtilizationDetail from './pages/signals/CreditUtilizationDetail';
import SubscriptionsDetail from './pages/signals/SubscriptionsDetail';
import SavingsDetail from './pages/signals/SavingsDetail';
import IncomeDetail from './pages/signals/IncomeDetail';
import RecommendationsFeed from './pages/RecommendationsFeed';
import RecommendationDetail from './pages/RecommendationDetail';
import ChatInterface from './pages/ChatInterface';
import SettingsPage from './pages/SettingsPage';
import FAQPage from './pages/FAQPage';
import PrivacyPolicyPage from './pages/PrivacyPolicyPage';
import TermsOfServicePage from './pages/TermsOfServicePage';
import HowItWorksPage from './pages/HowItWorksPage';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Protected Route Component - redirects to login if not authenticated
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const isAuthenticated = !!localStorage.getItem('operator_token');

  if (!isAuthenticated) {
    // Redirect to login, but save the attempted URL
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}

function Navigation() {
  const navigate = useNavigate();
  const isAuthenticated = !!localStorage.getItem('operator_token');
  const operatorRole = localStorage.getItem('operator_role');

  const handleLogout = () => {
    localStorage.removeItem('operator_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('operator_id');
    localStorage.removeItem('operator_role');
    navigate('/login');
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold text-gray-900">
              SpendSense
            </Link>
            <div className="ml-10 flex items-baseline space-x-4">
              <Link
                to="/signals"
                className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-100 transition-colors"
              >
                Signal Dashboard
              </Link>
              <Link
                to="/audit"
                className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-100 transition-colors"
              >
                Audit Log
              </Link>
              <Link
                to="/compliance"
                className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-100 transition-colors"
              >
                Compliance Metrics
              </Link>
              <Link
                to="/consent"
                className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-100 transition-colors"
              >
                Consent Management
              </Link>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">
              Role: <span className="font-medium">{operatorRole}</span>
            </span>
            <button
              onClick={handleLogout}
              className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium hover:bg-gray-100 transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <div className="min-h-screen bg-gray-50">
            <Navigation />
            {/* Routes */}
            <Routes>
              {/* User Authentication */}
              <Route path="/user-login" element={<UserLogin />} />

              {/* End-User Routes (auth required) */}
              <Route path="/onboarding/*" element={<OnboardingFlow />} />
              <Route path="/dashboard" element={<EndUserDashboard />} />
              <Route path="/dashboard/signals/credit" element={<CreditUtilizationDetail />} />
              <Route path="/dashboard/signals/subscriptions" element={<SubscriptionsDetail />} />
              <Route path="/dashboard/signals/savings" element={<SavingsDetail />} />
              <Route path="/dashboard/signals/income" element={<IncomeDetail />} />
              <Route path="/dashboard/tips" element={<RecommendationsFeed />} />
              <Route path="/dashboard/recommendations/:id" element={<RecommendationDetail />} />
              <Route path="/dashboard/chat" element={<ChatInterface />} />
              <Route path="/dashboard/settings" element={<SettingsPage />} />
              <Route path="/faq" element={<FAQPage />} />
              <Route path="/privacy-policy" element={<PrivacyPolicyPage />} />
              <Route path="/terms-of-service" element={<TermsOfServicePage />} />
              <Route path="/how-it-works" element={<HowItWorksPage />} />

              {/* Operator Routes (auth required) */}
              <Route path="/login" element={<Login />} />
              <Route path="/operator" element={<ProtectedRoute><HomePage /></ProtectedRoute>} />
              <Route path="/signals" element={<ProtectedRoute><SignalDashboard /></ProtectedRoute>} />
              <Route path="/audit" element={<ProtectedRoute><AuditLog /></ProtectedRoute>} />
              <Route path="/compliance" element={<ProtectedRoute><ComplianceMetrics /></ProtectedRoute>} />
              <Route path="/consent" element={<ProtectedRoute><ConsentManagement /></ProtectedRoute>} />

              {/* Default: redirect to user login */}
              <Route path="/" element={<Navigate to="/user-login" replace />} />
            </Routes>
          </div>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

function HomePage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to SpendSense
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Operator Dashboard for Behavioral Signal Analysis
        </p>
        <Link
          to="/signals"
          className="inline-block px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
        >
          View Signal Dashboard
        </Link>
      </div>
    </div>
  );
}

export default App;
