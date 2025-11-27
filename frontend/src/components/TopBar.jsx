import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import defaultSilhouette from '../assets/default_silhouette.png';
import './TopBar.css';

/**
 * Reusable top bar component with profile dropdown
 */
function TopBar() {
  const navigate = useNavigate();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [faculty, setFaculty] = useState(null);
  const dropdownRef = useRef(null);
  const buttonRef = useRef(null);

  // Get faculty data from localStorage
  useEffect(() => {
    const facultyData = localStorage.getItem('faculty');
    if (facultyData) {
      try {
        setFaculty(JSON.parse(facultyData));
      } catch (err) {
        console.error('Failed to parse faculty data:', err);
        setFaculty(null);
      }
    } else {
      setFaculty(null);
    }
  }, []); // Only run on mount - state is cleared immediately in handleLogout

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        dropdownRef.current &&
        buttonRef.current &&
        !dropdownRef.current.contains(event.target) &&
        !buttonRef.current.contains(event.target)
      ) {
        setIsDropdownOpen(false);
      }
    };

    if (isDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isDropdownOpen]);

  const handleLogout = () => {
    setIsDropdownOpen(false);
    setFaculty(null);
    localStorage.removeItem('faculty');
    localStorage.removeItem('faculty_id');
    navigate('/', { replace: true });
  };

  const toggleDropdown = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  const handleViewProfile = () => {
    setIsDropdownOpen(false);
    // Navigate to profile page when implemented
    // navigate('/profile');
  };

  // Get user's institution and department
  const institutionName = faculty?.institution_name || 'Not specified';
  const departmentName = faculty?.departments && faculty.departments.length > 0 
    ? faculty.departments[0] 
    : 'Not specified';

  return (
    <header className="topbar">
      <Link to="/dashboard" className="topbar-home">
        <h1>ScholarSphere</h1>
      </Link>
      
      {faculty && (
        <div className="topbar-profile-container">
          <button
            ref={buttonRef}
            className="topbar-profile-button"
            onClick={toggleDropdown}
            aria-expanded={isDropdownOpen}
            aria-haspopup="true"
          >
            <img 
              src={defaultSilhouette} 
              alt="Profile" 
              className="topbar-profile-icon"
            />
            <span className="topbar-profile-text">Me</span>
            <svg 
              className={`topbar-dropdown-arrow ${isDropdownOpen ? 'open' : ''}`}
              width="16" 
              height="16" 
              viewBox="0 0 16 16" 
              fill="none"
            >
              <path 
                d="M4 6L8 10L12 6" 
                stroke="currentColor" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round"
              />
            </svg>
          </button>

          {isDropdownOpen && (
            <div ref={dropdownRef} className="topbar-dropdown">
              {/* User Info Section */}
              <div className="topbar-dropdown-section">
                <div className="topbar-dropdown-user-info">
                  <img 
                    src={defaultSilhouette} 
                    alt="Profile" 
                    className="topbar-dropdown-avatar"
                  />
                  <div className="topbar-dropdown-user-details">
                    <div className="topbar-dropdown-name">
                      {faculty.first_name} {faculty.last_name}
                    </div>
                    <div className="topbar-dropdown-institution">{institutionName}</div>
                    <div className="topbar-dropdown-department">{departmentName}</div>
                  </div>
                </div>
                <button 
                  className="topbar-dropdown-view-profile"
                  onClick={handleViewProfile}
                >
                  View Profile
                </button>
              </div>

              {/* Separator */}
              <div className="topbar-dropdown-divider"></div>

              {/* Actions Section */}
              <div className="topbar-dropdown-section">
                <Link 
                  to="/help" 
                  className="topbar-dropdown-link"
                  onClick={() => setIsDropdownOpen(false)}
                >
                  Help
                </Link>
                <Link 
                  to="/settings" 
                  className="topbar-dropdown-link"
                  onClick={() => setIsDropdownOpen(false)}
                >
                  Settings & Privacy
                </Link>
                <button 
                  className="topbar-dropdown-logout"
                  onClick={handleLogout}
                >
                  Log out
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </header>
  );
}

export default TopBar;

