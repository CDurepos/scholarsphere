DELIMITER $$

/**
 * Updates session records based on identifier and optional fields.
 * 
 * This unified procedure allows updating any session field(s) by identifying
 * the session(s) using one of: session_id, token_hash, or faculty_id.
 * 
 * At least one identifier must be provided. If multiple identifiers are provided,
 * they are combined with AND logic (most specific match).
 * 
 * @param p_session_id    Optional UUID of the specific session to update
 * @param p_token_hash    Optional SHA-256 hash of the refresh token (64 characters)
 * @param p_faculty_id    Optional UUID of the faculty member (updates all their sessions)
 * @param p_revoked       Optional boolean value for the revoked flag
 * @param p_expires_at    Optional datetime value for the expiration time
 * 
 * @returns No result set. Use read procedures to verify the update.
 * 
 * @throws SQLSTATE '45000' if no identifier is provided
 * @throws SQLSTATE '45000' if no fields to update are provided
 */
DROP PROCEDURE IF EXISTS update_session;
CREATE PROCEDURE update_session(
    IN p_session_id CHAR(36),
    IN p_token_hash VARCHAR(64),
    IN p_faculty_id CHAR(36),
    IN p_revoked BOOLEAN,
    IN p_expires_at DATETIME
)
BEGIN
    -- Validate that at least one identifier is provided
    IF p_session_id IS NULL AND p_token_hash IS NULL AND p_faculty_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'At least one identifier (session_id, token_hash, or faculty_id) is required';
    END IF;

    -- Validate that at least one field to update is provided
    IF p_revoked IS NULL AND p_expires_at IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'At least one field to update (revoked or expires_at) is required';
    END IF;

    -- Update session(s) based on provided identifiers and fields
    UPDATE session
    SET 
        revoked = IF(p_revoked IS NOT NULL, p_revoked, revoked),
        expires_at = IF(p_expires_at IS NOT NULL, p_expires_at, expires_at)
    WHERE 
        (p_session_id IS NULL OR session_id = p_session_id)
        AND (p_token_hash IS NULL OR token_hash = p_token_hash)
        AND (p_faculty_id IS NULL OR faculty_id = p_faculty_id);
END $$

DELIMITER ;
