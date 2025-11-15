CREATE TABLE grants_for_keywords (
    grant_id        CHAR(36)    NOT NULL,
    name            VARCHAR(64) NOT NULL,

    PRIMARY KEY (name, grant_id),

    FOREIGN KEY (name)
        REFRENCES keywords(name)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY(grant_id)
        REFRENCES grants(grant_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
)