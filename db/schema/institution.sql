-- Written by Abby Pitcairn

-- Institution schema
CREATE TABLE IF NOT EXISTS institution (
    institution_id      CHAR(36)        PRIMARY KEY,
    name                VARCHAR(256)    NOT NULL,

    -- Location composite attributes
    street_addr         VARCHAR(255),
    city                VARCHAR(255),
    state               VARCHAR(255),
    country             VARCHAR(255) NOT NULL,
    zip                 VARCHAR(16),

    website_url         VARCHAR(255),
    type                ENUM(
                            "Public University", 
                            "Private University", 
                            "Community College"
                        ),


    -- Constraints
    CHECK (zip IS NULL OR zip REGEXP '^[0-9]{5}$'),

    -- Index on institution name for faster lookup
    INDEX idx_institution_name (name),

    -- Index on city and state for regional searches
    INDEX idx_institution_city_state (city, state),

    -- Index on zip code for a more specific location lookup
    INDEX idx_institution_zip (zip)
);
