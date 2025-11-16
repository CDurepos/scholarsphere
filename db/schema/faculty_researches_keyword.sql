CREATE TABLE faculty_researches_keyword (
    name        VARCHAR(64)     NOT NULL,
    faculty_id     CHAR(36)     NOT NULL,

    PRIMARY KEY (name, faculty_id),

    FOREIGN KEY (name)
        REFERENCES keyword(name)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (faculty_id)
        REFERENCES faculty(faculty_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
