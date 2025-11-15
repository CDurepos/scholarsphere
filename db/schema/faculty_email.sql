CREATE TABLE IF NOT EXISTS faculty_email (
    faculty_id CHAR(36) NOT NULL,
    email VARCHAR(255),

    PRIMARY KEY (faculty_id, email),
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE

    CHECK (email IS NULL OR email LIKE '%_@__%.__%')
);