import { useState, useEffect } from 'react';
import Header from '../../components/Header';
import './Equipment.css';

function Equipment() {
  const [institutions, setInstitutions] = useState([]);
  const [locations, setLocations] = useState([]);
  const [menuOpen, setMenuOpen] = useState(false);

  const [keywords, setKeywords] = useState('');
  const [availableOnly, setAvailableOnly] = useState(false);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

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

    const params = new URLSearchParams({
      keywords,
      available: availableOnly,
    });

    // Append multiple selected locations
    locations.forEach(loc => params.append("location", loc));

    const res = await fetch(`/api/equipment/search?${params.toString()}`);
    const data = await res.json();

    setResults(data);
    setLoading(false);
  };

  return (
    <div className="search-container">
      <Header />

      <main className="search-main">
        <div className="search-content">
          <h2 className="search-title">Search Equipment</h2>

          {/* Search Form */}
          <form className="search-form" onSubmit={handleSearch}>

            {/* Keywords */}
            <div className="form-group">
              <label>Keywords</label>
              <input
                type="text"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="microscope, PCR, high resolution..."
              />
            </div>

            {/* Multi-select Location Menu */}
            <div className="form-group">
              <label>Locations</label>

              <div
                className="multi-select"
                onClick={() => setMenuOpen(!menuOpen)}
              >
                <div className="multi-select-header">
                  {locations.length === 0
                    ? "Select institution(s)"
                    : `${locations.length} selected`}
                  <span className="arrow">{menuOpen ? "▲" : "▼"}</span>
                </div>

                {menuOpen && (
                  <div className="multi-select-menu" onClick={(e) => e.stopPropagation()}>
                    <button className="clear-btn" onClick={clearLocations}>
                      Clear Selection
                    </button>

                    {institutions.map(inst => (
                      <label key={inst.name} className="multi-select-item">
                        <input
                          type="checkbox"
                          checked={locations.includes(inst.city)}
                          onChange={() => toggleLocation(inst.city)}
                        />
                        {inst.name} — {inst.city}
                      </label>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Availability */}
            <div className="checkbox-group">
              <input
                type="checkbox"
                id="availableOnly"
                checked={availableOnly}
                onChange={(e) => setAvailableOnly(e.target.checked)}
              />
              <label htmlFor="availableOnly">Show only available equipment</label>
            </div>

            <button type="submit" className="search-btn">Search</button>
          </form>

          {/* Results */}
          {loading && <p>Loading...</p>}

          {!loading && results.length > 0 && (
            <div className="results-grid">
              {results.map(item => (
                <div key={item.equipment_id} className="equipment-card">
                  <h3>{item.name}</h3>
                  <p>{item.description}</p>
                  <p><strong>Institution:</strong> {item.institution_name}</p>
                  <p><strong>City:</strong> {item.city}</p>
                  <p><strong>Availability:</strong> {item.availability}</p>
                </div>
              ))}
            </div>
          )}

          {!loading && results.length === 0 && (
            <p>No results yet — try searching!</p>
          )}
        </div>
      </main>
    </div>
  );
}

export default Equipment;
