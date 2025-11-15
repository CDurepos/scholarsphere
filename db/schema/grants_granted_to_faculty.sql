CREATE TABLE grants_granted_to_faculty (
    grant_id        CHAR(36)    NOT NULL,
    faculty_id      CHAR(36)    NOT NULL,

    PRIMARY KEY (grant_id, faculty_id),

    FOREIGN KEY (grant_id)
        REFERENCES grants (grant_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (faculty_id)
        REFERENCES faculty (faculty_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
