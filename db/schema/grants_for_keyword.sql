-- Written by Owen Leitzell

CREATE TABLE grants_for_keyword (
    grant_id        CHAR(36)    NOT NULL,
    name            VARCHAR(64) NOT NULL,

    PRIMARY KEY (name, grant_id),

    FOREIGN KEY (name)
        REFERENCES keyword(name)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY(grant_id)
        REFERENCES grants(grant_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);