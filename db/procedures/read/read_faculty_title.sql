DELIMITER $$

/**
 * Retrieves all titles associated with a faculty member.
 * 
 * Returns all title records for the specified faculty member. Since faculty
 * members can have multiple titles, this may return multiple rows.
 * 
 * @param p_faculty_id  Required UUID of the faculty member
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the faculty member
 *   - title: One title associated with the faculty member
 *   (Multiple rows if the faculty member has multiple titles)
 */
CREATE PROCEDURE read_faculty_title (
    IN p_faculty_id CHAR(36)
)
BEGIN
    -- Retrieve all titles for the specified faculty member
    -- Returns multiple rows if the faculty member has multiple titles
    -- Each row represents one title association
    SELECT faculty_id, title
    FROM faculty_title
    WHERE faculty_id = p_faculty_id;
END$$

DELIMITER ;