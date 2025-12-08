-- Written by Aidan Bell

DELIMITER $$

/**
 * Retrieves all title records from the database.
 * 
 * Returns all records from the faculty_title table.
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the faculty member
 *   - title: Title
 * 
 * Results are ordered by faculty_id, then title.
 */
DROP PROCEDURE IF EXISTS read_faculty_title$$
CREATE PROCEDURE read_faculty_title()
BEGIN
    SELECT faculty_id, title
    FROM faculty_title
    ORDER BY faculty_id, title;
END $$

DELIMITER ;

