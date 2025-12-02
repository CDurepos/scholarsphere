import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { logout as logoutApi } from '../services/api';
import defaultSilhouette from '../assets/default_silhouette.png';
import './Header.css';

/**
 * Reusable header component with profile dropdown
 */
function Header() {
  const navigate = useNavigate();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [faculty, setFaculty] = useState(null);
  const dropdownRef = useRef(null);
  const buttonRef = useRef(null);

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
      <Link to="/dashboard" className="header-home">
        <h1>ScholarSphere</h1>
      </Link>
      
      {faculty && (
        <div className="header-profile-container">
          <button
            ref={buttonRef}
            className="header-profile-button"
            onClick={toggleDropdown}
            aria-expanded={isDropdownOpen}
            aria-haspopup="true"
          >
            <img 
              src={defaultSilhouette} 
              alt="Profile" 
              className="header-profile-icon"
            />
            <span className="header-profile-text">Me</span>
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

