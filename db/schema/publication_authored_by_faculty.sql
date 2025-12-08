CREATE TABLE IF NOT EXISTS publication_authored_by_faculty (
    faculty_id         CHAR(36)    NOT NULL,
    publication_id  CHAR(36)    NOT NULL,

    PRIMARY KEY (faculty_id, publication_id),

    FOREIGN KEY (faculty_id)
        REFERENCES faculty(faculty_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    FOREIGN KEY (publication_id)
        REFERENCES publication(publication_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    -- Index on publication_id for joins from publication side (keyword searches)
    INDEX idx_pabf_publication_id (publication_id)
);
