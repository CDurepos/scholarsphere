CREATE TABLE IF NOT EXISTS faculty_phone (
    faculty_id CHAR(36) NOT NULL,
    phone_num VARCHAR(50),

    PRIMARY KEY (faculty_id, phone_num),
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE
);