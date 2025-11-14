CREATE TABLE grants_organization (
    grant_id       CHAR(36) NOT NULL,
    name           VARCHAR(256) NOT NULL,
    PRIMARY KEY (grant_id),

    FOREIGN KEY (grant_id)
        REFERENCES grants (grant_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
