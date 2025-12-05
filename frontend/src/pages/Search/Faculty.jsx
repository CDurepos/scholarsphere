import { useState, useRef, useCallback } from 'react';
import Header from '../../components/Header';
import { searchFaculty } from '../../services/api';
import styles from './Faculty.module.css';

/**
 * Faculty search page component - allows users to search for faculty members
 */
function Faculty() {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hasSearched, setHasSearched] = useState(false);
  const [isAtBottom, setIsAtBottom] = useState(false);
  const resultsListRef = useRef(null);
  const MAX_RESULTS = 50;

  const handleScroll = useCallback(() => {
    if (resultsListRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = resultsListRef.current;
      const atBottom = scrollTop + clientHeight >= scrollHeight - 20;
      setIsAtBottom(atBottom);
    }
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }

    setLoading(true);
    setError('');
    setHasSearched(true);

    try {
      const response = await searchFaculty({ query: searchQuery.trim() });
      
      const limitedResults = Array.isArray(response) 
        ? response.slice(0, MAX_RESULTS)
        : [];
      
      setResults(limitedResults);
    } catch (err) {
      setError('An error occurred while searching. Please try again.');
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setSearchQuery(e.target.value);
    setError('');
  };

  const handleResultClick = (facultyId) => {
    // TODO: Navigate to profile page when implemented
  };

  const truncateText = (text, maxLength) => {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const getInitials = (firstName, lastName) => {
    const first = firstName ? firstName.charAt(0).toUpperCase() : '';
    const last = lastName ? lastName.charAt(0).toUpperCase() : '';
    return first + last || '?';
  };

  return (
    <div className={styles['search-container']}>
      <Header />
      
      <main className={styles['search-main']}>
        <div className={styles['search-content']}>
          {/* Hero Section with Search */}
          <div className={`${styles['search-hero']} ${hasSearched ? styles['search-hero-compact'] : ''}`}>
            <h2 className={`${styles['search-title']} ${hasSearched ? styles['search-title-hidden'] : ''}`}>
              Search Faculty
            </h2>
            <p className={`${styles['search-subtitle']} ${hasSearched ? styles['search-subtitle-hidden'] : ''}`}>
              Find researchers by name, department, or institution
            </p>
            
            <form onSubmit={handleSearch} className={styles['search-form']}>
              <div className={`${styles['search-input-wrapper']} ${hasSearched ? styles['search-input-wrapper-expanded'] : ''}`}>
                <input
                  type="text"
                  className={styles['search-input']}
                  placeholder="Search by name, department, or institution..."
                  value={searchQuery}
                  onChange={handleInputChange}
                  disabled={loading}
                />
                <button 
                  type="submit" 
                  className={styles['search-button']}
                  disabled={loading || !searchQuery.trim()}
                >
                  {loading ? 'Searching...' : 'Search'}
                </button>
              </div>
            </form>

            {/* Expand arrow - shows only when compact */}
            {hasSearched && (
              <button 
                type="button"
                className={styles['search-hero-expand']}
                onClick={() => setHasSearched(false)}
                aria-label="Expand search"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="m18 15-6-6-6 6"/>
                </svg>
              </button>
            )}
          </div>

          {/* Results Section */}
          <div className={`${styles['search-results-section']} ${results?.length > 0 ? styles['search-results-section-expanded'] : ''}`}>
            {error && <div className={styles['search-error']}>{error}</div>}

            {results === null && !error ? (
              <div className={styles['search-initial']}>
                <div className={styles['search-initial-icon']}>
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="11" cy="11" r="8"/>
                    <path d="m21 21-4.35-4.35"/>
                  </svg>
                </div>
                <h3>Start Your Search</h3>
                <p>Enter a name, department, or institution to find faculty members</p>
              </div>
            ) : results?.length > 0 ? (
              <>
                <div className={styles['search-results-header']}>
                  <h3 className={styles['search-results-title']}>Results</h3>
                  <p className={styles['search-results-count']}>
                    {results.length} {results.length === 1 ? 'match' : 'matches'}
                  </p>
                </div>
                <div className={styles['search-results-list-wrapper']}>
                  <div 
                    className={styles['search-results-list']}
                    ref={resultsListRef}
                    onScroll={handleScroll}
                  >
                    {results.map((faculty) => (
                      <div 
                        key={faculty.faculty_id} 
                        onClick={() => handleResultClick(faculty.faculty_id)} 
                        className={styles['search-result-card']}
                      >
                        <div className={styles['result-avatar']}>
                          {getInitials(faculty.first_name, faculty.last_name)}
                        </div>
                        <div className={styles['result-content']}>
                          <div className={styles['result-header']}>
                            <h3 className={styles['result-name']}>
                              {truncateText(faculty.first_name, 30)} {truncateText(faculty.last_name, 30)}
                            </h3>
                            <span className={styles['result-badge']}>Faculty</span>
                          </div>
                          <div className={styles['result-meta']}>
                            {faculty.department_name && (
                              <p className={styles['result-info']}>
                                <svg className={styles['result-info-icon']} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                  <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
                                  <path d="M6 12v5c3 3 9 3 12 0v-5"/>
                                </svg>
                                {truncateText(faculty.department_name, 40)}
                              </p>
                            )}
                            {faculty.institution_name && (
                              <p className={styles['result-info']}>
                                <svg className={styles['result-info-icon']} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                  <path d="M3 21h18"/>
                                  <path d="M5 21V7l8-4v18"/>
                                  <path d="M19 21V11l-6-4"/>
                                  <path d="M9 9v.01"/>
                                  <path d="M9 12v.01"/>
                                  <path d="M9 15v.01"/>
                                  <path d="M9 18v.01"/>
                                </svg>
                                {truncateText(faculty.institution_name, 40)}
                              </p>
                            )}
                          </div>
                          {faculty.biography && (
                            <p className={styles['result-biography']}>
                              {truncateText(faculty.biography, 200)}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                  {results.length > 3 && (
                    <div className={`${styles['search-results-fade']} ${isAtBottom ? styles['search-results-fade-hidden'] : ''}`} />
                  )}
                </div>
              </>
            ) : !loading && !error && results !== null && results.length === 0 ? (
              <div className={styles['search-empty']}>
                <div className={styles['search-empty-icon']}>
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10"/>
                    <path d="M16 16s-1.5-2-4-2-4 2-4 2"/>
                    <line x1="9" y1="9" x2="9.01" y2="9"/>
                    <line x1="15" y1="9" x2="15.01" y2="9"/>
                  </svg>
                </div>
                <p>No results found. Try a different search term.</p>
              </div>
            ) : null}
          </div>
        </div>
      </main>
    </div>
  );
}

export default Faculty;
