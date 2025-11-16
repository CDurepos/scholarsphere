-- Index on last name and first name, and department name for faster search functionality
CREATE INDEX idx_faculty_last_first_name ON faculty(last_name, first_name);
CREATE INDEX idx_faculty_department_dept_name ON faculty_department(department_name);