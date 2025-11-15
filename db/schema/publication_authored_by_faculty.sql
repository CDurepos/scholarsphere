CREATE TABLE publication_authors (
    faculty_id         CHAR(36)    NOT NULL,
    publication_id  CHAR(36)    NOT NULL,

    PRIMARY KEY (faculty_id, publication_id),

    FOREIGN KEY (faculty_id)
        REFERENCES user(faculty_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    FOREIGN KEY (publication_id)
        REFERENCES Publication(publication_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE

);
