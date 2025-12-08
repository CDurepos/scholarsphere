-- Written by Clayton Durepos, Aidan Bell

DELIMITER $$

/**
 * Retrieves all active sessions for a given faculty member.
 * 
 * Returns all non-revoked, non-expired sessions for the specified faculty member.
 * 
 * @param p_faculty_id  Required UUID of the faculty member
 * 
 * @returns Result set containing:
 *   - session_id: UUID of the session
 *   - faculty_id: UUID of the faculty member
 *   - created_at: When the session was created
 *   - expires_at: When the session expires
 *   - revoked: Whether the session has been revoked
 * 
 * Results are ordered by created_at descending (most recent first).
 * 
 * @throws SQLSTATE '45000' if faculty_id is NULL
 */
DROP PROCEDURE IF EXISTS read_session_by_faculty$$
CREATE PROCEDURE read_session_by_faculty(
    IN p_faculty_id CHAR(36)
)
BEGIN
    IF p_faculty_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id is required';
    END IF;

    SELECT 
        session_id,
        faculty_id,
        created_at,
        expires_at,
        revoked
    FROM session
    WHERE faculty_id = p_faculty_id
        AND revoked = FALSE
        AND expires_at > UTC_TIMESTAMP()
    ORDER BY created_at DESC;
END $$

DELIMITER ;

