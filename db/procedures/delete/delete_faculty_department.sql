DELIMITER $$

/**
 * Removes a specific department association from a faculty member.
 * 
 * Deletes a department association for the specified faculty member. Both
 * faculty_id and department_name must be provided to uniquely identify which
 * department record to remove, since faculty members can belong to multiple
 * departments.
 * 
 * @param p_faculty_id      Required UUID of the faculty member
 * @param p_department_name Required department name to remove
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the faculty member
 *   - department_name: The department name that was deleted
 *   - action: Status message ('deleted')
 * 
 * @throws SQLSTATE '45000' if faculty_id or department_name is NULL, or if no matching record exists
 */
CREATE PROCEDURE delete_faculty_department (
    IN p_faculty_id CHAR(36),
    IN p_department_name VARCHAR(128)
)
BEGIN
    -- Validate that both required parameters are provided
    IF p_faculty_id IS NULL OR p_department_name IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id and department_name are required.';
    END IF;

    -- Delete the specific department association
    -- Both faculty_id AND department_name are required in WHERE clause to uniquely
    -- identify which department to remove (since faculty can belong to multiple departments)
    DELETE FROM faculty_department
    WHERE faculty_id = p_faculty_id
      AND department_name = p_department_name;

    -- Check if any rows were actually deleted
    -- ROW_COUNT() returns 0 if no matching record was found
    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No matching faculty/department entry to delete.';
    END IF;

    -- Return confirmation of what was deleted
    SELECT p_faculty_id AS faculty_id,
           p_department_name AS department_name,
           'deleted' AS action;
END $$

DELIMITER ;