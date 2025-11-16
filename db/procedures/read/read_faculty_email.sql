DELIMITER $$

/**
 * Retrieves all email addresses associated with a faculty member.
 * 
 * Returns all email records for the specified faculty member. Since
 * faculty members can have multiple email addresses, this may return
 * multiple rows.
 * 
 * @param p_faculty_id  Required UUID of the faculty member
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the faculty member
 *   - email: One email address associated with the faculty member
 *   (Multiple rows if the faculty member has multiple email addresses)
 */
CREATE PROCEDURE read_faculty_email (
    IN p_faculty_id CHAR(36)
)
BEGIN
    -- Retrieve all email addresses for the specified faculty member
    -- Returns multiple rows if the faculty member has multiple email addresses
    -- Each row represents one email address association
    SELECT faculty_id, email
    FROM faculty_email
    WHERE faculty_id = p_faculty_id;
END$$

DELIMITER ;