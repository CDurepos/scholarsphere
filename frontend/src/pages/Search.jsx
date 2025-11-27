import { useState } from 'react';
import TopBar from '../components/TopBar';
import { searchFaculty } from '../services/api';
import './Search.css';

/**
 * Search page component - allows users to search for faculty members
 */
function Search() {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState([]);
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
      // Pass the query string as a search parameter
      // The backend handles parsing it appropriately
      const response = await searchFaculty({ query: searchQuery.trim() });
      
      // Limit results to MAX_RESULTS
      const limitedResults = Array.isArray(response) 
        ? response.slice(0, MAX_RESULTS)
        : [];
      
      setResults(limitedResults);
    } catch (err) {
      console.error('Search error:', err);
      setError('An error occurred while searching. Please try again.');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setSearchQuery(e.target.value);
    setError('');
  };

  return (
    <div className="search-container">
      <TopBar />
      
      <main className="search-main">
        <div className="search-content">
          <h2 className="search-title">Search Faculty</h2>
          
          <form onSubmit={handleSearch} className="search-form">
            <div className="search-input-wrapper">
              <input
                type="text"
                className="search-input"
                placeholder="Search by name, department, or institution..."
                value={searchQuery}
                onChange={handleInputChange}
                disabled={loading}
              />
              <button 
                type="submit" 
                className="search-button"
                disabled={loading || !searchQuery.trim()}
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </form>

          {error && <div className="search-error">{error}</div>}

          <div className="search-results-container">
            {results.length > 0 ? (
              <>
                <div className="search-results-header">
                  <p className="search-results-count">
                    Found {results.length} result{results.length !== 1 ? 's' : ''}
                  </p>
                </div>
                <div className="search-results-list">
                  {results.map((faculty) => (
                    <div key={faculty.faculty_id} className="search-result-card">
                      <h3 className="result-name">
                        {faculty.first_name} {faculty.last_name}
                      </h3>
                      {faculty.department_name && (
                        <p className="result-info">
                          <span className="result-label">Department:</span>{' '}
                          {faculty.department_name}
                        </p>
                      )}
                      {faculty.institution_name && (
                        <p className="result-info">
                          <span className="result-label">Institution:</span>{' '}
                          {faculty.institution_name}
                        </p>
                      )}
                      {faculty.biography && (
                        <p className="result-biography">{faculty.biography}</p>
                      )}
                    </div>
                  ))}
                </div>
              </>
            ) : searchQuery && !loading && !error ? (
              <div className="search-empty">
                <p>No results found. Try a different search term.</p>
              </div>
            ) : null}
          </div>
        </div>
      </main>
    </div>
  );
}

export default Search;

