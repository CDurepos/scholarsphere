import { useState, useEffect } from 'react';
import Header from '../../components/Header';
import styles from './Equipment.module.css';

function Equipment() {
  const [institutions, setInstitutions] = useState([]);
  const [locations, setLocations] = useState([]);
  const [menuOpen, setMenuOpen] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const [keywords, setKeywords] = useState('');
  const [availableOnly, setAvailableOnly] = useState(false);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // ---- Load institutions dynamically ----
  useEffect(() => {
    fetch('/api/institution/list')
      .then(res => res.json())
      .then(data => {
        // Sort alphabetically so menu is clean
        const sorted = data.sort((a, b) => a.name.localeCompare(b.name));
        setInstitutions(sorted);
      })
      .catch(err => console.error("Failed to load institutions:", err));
  }, []);

  // ---- Toggle one location ----
  const toggleLocation = (city) => {
    setLocations(prev =>
      prev.includes(city)
        ? prev.filter(c => c !== city)
        : [...prev, city]
    );
  };

  const clearLocations = (e) => {
    e.stopPropagation();
    setLocations([]);
  };

  // ---- Perform Search ----
  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setHasSearched(true);

    try {
      const params = new URLSearchParams({
        keywords,
        available: availableOnly,
      });

      // Append multiple selected locations
      locations.forEach(loc => params.append("location", loc));

      const res = await fetch(`/api/equipment/search?${params.toString()}`);
      const data = await res.json();

      setResults(data);
    } catch (err) {
      setError('An error occurred while searching. Please try again.');
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const handleExpandHero = () => {
    setHasSearched(false);
  };

  return (
    <div className={styles['search-container']}>
      <Header />

      <main className={styles['search-main']}>
        <div className={styles['search-content']}>
          {/* Compact Hero - Just an expand bar */}
          {hasSearched && (
            <button 
              type="button"
              className={styles['search-hero-compact']}
              onClick={handleExpandHero}
              aria-label="Expand search"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="m18 15-6-6-6 6"/>
              </svg>
            </button>
          )}

          {/* Full Hero Section with Search */}
          {!hasSearched && (
            <div className={`${styles['search-hero']} ${showAdvanced ? styles['search-hero-advanced'] : ''}`}>
              {/* Minimize button - top left */}
              <button 
                type="button"
                className={styles['search-hero-minimize']}
                onClick={() => setHasSearched(true)}
                aria-label="Minimize search"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M5 12h14"/>
                </svg>
              </button>

              <h2 className={styles['search-title']}>Search Equipment</h2>
              <p className={styles['search-subtitle']}>
                Find equipment by name, description, or location
              </p>
              
              <form onSubmit={handleSearch} className={styles['search-form']}>
                <div className={styles['search-input-wrapper']}>
                  <input
                    type="text"
                    className={styles['search-input']}
                    placeholder="Search by keywords..."
                    value={keywords}
                    onChange={(e) => setKeywords(e.target.value)}
                    disabled={loading}
                  />
                  <button 
                    type="submit" 
                    className={styles['search-button']}
                    disabled={loading || !keywords.trim()}
                  >
                    {loading ? 'Searching...' : 'Search'}
                  </button>
                </div>

                {/* Advanced Search Section */}
                <div className={`${styles['search-advanced']} ${showAdvanced ? styles['search-advanced-visible'] : ''}`}>
                  <div className={styles['search-advanced-content']}>
                    {/* Multi-select Location Menu */}
                    <div className={styles['search-advanced-field']}>
                      <div className={styles['institutions-header']}>
                        <label className={styles['search-advanced-label']}>Locations</label>
                        <button
                          type="button"
                          className={styles['institutions-toggle']}
                          onClick={() => setMenuOpen(!menuOpen)}
                          aria-label={menuOpen ? 'Collapse institutions' : 'Expand institutions'}
                        >
                          <span>{menuOpen ? 'Hide' : 'Show'} Institutions</span>
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d={menuOpen ? "m18 15-6-6-6 6" : "m6 9 6 6 6-6"}/>
                          </svg>
                        </button>
                      </div>
                      
                      {locations.length > 0 && (
                        <div className={styles['selected-count']}>
                          {locations.length} {locations.length === 1 ? 'institution' : 'institutions'} selected
                          <button
                            type="button"
                            className={styles['clear-selected-btn']}
                            onClick={clearLocations}
                          >
                            Clear
                          </button>
                        </div>
                      )}

                      {menuOpen && (
                        <div className={styles['institutions-list']} onClick={(e) => e.stopPropagation()}>
                          {institutions.map(inst => (
                            <label key={inst.name} className={styles['institution-item']}>
                              <input
                                type="checkbox"
                                checked={locations.includes(inst.city)}
                                onChange={() => toggleLocation(inst.city)}
                                disabled={loading}
                              />
                              <div className={styles['institution-info']}>
                                <span className={styles['institution-name']}>{inst.name}</span>
                                <span className={styles['institution-city']}>{inst.city}</span>
                              </div>
                            </label>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Availability */}
                    <div className={styles['checkbox-group']}>
                      <input
                        type="checkbox"
                        id="availableOnly"
                        checked={availableOnly}
                        onChange={(e) => setAvailableOnly(e.target.checked)}
                        disabled={loading}
                      />
                      <label htmlFor="availableOnly" className={styles['search-advanced-label']}>
                        Show only available equipment
                      </label>
                    </div>
                  </div>
                </div>
              </form>

              {/* Advanced toggle arrow - at bottom */}
              <button 
                type="button"
                className={`${styles['search-hero-toggle']} ${showAdvanced ? styles['search-hero-toggle-active'] : ''}`}
                onClick={() => setShowAdvanced(!showAdvanced)}
                aria-label={showAdvanced ? 'Hide advanced search' : 'Show advanced search'}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="m6 9 6 6 6-6"/>
                </svg>
              </button>
            </div>
          )}

          {/* Results Section */}
          <div className={`${styles['search-results-section']} ${results?.length > 0 ? styles['search-results-section-expanded'] : ''}`}>
            {error && <div className={styles['search-error']}>{error}</div>}

            {results === null && !error ? (
              <div className={styles['search-initial']}>
                <div className={styles['search-initial-icon']}>
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                    <path d="M9 9h6v6H9z"/>
                  </svg>
                </div>
                <h3>Start Your Search</h3>
                <p>Enter keywords to find equipment</p>
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
                  <div className={styles['search-results-list']}>
                    {results.map((item) => (
                      <div 
                        key={item.equipment_id} 
                        className={styles['search-result-card']}
                      >
                        <div className={styles['result-content']}>
                          <div className={styles['result-header']}>
                            <h3 className={styles['result-name']}>{item.name}</h3>
                            <span className={styles['result-badge']}>Equipment</span>
                          </div>
                          <div className={styles['result-meta']}>
                            {item.institution_name && (
                              <p className={styles['result-info']}>
                                <svg className={styles['result-info-icon']} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                  <path d="M3 21h18"/>
                                  <path d="M5 21V7l8-4v18"/>
                                  <path d="M19 21V11l-6-4"/>
                                </svg>
                                {item.institution_name}
                              </p>
                            )}
                            {item.city && (
                              <p className={styles['result-info']}>
                                <svg className={styles['result-info-icon']} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                                  <circle cx="12" cy="10" r="3"/>
                                </svg>
                                {item.city}
                              </p>
                            )}
                          </div>
                          {item.description && (
                            <p className={styles['result-biography']}>
                              {item.description}
                            </p>
                          )}
                          {item.availability && (
                            <p className={styles['result-info']} style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(11, 38, 79, 0.08)' }}>
                              <strong>Availability:</strong> {item.availability}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            ) : !loading && !error && results !== null && results.length === 0 ? (
              <div className={styles['search-empty']}>
                <div className={styles['search-empty-icon']}>
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                    <path d="M9 9h6v6H9z"/>
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

export default Equipment;
