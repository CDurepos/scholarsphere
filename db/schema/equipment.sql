-- Equipment schema
CREATE TABLE equipment (
    eq_id CHAR(36) PRIMARY KEY
    name VARCHAR(64) NOT NULL,
    description TEXT,
    availability TEXT NOT NULL,

    -- Each Equipment must belong to exactly one Institution
    institution_id UUID NOT NULL,
    FOREIGN KEY (institution_id)
        REFERENCES Institution(institution_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
