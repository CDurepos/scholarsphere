-- Index on institution name for faster lookup
CREATE INDEX idx_institution_name ON institution(name);

-- Index on city and state for regional searches
CREATE INDEX idx_institution_city_state ON institution(city, state);

-- Index on zip code for a more specific location lookup
CREATE INDEX idx_institution_zip ON institution(zip);
