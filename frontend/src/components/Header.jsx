import { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { logout as logoutApi } from '../services/api';
import defaultSilhouette from '../assets/default_silhouette.png';
import logo from '../assets/logo.png';
import logoLight from '../assets/logo_light.png';
import styles from './Header.module.css';

// Dark mode localStorage key
const DARK_MODE_KEY = 'scholarsphere_dark_mode';

/**
 * Reusable header component with profile dropdown
 */
function Header() {
  const navigate = useNavigate();
  const location = useLocation();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isSearchDropdownOpen, setIsSearchDropdownOpen] = useState(false);
  const [faculty, setFaculty] = useState(null);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const dropdownRef = useRef(null);
  const buttonRef = useRef(null);
  const searchDropdownRef = useRef(null);
  const searchButtonRef = useRef(null);

  // Initialize dark mode from localStorage
  useEffect(() => {
    const savedDarkMode = localStorage.getItem(DARK_MODE_KEY);
    if (savedDarkMode === 'true') {
      setIsDarkMode(true);
      document.documentElement.classList.add('dark');
    } else {
      setIsDarkMode(false);
      document.documentElement.classList.remove('dark');
    }
  }, []);

  const toggleDarkMode = () => {
    const newDarkMode = !isDarkMode;
    setIsDarkMode(newDarkMode);
    localStorage.setItem(DARK_MODE_KEY, String(newDarkMode));
    if (newDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

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
    navigate(`/faculty/${faculty.faculty_id}`);
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
    <header className={styles.header}>
      <div className={styles['header-left']}>
        <Link to="/dashboard" className={styles['header-logo']}>
          <img src={isDarkMode ? logoLight : logo} alt="ScholarSphere" className={styles['header-logo-img']} />
        </Link>
        {faculty && (
          <nav className={styles['header-nav']}>
            <Link 
              to="/dashboard" 
              className={`${styles['header-nav-link']} ${location.pathname === '/dashboard' ? styles.active : ''}`}
            >
              Dashboard
            </Link>
            <div className={styles['header-search-dropdown-container']}>
              <button
                ref={searchButtonRef}
                className={`${styles['header-nav-link']} ${styles['header-search-dropdown-button']} ${location.pathname.startsWith('/search') ? styles.active : ''}`}
                onClick={() => setIsSearchDropdownOpen(!isSearchDropdownOpen)}
              >
                Search
                <svg 
                  className={`${styles['header-search-arrow']} ${isSearchDropdownOpen ? styles.open : ''}`}
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
                <div ref={searchDropdownRef} className={styles['header-search-dropdown']}>
                  <Link 
                    to="/search/faculty" 
                    className={`${styles['header-search-dropdown-link']} ${location.pathname === '/search/faculty' ? styles.active : ''}`}
                    onClick={() => setIsSearchDropdownOpen(false)}
                  >
                    Faculty
                  </Link>
                  <Link 
                    to="/search/equipment" 
                    className={`${styles['header-search-dropdown-link']} ${location.pathname === '/search/equipment' ? styles.active : ''}`}
                    onClick={() => setIsSearchDropdownOpen(false)}
                  >
                    Equipment
                  </Link>
                  <Link 
                    to="/search/grants" 
                    className={`${styles['header-search-dropdown-link']} ${location.pathname === '/search/grants' ? styles.active : ''}`}
                    onClick={() => setIsSearchDropdownOpen(false)}
                  >
                    Grants
                  </Link>
                  <Link 
                    to="/search/institutions" 
                    className={`${styles['header-search-dropdown-link']} ${location.pathname === '/search/institutions' ? styles.active : ''}`}
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
        <div className={styles['header-profile-container']}>
          <button
            ref={buttonRef}
            className={styles['header-profile-button']}
            onClick={toggleDropdown}
            aria-expanded={isDropdownOpen}
            aria-haspopup="true"
          >
            <div className={styles['header-profile-avatar-wrapper']}>
              <img 
                src={defaultSilhouette} 
                alt="Profile" 
                className={styles['header-profile-icon']}
              />
            </div>
            <div className={styles['header-profile-info']}>
              <span className={styles['header-profile-name']}>
                {truncatedFirstName} {truncatedLastName}
              </span>
              <span className={styles['header-profile-institution']}>{truncatedInstitutionName}</span>
            </div>
            <svg 
              className={`${styles['header-dropdown-arrow']} ${isDropdownOpen ? styles.open : ''}`}
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
            <div ref={dropdownRef} className={styles['header-dropdown']}>
              {/* User Info Section */}
              <div className={styles['header-dropdown-section']}>
                <div className={styles['header-dropdown-user-info']}>
                  <img 
                    src={defaultSilhouette} 
                    alt="Profile" 
                    className={styles['header-dropdown-avatar']}
                  />
                  <div className={styles['header-dropdown-user-details']}>
                    <div className={styles['header-dropdown-name']}>
                      {truncatedFirstName} {truncatedLastName}
                    </div>
                    <div className={styles['header-dropdown-institution']}>{truncatedInstitutionName}</div>
                    <div className={styles['header-dropdown-department']}>{truncatedDepartmentName}</div>
                  </div>
                </div>
                <button 
                  className={styles['header-dropdown-view-profile']}
                  onClick={handleViewProfile}
                >
                  View Profile
                </button>
              </div>

              {/* Separator */}
              <div className={styles['header-dropdown-divider']}></div>

              {/* Actions Section */}
              <div className={styles['header-dropdown-section']}>
                <Link 
                  to="/help" 
                  className={styles['header-dropdown-link']}
                  onClick={() => setIsDropdownOpen(false)}
                >
                  Help
                </Link>
                <Link 
                  to="/settings" 
                  className={styles['header-dropdown-link']}
                  onClick={() => setIsDropdownOpen(false)}
                >
                  Settings & Privacy
                </Link>
                 {/* Dark Mode Toggle */}
                 <div className={styles['header-dropdown-theme']}>
                  <span className={styles['header-dropdown-theme-label']}>
                    Dark Mode
                  </span>
                  <button 
                    className={`${styles['theme-toggle']} ${isDarkMode ? styles['theme-toggle-active'] : ''}`}
                    onClick={toggleDarkMode}
                    aria-label="Toggle dark mode"
                  >
                    <span className={styles['theme-toggle-slider']}></span>
                  </button>
                </div>
                <button 
                  className={styles['header-dropdown-logout']}
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
