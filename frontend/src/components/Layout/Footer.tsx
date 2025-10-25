import { BarChart3, Github, Linkedin, Mail, Twitter } from 'lucide-react';
import React from 'react';
import './Layout.css';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="layout-footer">
      <div className="layout-footer-content">
        {/* Top Section */}
        <div className="layout-footer-top">
          {/* Brand Column */}
          <div className="layout-footer-brand">
            <div className="layout-footer-logo">
              <div className="layout-footer-logo-icon">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <span className="layout-footer-logo-text">Finalyst</span>
            </div>
            <p className="layout-footer-description">
              Intelligent financial analysis powered by AI. Transform your annual reports into actionable insights.
            </p>
            <div className="layout-footer-social">
              <a href="#" className="layout-social-link" aria-label="Twitter">
                <Twitter className="w-5 h-5" />
              </a>
              <a href="#" className="layout-social-link" aria-label="LinkedIn">
                <Linkedin className="w-5 h-5" />
              </a>
              <a href="#" className="layout-social-link" aria-label="GitHub">
                <Github className="w-5 h-5" />
              </a>
              <a href="#" className="layout-social-link" aria-label="Email">
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div className="layout-footer-links">
            <h3 className="layout-footer-heading">Product</h3>
            <ul className="layout-footer-list">
              <li><a href="#" className="layout-footer-link">Features</a></li>
              <li><a href="#" className="layout-footer-link">Pricing</a></li>
              <li><a href="#" className="layout-footer-link">Documentation</a></li>
              <li><a href="#" className="layout-footer-link">API Reference</a></li>
            </ul>
          </div>

          {/* Company */}
          <div className="layout-footer-links">
            <h3 className="layout-footer-heading">Company</h3>
            <ul className="layout-footer-list">
              <li><a href="#" className="layout-footer-link">About Us</a></li>
              <li><a href="#" className="layout-footer-link">Careers</a></li>
              <li><a href="#" className="layout-footer-link">Blog</a></li>
              <li><a href="#" className="layout-footer-link">Contact</a></li>
            </ul>
          </div>

          {/* Support */}
          <div className="layout-footer-links">
            <h3 className="layout-footer-heading">Support</h3>
            <ul className="layout-footer-list">
              <li><a href="#" className="layout-footer-link">Help Center</a></li>
              <li><a href="#" className="layout-footer-link">Privacy Policy</a></li>
              <li><a href="#" className="layout-footer-link">Terms of Service</a></li>
              <li><a href="#" className="layout-footer-link">Cookie Policy</a></li>
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="layout-footer-bottom">
          <p className="layout-footer-copyright">
            © {currentYear} AI Analyst Agent. All rights reserved.
          </p>
          <p className="layout-footer-tagline">
            Built with ❤️ for financial intelligence
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
