import { Link } from 'react-router-dom';
import defaultSilhouette from '../assets/default_silhouette.png';
import './TopBar.css';

/**
 * Reusable top bar component with home link and profile icon
 */
function TopBar() {
  return (
    <header className="topbar">
      <Link to="/dashboard" className="topbar-home">
        <h1>ScholarSphere</h1>
      </Link>
      <Link to="/profile" className="topbar-profile">
        <img 
          src={defaultSilhouette} 
          alt="Profile" 
          className="topbar-profile-icon"
        />
      </Link>
    </header>
  );
}

export default TopBar;

