DELIMITER $$

/**
 * Associates a department with a faculty member.
 * 
 * Inserts a new department association for the specified faculty member.
 * Faculty members can belong to multiple departments, so this creates an
 * additional department association rather than replacing existing ones.
 * 
 * @param p_faculty_id      Required UUID of the faculty member
 * @param p_department_name Required name of the department
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the faculty member
 *   - department_name: The department name that was inserted
 *   - action: Status message ('inserted')
 * 
 * @throws SQLSTATE '45000' if faculty_id or department_name is NULL
 */
CREATE PROCEDURE insert_faculty_department (
    IN p_faculty_id CHAR(36),
    IN p_department_name VARCHAR(128)
)
BEGIN
    -- Validate that both required parameters are provided
    IF p_faculty_id IS NULL OR p_department_name IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id and department_name are required.';
    END IF;

    -- Insert a new department association for the faculty member
    -- Faculty can belong to multiple departments (e.g., joint appointments)
    -- The combination of faculty_id and department_name should be unique
    INSERT INTO faculty_department (faculty_id, department_name)
    VALUES (p_faculty_id, p_department_name);

    -- Return confirmation with the inserted values
    SELECT p_faculty_id AS faculty_id,
           p_department_name AS department_name,
           'inserted' AS action;
END $$

DELIMITER ;