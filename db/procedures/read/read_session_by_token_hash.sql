-- Written by Clayton Durepos, Aidan Bell

DELIMITER $$

/**
 * Retrieves a session record by its token hash.
 * 
 * Returns the session record for a given refresh token hash.
 * Only returns active (non-revoked, non-expired) sessions.
 * 
 * @param p_token_hash  Required SHA-256 hash of the refresh token (64 characters)
 * 
 * @returns Result set containing:
 *   - session_id: UUID of the session
 *   - faculty_id: UUID of the faculty member
 *   - created_at: When the session was created
 *   - expires_at: When the session expires
 *   - revoked: Whether the session has been revoked
 * 
 * @throws SQLSTATE '45000' if token_hash is NULL
 */
DROP PROCEDURE IF EXISTS read_session_by_token_hash$$
CREATE PROCEDURE read_session_by_token_hash(
    IN p_token_hash VARCHAR(64)
)
BEGIN
    IF p_token_hash IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'token_hash is required';
    END IF;

    SELECT 
        session_id,
        faculty_id,
        created_at,
        expires_at,
        revoked
    FROM session
    WHERE token_hash = p_token_hash
        AND revoked = FALSE
        AND expires_at > UTC_TIMESTAMP();
END $$

DELIMITER ;

