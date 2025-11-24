import { Link } from 'react-router-dom';
import ConnectionParticles from '../components/ConnectionParticles';
import logo from '../assets/logo.png';
import './Landing.css';

/**
 * Landing page component - forces users to choose between Login or Signup
 */
function Landing() {
  return (
    <div className="landing-container">
      <ConnectionParticles
        className="landing-particles"
        colors={['#ffffff', '#dfe8ff']}
        linkColor="#c6d6ff"
        quantity={70}
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


