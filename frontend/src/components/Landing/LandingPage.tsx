import { ArrowRight, BarChart3, Bot, FileText, LineChart, Mail, MessageSquare, Sparkles, TrendingUp, Zap } from 'lucide-react';
import React from 'react';
import { Link } from 'react-router-dom';
import AnimatedBackground from '../Background/AnimatedBackground';
import { Footer, Header } from '../Layout';
import './LandingPage.css';

const LandingPage: React.FC = () => {
  return (
    <div className="landing-page">
      <AnimatedBackground />
      <Header showUserInfo={false} />
      
      <main className="landing-content">
        {/* Hero Section */}
        <section className="hero-section">
          <div className="hero-container">
            <div className="hero-badge">
              <span className="badge-dot"></span>
              <span>AI-Powered Financial Intelligence</span>
            </div>
            
            <h1 className="hero-title">
              Transform Financial Data into
              <span className="hero-gradient"> Strategic Insights</span>
            </h1>
            
            <p className="hero-description">
              Upload your financial reports and let our AI analyst generate comprehensive insights, 
              predictions, and professional reports in seconds. Make data-driven decisions with confidence.
            </p>
            
            <div className="hero-buttons">
              <Link to="/register" className="btn-primary">
                <span>Get Started Free</span>
                <ArrowRight className="btn-icon" />
              </Link>
              <Link to="/login" className="btn-secondary">
                <span>Sign In</span>
              </Link>
            </div>

            <div className="hero-stats">
              <div className="stat-item">
                <div className="stat-number">99.5%</div>
                <div className="stat-label">Accuracy</div>
              </div>
              <div className="stat-divider"></div>
              <div className="stat-item">
                <div className="stat-number">&lt;60s</div>
                <div className="stat-label">Analysis Time</div>
              </div>
              <div className="stat-divider"></div>
              <div className="stat-item">
                <div className="stat-number">24/7</div>
                <div className="stat-label">Availability</div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="features-section">
          <div className="section-header">
            <h2 className="section-title">Powerful Features</h2>
            <p className="section-description">
              Everything you need to analyze, predict, and report on financial data
            </p>
          </div>

          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon feature-icon-blue">
                <FileText />
              </div>
              <h3 className="feature-title">Financial Analysis</h3>
              <p className="feature-description">
                AI-powered comprehensive financial analysis with executive summaries and key insights
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon feature-icon-purple">
                <TrendingUp />
              </div>
              <h3 className="feature-title">ML Predictions</h3>
              <p className="feature-description">
                Advanced machine learning models predict revenue, profit, and cash flow trends
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon feature-icon-green">
                <BarChart3 />
              </div>
              <h3 className="feature-title">Data Visualization</h3>
              <p className="feature-description">
                Interactive charts and graphs that bring your financial data to life
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon feature-icon-cyan">
                <MessageSquare />
              </div>
              <h3 className="feature-title">AI Chatbot</h3>
              <p className="feature-description">
                Ask questions about your financial data in natural language and get instant answers
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon feature-icon-yellow">
                <Zap />
              </div>
              <h3 className="feature-title">Code Agent</h3>
              <p className="feature-description">
                AI agent generates and executes custom analysis code on your financial data
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon feature-icon-red">
                <Mail />
              </div>
              <h3 className="feature-title">Email Reports</h3>
              <p className="feature-description">
                Professional PDF reports sent directly to stakeholders with visualizations
              </p>
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <section className="how-section">
          <div className="section-header">
            <h2 className="section-title">How It Works</h2>
            <p className="section-description">
              Three simple steps to unlock powerful financial insights
            </p>
          </div>

          <div className="steps-container">
            <div className="step-card">
              <div className="step-number">1</div>
              <div className="step-icon">
                <FileText />
              </div>
              <h3 className="step-title">Upload Your Data</h3>
              <p className="step-description">
                Upload your Excel financial reports securely to our platform
              </p>
            </div>

            <div className="step-arrow">
              <ArrowRight />
            </div>

            <div className="step-card">
              <div className="step-number">2</div>
              <div className="step-icon">
                <Bot />
              </div>
              <h3 className="step-title">AI Analysis</h3>
              <p className="step-description">
                Our AI analyzes your data and generates predictions and insights
              </p>
            </div>

            <div className="step-arrow">
              <ArrowRight />
            </div>

            <div className="step-card">
              <div className="step-number">3</div>
              <div className="step-icon">
                <LineChart />
              </div>
              <h3 className="step-title">Get Insights</h3>
              <p className="step-description">
                View interactive dashboards, chat with AI, and share reports
              </p>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="cta-section">
          <div className="cta-container">
            <div className="cta-icon">
              <Sparkles />
            </div>
            <h2 className="cta-title">Ready to Transform Your Financial Analysis?</h2>
            <p className="cta-description">
              Join thousands of analysts who trust Finalyst for their financial intelligence needs
            </p>
            <div className="cta-buttons">
              <Link to="/register" className="btn-cta-primary">
                <span>Start Free Trial</span>
                <ArrowRight className="btn-icon" />
              </Link>
              <Link to="/login" className="btn-cta-secondary">
                <span>View Demo</span>
              </Link>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default LandingPage;