import { AlertCircle, Lock, Mail, User, UserPlus } from 'lucide-react';
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { getErrorMessage } from '../../utils/helpers';
import AnimatedBackground from '../Background/AnimatedBackground';
import { Footer, Header } from '../Layout';
import './Auth.css';

const Register: React.FC = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    fullName: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);

    try {
      await register(formData.email, formData.username, formData.password, formData.fullName);
      navigate('/dashboard');
    } catch (err: unknown) {
      setError(getErrorMessage(err) || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <AnimatedBackground />
      <Header showUserInfo={false} />
      
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <div className="auth-icon">
              <UserPlus />
            </div>
            <h2 className="auth-title">Create your account</h2>
            <p className="auth-subtitle">
              Already have an account?{' '}
              <Link to="/login" className="auth-link">
                Sign in
              </Link>
            </p>
          </div>

          {error && (
            <div className="auth-error">
              <AlertCircle className="auth-error-icon" />
              <p className="auth-error-text">{error}</p>
            </div>
          )}

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="auth-form-group">
              <label htmlFor="email" className="auth-label">
                Email address
              </label>
              <div className="auth-input-wrapper">
                <Mail className="auth-input-icon" />
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className="auth-input"
                  placeholder="you@example.com"
                />
              </div>
            </div>

            <div className="auth-form-group">
              <label htmlFor="username" className="auth-label">
                Username
              </label>
              <div className="auth-input-wrapper">
                <User className="auth-input-icon" />
                <input
                  id="username"
                  name="username"
                  type="text"
                  required
                  value={formData.username}
                  onChange={handleChange}
                  className="auth-input"
                  placeholder="johndoe"
                />
              </div>
            </div>

            <div className="auth-form-group">
              <label htmlFor="fullName" className="auth-label">
                Full Name <span className="auth-label-optional">(Optional)</span>
              </label>
              <input
                id="fullName"
                name="fullName"
                type="text"
                value={formData.fullName}
                onChange={handleChange}
                className="auth-input auth-input-no-icon"
                placeholder="John Doe"
              />
            </div>

            <div className="auth-form-group">
              <label htmlFor="password" className="auth-label">
                Password
              </label>
              <div className="auth-input-wrapper">
                <Lock className="auth-input-icon" />
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="auth-input"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <div className="auth-form-group">
              <label htmlFor="confirmPassword" className="auth-label">
                Confirm Password
              </label>
              <div className="auth-input-wrapper">
                <Lock className="auth-input-icon" />
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  required
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className="auth-input"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="auth-submit-btn"
            >
              {loading ? (
                <span className="auth-btn-content">
                  <svg className="auth-spinner" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Creating account...
                </span>
              ) : (
                'Create account'
              )}
            </button>
          </form>
        </div>
      </div>
      
      <Footer />
    </div>
  );
};

export default Register;
