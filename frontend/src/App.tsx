import React from 'react';
import { Navigate, Route, Routes, useParams } from 'react-router-dom';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import AnimatedBackground from './components/Background/AnimatedBackground';
import Dashboard from './components/Dashboard/Dashboard';
import LandingPage from './components/Landing/LandingPage';
import AgentPage from './components/ReportAnalysis/AgentPage';
import ChartsPage from './components/ReportAnalysis/ChartsPage';
import ChatPage from './components/ReportAnalysis/ChatPage';
import EmailPage from './components/ReportAnalysis/EmailPage';
import OverviewPage from './components/ReportAnalysis/OverviewPage';
import PredictionsPage from './components/ReportAnalysis/PredictionsPage';
import { useAuth } from './context/AuthContext';

// Redirect component for old report route
const ReportRedirect: React.FC = () => {
  const { reportId } = useParams<{ reportId: string }>();
  return <Navigate to={`/report/${reportId}/overview`} replace />;
};

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-indigo-50 via-blue-50 to-purple-50">
        <div className="text-center">
          <div className="relative w-16 h-16 mx-auto">
            <div className="absolute top-0 left-0 w-16 h-16 border-4 border-indigo-200 rounded-full"></div>
            <div className="absolute top-0 left-0 w-16 h-16 border-4 border-indigo-600 rounded-full border-t-transparent animate-spin"></div>
          </div>
          <p className="mt-6 text-lg font-semibold text-gray-700">Loading...</p>
        </div>
      </div>
    );
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

// Public Route Component (redirects to dashboard if authenticated)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-indigo-50 via-blue-50 to-purple-50">
        <div className="text-center">
          <div className="relative w-16 h-16 mx-auto">
            <div className="absolute top-0 left-0 w-16 h-16 border-4 border-indigo-200 rounded-full"></div>
            <div className="absolute top-0 left-0 w-16 h-16 border-4 border-indigo-600 rounded-full border-t-transparent animate-spin"></div>
          </div>
          <p className="mt-6 text-lg font-semibold text-gray-700">Loading...</p>
        </div>
      </div>
    );
  }

  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <>{children}</>;
};

function App() {
  return (
    <>
      {/* Animated background layer - sits behind all content */}
      <AnimatedBackground />
      
      <Routes>
      {/* Authentication Routes */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicRoute>
            <Register />
          </PublicRoute>
        }
      />

      {/* Protected Routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      
      {/* Report Analysis Tab Routes */}
      <Route
        path="/report/:reportId/overview"
        element={
          <ProtectedRoute>
            <OverviewPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/report/:reportId/charts"
        element={
          <ProtectedRoute>
            <ChartsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/report/:reportId/predictions"
        element={
          <ProtectedRoute>
            <PredictionsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/report/:reportId/chat"
        element={
          <ProtectedRoute>
            <ChatPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/report/:reportId/agent"
        element={
          <ProtectedRoute>
            <AgentPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/report/:reportId/email"
        element={
          <ProtectedRoute>
            <EmailPage />
          </ProtectedRoute>
        }
      />
      
      {/* Redirect old report route to overview */}
      <Route
        path="/report/:reportId"
        element={
          <ProtectedRoute>
            <ReportRedirect />
          </ProtectedRoute>
        }
      />

      {/* Landing Page */}
      <Route path="/" element={<LandingPage />} />
      
      {/* 404 Route */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
    </>
  );
}

export default App;
