CREATE TABLE IF NOT EXISTS faculty_generates_keyword (
    generation_id    CHAR(36)        PRIMARY KEY,
    faculty_id       CHAR(36)        NOT NULL,
    generated_at     DATETIME        NOT NULL,

    FOREIGN KEY (faculty_id)
        REFERENCES faculty(faculty_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

