import { ArrowRight, BarChart3, LogOut } from 'lucide-react';
import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './Layout.css';

interface HeaderProps {
  showUserInfo?: boolean;
}

const Header: React.FC<HeaderProps> = ({ showUserInfo = false }) => {
  const { user, logout } = useAuth();

  return (
    <header className="layout-header">
      <div className="layout-header-content">
        <div className="layout-header-inner">
          {/* Logo Section */}
          <div className="layout-logo-container">
            <div className="layout-logo-icon">
              <BarChart3 className="w-7 h-7 text-white" />
            </div>
            <div>
                <h1 className="layout-title">
                  Finalyst
                </h1>
                <p className="layout-subtitle">Financial Intelligence Platform</p>
            </div>
          </div>

          {/* User Info & Logout - Authenticated */}
          {showUserInfo && user && (
            <div className="layout-user-section">
              <div className="layout-welcome-badge">
                <span className="layout-welcome-text">Welcome,</span>
                <span className="layout-username">{user.username}</span>
              </div>
              <button
                onClick={logout}
                className="layout-logout-btn"
                aria-label="Logout"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          )}

          {/* Navigation Links - Landing Page */}
          {!showUserInfo && (
            <div className="layout-nav-section">
              <Link to="/login" className="layout-nav-link">
                Sign In
              </Link>
              <Link to="/register" className="layout-nav-btn">
                <span>Get Started</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
