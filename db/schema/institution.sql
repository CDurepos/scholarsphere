-- Institution schema
CREATE TABLE institution (
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
                        )


    -- Constraints
    CHECK (zip ~ '^[0-9]{5}$' OR zip IS NULL)
);
