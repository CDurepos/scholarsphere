DELIMITER $$

/**
 * Retrieves all session records from the database.
 * 
 * Returns all records from the session table.
 * 
 * @returns Result set containing:
 *   - session_id: UUID of the session
 *   - faculty_id: UUID of the faculty member
 *   - token_hash: SHA-256 hash of the refresh token
 *   - created_at: When the session was created
 *   - expires_at: When the session expires
 *   - revoked: Whether the session has been revoked
 * 
 * Results are ordered by created_at descending (most recent first).
 */
DROP PROCEDURE IF EXISTS read_session;
CREATE PROCEDURE read_session()
BEGIN
    SELECT 
        session_id,
        faculty_id,
        token_hash,
        created_at,
        expires_at,
        revoked
    FROM session
    ORDER BY created_at DESC;
END $$

DELIMITER ;

