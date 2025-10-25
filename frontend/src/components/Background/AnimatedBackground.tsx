import React from 'react';
import './AnimatedBackground.css';

/**
 * AnimatedBackground Component
 * 
 * A fixed background layer that sits behind all page content.
 * Features:
 * - Multi-layer gradient base
 * - Three floating animated orbs with blur effects
 * - Subtle grid pattern overlay
 * - Animated accent particles for depth
 * - GPU-accelerated animations for performance
 * - Fixed positioning (z-index: -1) to stay behind all content
 */
const AnimatedBackground: React.FC = () => {
  return (
    <div className="animated-background">
      {/* Base gradient layer */}
      <div className="background-gradient"></div>
      
      {/* Floating orbs with blur effects */}
      <div className="floating-orb floating-orb-1"></div>
      <div className="floating-orb floating-orb-2"></div>
      <div className="floating-orb floating-orb-3"></div>
      
      {/* Grid pattern overlay */}
      <div className="grid-pattern"></div>
      
      {/* Accent particles for additional depth */}
      <div className="accent-particles">
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
      </div>
    </div>
  );
};

export default AnimatedBackground;
