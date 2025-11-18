DELIMITER $$

/**
 * Retrieves all grants granted to a specific faculty member.
 * 
 * Returns all grant records associated with the specified faculty member
 * through the grants_granted_to_faculty join table. Includes a derived
 * status field indicating whether the grant is active, expired, or upcoming.
 * 
 * @param p_faculty_id  Required UUID of the faculty member
 * 
 * @returns Result set containing all columns from the grants table plus:
 *   - grant_id
 *   - description
 *   - amount
 *   - start_date
 *   - end_date
 *   - derived_status: Computed status ('Active', 'Expired', or 'Upcoming')
 * 
 * Results are ordered by start_date (oldest first).
 * 
 * @throws SQLSTATE '45000' if faculty_id is NULL
 */
DROP PROCEDURE IF EXISTS read_grants_granted_to_faculty;
CREATE PROCEDURE read_grants_granted_to_faculty(
    IN p_faculty_id     CHAR(36)
)
BEGIN
    -- Validate that faculty_id is provided
    IF p_faculty_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id is required';
    END IF;
    SELECT  g.*,
            grants_status(g.start_date, g.end_date) AS derived_status
    FROM    grants AS g
    JOIN    grants_granted_to_faculty AS ggf
            ON g.grant_id = ggf.grant_id
    WHERE
            ggf.faculty_id = p_faculty_id
    ORDER BY g.start_date;
END $$
DELIMITER ;
