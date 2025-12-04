import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { logout as logoutApi } from '../services/api';
import defaultSilhouette from '../assets/default_silhouette.png';
import logo from '../assets/logo.png';
import './Header.css';

/**
 * Reusable header component with profile dropdown
 */
function Header() {
  const navigate = useNavigate();
  const location = useLocation();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isSearchDropdownOpen, setIsSearchDropdownOpen] = useState(false);
  const [faculty, setFaculty] = useState(null);
  const dropdownRef = useRef(null);
  const buttonRef = useRef(null);
  const searchDropdownRef = useRef(null);
  const searchButtonRef = useRef(null);

  useEffect(() => {
    const facultyData = localStorage.getItem('faculty');
    if (facultyData) {
      try {
        setFaculty(JSON.parse(facultyData));
      } catch (err) {
        setFaculty(null);
      }
    } else {
      setFaculty(null);
    }
  }, []);

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
      if (
        searchDropdownRef.current &&
        searchButtonRef.current &&
        !searchDropdownRef.current.contains(event.target) &&
        !searchButtonRef.current.contains(event.target)
      ) {
        setIsSearchDropdownOpen(false);
      }
    };

    if (isDropdownOpen || isSearchDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isDropdownOpen, isSearchDropdownOpen]);

  const handleLogout = async () => {
    setIsDropdownOpen(false);
    setFaculty(null);
    await logoutApi();
    localStorage.removeItem('faculty');
    localStorage.removeItem('faculty_id');
    navigate('/', { replace: true });
  };

  const toggleDropdown = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  const handleViewProfile = () => {
    setIsDropdownOpen(false);
    // TODO: Navigate to profile page when implemented
  };

  // Helper function to truncate text with ellipsis
  const truncateText = (text, maxLength) => {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  // Get user's institution and department
  const institutionName = faculty?.institution_name || 'Not specified';
  const departmentName = faculty?.departments && faculty.departments.length > 0 
    ? faculty.departments[0] 
    : 'Not specified';
  
  // Truncate names and institution for display
  const truncatedFirstName = truncateText(faculty?.first_name || '', 20);
  const truncatedLastName = truncateText(faculty?.last_name || '', 20);
  const truncatedInstitutionName = truncateText(institutionName, 40);
  const truncatedDepartmentName = truncateText(departmentName, 30);

  return (
    <header className="header">
      <div className="header-left">
        <Link to="/dashboard" className="header-logo">
          <img src={logo} alt="ScholarSphere" className="header-logo-img" />
        </Link>
        {faculty && (
          <nav className="header-nav">
            <Link 
              to="/dashboard" 
              className={`header-nav-link ${location.pathname === '/dashboard' ? 'active' : ''}`}
            >
              Dashboard
            </Link>
            <div className="header-search-dropdown-container">
              <button
                ref={searchButtonRef}
                className={`header-nav-link header-search-dropdown-button ${location.pathname.startsWith('/search') ? 'active' : ''}`}
                onClick={() => setIsSearchDropdownOpen(!isSearchDropdownOpen)}
              >
                Search
                <svg 
                  className={`header-search-arrow ${isSearchDropdownOpen ? 'open' : ''}`}
                  width="12" 
                  height="12" 
                  viewBox="0 0 12 12" 
                  fill="none"
                >
                  <path 
                    d="M3 4.5L6 7.5L9 4.5" 
                    stroke="currentColor" 
                    strokeWidth="1.5" 
                    strokeLinecap="round" 
                    strokeLinejoin="round"
                  />
                </svg>
              </button>
              {isSearchDropdownOpen && (
                <div ref={searchDropdownRef} className="header-search-dropdown">
                  <Link 
                    to="/search/faculty" 
                    className={`header-search-dropdown-link ${location.pathname === '/search/faculty' ? 'active' : ''}`}
                    onClick={() => setIsSearchDropdownOpen(false)}
                  >
                    Faculty
                  </Link>
                  <Link 
                    to="/search/equipment" 
                    className={`header-search-dropdown-link ${location.pathname === '/search/equipment' ? 'active' : ''}`}
                    onClick={() => setIsSearchDropdownOpen(false)}
                  >
                    Equipment
                  </Link>
                  <Link 
                    to="/search/grants" 
                    className={`header-search-dropdown-link ${location.pathname === '/search/grants' ? 'active' : ''}`}
                    onClick={() => setIsSearchDropdownOpen(false)}
                  >
                    Grants
                  </Link>
                  <Link 
                    to="/search/institutions" 
                    className={`header-search-dropdown-link ${location.pathname === '/search/institutions' ? 'active' : ''}`}
                    onClick={() => setIsSearchDropdownOpen(false)}
                  >
                    Institutions
                  </Link>
                </div>
              )}
            </div>
          </nav>
        )}
      </div>
      
      {faculty && (
        <div className="header-profile-container">
          <button
            ref={buttonRef}
            className="header-profile-button"
            onClick={toggleDropdown}
            aria-expanded={isDropdownOpen}
            aria-haspopup="true"
          >
            <div className="header-profile-avatar-wrapper">
              <img 
                src={defaultSilhouette} 
                alt="Profile" 
                className="header-profile-icon"
              />
            </div>
            <div className="header-profile-info">
              <span className="header-profile-name">
                {truncatedFirstName} {truncatedLastName}
              </span>
              <span className="header-profile-institution">{truncatedInstitutionName}</span>
            </div>
            <svg 
              className={`header-dropdown-arrow ${isDropdownOpen ? 'open' : ''}`}
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
            <div ref={dropdownRef} className="header-dropdown">
              {/* User Info Section */}
              <div className="header-dropdown-section">
                <div className="header-dropdown-user-info">
                  <img 
                    src={defaultSilhouette} 
                    alt="Profile" 
                    className="header-dropdown-avatar"
                  />
                  <div className="header-dropdown-user-details">
                    <div className="header-dropdown-name">
                      {truncatedFirstName} {truncatedLastName}
                    </div>
                    <div className="header-dropdown-institution">{truncatedInstitutionName}</div>
                    <div className="header-dropdown-department">{truncatedDepartmentName}</div>
                  </div>
                </div>
                <button 
                  className="header-dropdown-view-profile"
                  onClick={handleViewProfile}
                >
                  View Profile
                </button>
              </div>

              {/* Separator */}
              <div className="header-dropdown-divider"></div>

              {/* Actions Section */}
              <div className="header-dropdown-section">
                <Link 
                  to="/help" 
                  className="header-dropdown-link"
                  onClick={() => setIsDropdownOpen(false)}
                >
                  Help
                </Link>
                <Link 
                  to="/settings" 
                  className="header-dropdown-link"
                  onClick={() => setIsDropdownOpen(false)}
                >
                  Settings & Privacy
                </Link>
                <button 
                  className="header-dropdown-logout"
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

export default Header;

