CREATE TABLE IF NOT EXISTS faculty (
    faculty_id CHAR(36) PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    biography VARCHAR(2000),
    research_interest VARCHAR(2000),
    orcid CHAR(19),
    google_scholar_url VARCHAR(255),
    research_gate_url VARCHAR(255),
    scraped_from VARCHAR(255),
    
    CHECK (
        (google_scholar_url IS NULL 
            OR google_scholar_url LIKE 'https://scholar.google.com/%'
            OR google_scholar_url LIKE 'http://scholar.google.com/%')
        AND
        (research_gate_url IS NULL
            OR research_gate_url LIKE 'https://www.researchgate.net/%'
            OR research_gate_url LIKE 'http://www.researchgate.net/%')
    )
);