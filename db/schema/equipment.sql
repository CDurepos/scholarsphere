-- Equipment schema
CREATE TABLE Equipment (
    eq_id UUID PRIMARY KEY NOT NULL UNIQUE,
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
