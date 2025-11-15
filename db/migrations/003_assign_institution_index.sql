-- Index on institution name for faster lookup
CREATE INDEX idx_institution_name ON Institution(name);

-- Index on city and state for regional searches
CREATE INDEX idx_institution_city_state ON Institution(city, state);

-- Index on zip code for a more specific location lookup
CREATE INDEX idx_institution_zip ON Institution(zip);
