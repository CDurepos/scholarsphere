-- Written by Aidan Bell

CREATE TABLE IF NOT EXISTS faculty_department (
    faculty_id      CHAR(36)        NOT NULL,
    department_name VARCHAR(128),

    PRIMARY KEY (faculty_id, department_name),

    FOREIGN KEY (faculty_id) 
        REFERENCES faculty(faculty_id) 
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    -- Index on department name for faster search functionality
    INDEX idx_faculty_department_dept_name (department_name)
);