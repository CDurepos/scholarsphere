DELIMITER $$

/**
 * Updates a specific department association for a faculty member.
 * 
 * Changes an existing department name to a new value. Both the old department
 * name and new department name must be specified to uniquely identify which
 * department record to update, since faculty members can belong to multiple
 * departments.
 * 
 * @param p_faculty_id          Required UUID of the faculty member
 * @param p_old_department_name Required current department name to be changed
 * @param p_new_department_name Required new department name value
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the faculty member
 *   - old_department: The previous department name
 *   - new_department: The new department name
 *   - action: Status message ('updated')
 * 
 * @throws SQLSTATE '45000' if any parameter is NULL or if no matching record exists
 */
CREATE PROCEDURE update_faculty_department (
    IN p_faculty_id CHAR(36),
    IN p_old_department_name VARCHAR(128),
    IN p_new_department_name VARCHAR(128)
)
BEGIN
    -- Validate that all required parameters are provided
    IF p_faculty_id IS NULL
       OR p_old_department_name IS NULL
       OR p_new_department_name IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id, old department, and new department are required.';
    END IF;

    -- Update the specific department association
    -- Both faculty_id AND old_department_name are needed in WHERE clause because
    -- a faculty member can belong to multiple departments, so we identify which one to change
    UPDATE faculty_department
    SET department_name = p_new_department_name
    WHERE faculty_id = p_faculty_id
      AND department_name = p_old_department_name;

    -- Check if any rows were actually updated
    -- ROW_COUNT() returns 0 if no matching record was found
    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No matching faculty/department entry to update.';
    END IF;

    -- Return confirmation showing both old and new department names
    SELECT p_faculty_id AS faculty_id,
           p_old_department_name AS old_department,
           p_new_department_name AS new_department,
           'updated' AS action;
END $$

DELIMITER ;