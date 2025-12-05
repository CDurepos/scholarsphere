import { useState, useCallback } from 'react';
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
  const MAX_RESULTS = 50;

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }

    setLoading(true);
    setError('');

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

  return (
    <div className={styles['search-container']}>
      <Header />
      
      <main className={styles['search-main']}>
        <div className={styles['search-content']}>
          <h2 className={styles['search-title']}>Search Faculty</h2>
          
          <form onSubmit={handleSearch} className={styles['search-form']}>
            <div className={styles['search-input-wrapper']}>
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

          {error && <div className={styles['search-error']}>{error}</div>}

          <div className={styles['search-results-container']}>
            {results?.length > 0 ? (
              <>
                <div className={styles['search-results-header']}>
                  <p className={styles['search-results-count']}>
                    Found {results.length} result{results.length !== 1 ? 's' : ''}
                  </p>
                </div>
                <div className={styles['search-results-list']}>
                  {results.map((faculty) => (
                    <div key={faculty.faculty_id} onClick={() => handleResultClick(faculty.faculty_id)} className={styles['search-result-card']}>
                      <h3 className={styles['result-name']}>
                        {truncateText(faculty.first_name, 30)} {truncateText(faculty.last_name, 30)}
                      </h3>
                      {faculty.department_name && (
                        <p className={styles['result-info']}>
                          <span className={styles['result-label']}>Department:</span>{' '}
                          {truncateText(faculty.department_name, 40)}
                        </p>
                      )}
                      {faculty.institution_name && (
                        <p className={styles['result-info']}>
                          <span className={styles['result-label']}>Institution:</span>{' '}
                          {truncateText(faculty.institution_name, 40)}
                        </p>
                      )}
                      {faculty.biography && (
                        <p className={styles['result-biography']}>{truncateText(faculty.biography, 200)}</p>
                      )}
                    </div>
                  ))}
                </div>
              </>
            ) : !loading && !error && results !== null && results.length === 0 ? (
              <div className={styles['search-empty']}>
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

