-- Institution schema
CREATE TABLE Institution (
    institution_id CHAR(36) PRIMARY KEY,
    name VARCHAR(256) NOT NULL,

    -- Location composite attributes
    street_addr VARCHAR(128),
    city VARCHAR(64),
    state VARCHAR(64),
    country VARCHAR(64) NOT NULL,
    zip VARCHAR(16),

    website_url VARCHAR(64),
    type VARCHAR(32),

    -- Constraints
    CHECK (zip ~ '^[0-9]{5}$' OR zip IS NULL)
);
