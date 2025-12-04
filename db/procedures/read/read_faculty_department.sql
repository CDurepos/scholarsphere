DELIMITER $$

/**
 * Retrieves all department records from the database.
 * 
 * Returns all records from the faculty_department table.
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the faculty member
 *   - department_name: Department name
 * 
 * Results are ordered by faculty_id, then department_name.
 */
DROP PROCEDURE IF EXISTS read_faculty_department$$
CREATE PROCEDURE read_faculty_department()
BEGIN
    SELECT faculty_id, department_name
    FROM faculty_department
    ORDER BY faculty_id, department_name;
END $$

DELIMITER ;

