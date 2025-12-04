DELIMITER $$

/**
 * Retrieves all departments associated with a faculty member.
 * 
 * Returns all department records for the specified faculty member. Since
 * faculty members can belong to multiple departments, this may return
 * multiple rows.
 * 
 * @param p_faculty_id  Required UUID of the faculty member
 * 
 * @returns Result set containing:
 *   - department_name: One department name associated with the faculty member
 *   (Multiple rows if the faculty member belongs to multiple departments)
 * 
 * @throws SQLSTATE '45000' if faculty_id is NULL
 */
DROP PROCEDURE IF EXISTS read_faculty_department_by_faculty$$
CREATE PROCEDURE read_faculty_department_by_faculty (
    IN p_faculty_id CHAR(36)
)
BEGIN
    -- Validate that faculty_id is provided
    IF p_faculty_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id is required.';
    END IF;

    -- Retrieve all departments for the specified faculty member
    -- Returns multiple rows if the faculty member belongs to multiple departments
    -- Each row represents one department association
    -- Only returns department_name (not faculty_id) since it's already known
    SELECT department_name
    FROM faculty_department
    WHERE faculty_id = p_faculty_id;
END $$

DELIMITER ;