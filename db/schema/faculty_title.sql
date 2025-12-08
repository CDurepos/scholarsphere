-- Written by Aidan Bell

CREATE TABLE IF NOT EXISTS faculty_title (
    faculty_id  CHAR(36)        NOT NULL,
    title       VARCHAR(255),

    PRIMARY KEY (faculty_id, title),
    FOREIGN KEY (faculty_id) 
        REFERENCES faculty(faculty_id) 
        ON DELETE CASCADE
        ON UPDATE CASCADE
);