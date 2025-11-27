import { Link } from 'react-router-dom';
import ConnectionParticles from '../components/ConnectionParticles';
import logo from '../assets/logo.png';
import './Landing.css';

// Stable particle config to prevent re-renders
const LANDING_PARTICLE_COLORS = ['#ffffff', '#dfe8ff'];
const LANDING_PARTICLE_LINK_COLOR = '#c6d6ff';
const LANDING_PARTICLE_QUANTITY = 70;

/**
 * Landing page component - forces users to choose between Login or Signup
 */
function Landing() {
  return (
    <div className="landing-container">
      <ConnectionParticles
        className="landing-particles"
        colors={LANDING_PARTICLE_COLORS}
        linkColor={LANDING_PARTICLE_LINK_COLOR}
        quantity={LANDING_PARTICLE_QUANTITY}
      />
      <div className="landing-content">
        <img src={logo} alt="ScholarSphere Logo" className="landing-logo" />
        <h1 className="landing-title">ScholarSphere</h1>
        <p className="landing-subtitle">
          Connecting Maine Scholars
        </p>
        
        <div className="landing-actions">
          <Link to="/login" className="landing-button landing-button-primary">
            Login
          </Link>
          <Link to="/signup" className="landing-button landing-button-secondary">
            Sign Up
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Landing;


