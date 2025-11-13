CREATE TABLE grants_provided_by_institution (
    grant_id       CHAR(36) NOT NULL,
    institution_id CHAR(36) NOT NULL,

    PRIMARY KEY (grant_id, institution_id),

    FOREIGN KEY (grant_id)
        REFERENCES grants (grant_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (institution_id)
        REFERENCES institution (institution_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
