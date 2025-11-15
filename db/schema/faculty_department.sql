CREATE TABLE IF NOT EXISTS faculty_department (
    faculty_id CHAR(36) NOT NULL,
    department_name VARCHAR(100),

    PRIMARY KEY (faculty_id, department_name),
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE
);