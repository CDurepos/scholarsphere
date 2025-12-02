DELIMITER $$

/**
 * Retrieves all email records from the database.
 * 
 * Returns all records from the faculty_email table.
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the faculty member
 *   - email: Email address
 * 
 * Results are ordered by faculty_id, then email.
 */
DROP PROCEDURE IF EXISTS read_faculty_email;
CREATE PROCEDURE read_faculty_email()
BEGIN
    SELECT faculty_id, email
    FROM faculty_email
    ORDER BY faculty_id, email;
END $$

DELIMITER ;

