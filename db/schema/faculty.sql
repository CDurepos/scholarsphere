CREATE TABLE IF NOT EXISTS faculty (
    faculty_id          CHAR(36)        PRIMARY KEY,
    
    -- Keep first name `NOT NULL` to ensure some info is stored for any instance
    first_name          VARCHAR(128)    NOT NULL,
    last_name           VARCHAR(128),
    biography           VARCHAR(2048),
    orcid               CHAR(19),
    google_scholar_url  VARCHAR(255),
    research_gate_url   VARCHAR(255),

    -- Store URLs we retrieved a users info from
    -- Better transparency with users
    scraped_from        VARCHAR(255),
    
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