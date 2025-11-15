-- EQUIPMENT SCH
CREATE TABLE equipment (
    eq_id           CHAR(36)        PRIMARY KEY,
    name            VARCHAR(64)     NOT NULL,

    -- Description of the equipment itself
    description     VARCHAR(2048),

    -- TEXT DEFAULT
    -- Allow for simple phrases `Available,` `Unavailable,` etc.
    -- In addition to descriptive passages...
    -- `Available Mondays 14:00-20:00 ...`
    availability    VARCHAR(2048)            NOT NULL,

    -- Each Equipment must belong to exactly one Institution
    institution_id  CHAR(36)    NOT NULL,
    FOREIGN KEY (institution_id)
        REFERENCES Institution(institution_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
