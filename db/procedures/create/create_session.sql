DELIMITER $$

/**
 * Creates a new session record in the database.
 * 
 * Inserts a new session with a hashed refresh token for long-term authentication.
 * Sessions are used to maintain user login state across browser sessions.
 * The refresh token is hashed using SHA-256 before storage for security.
 * 
 * @param p_session_id    Required UUID for the session record
 * @param p_faculty_id    Required UUID of the faculty member
 * @param p_token_hash     Required SHA-256 hash of the refresh token (64 characters)
 * @param p_expires_at     Required expiration datetime for the session
 * 
 * @returns No result set. Use read procedures to verify the insert.
 * 
 * @throws SQLSTATE '23000' if session_id or token_hash already exists (unique constraint)
 * @throws SQLSTATE '23000' if faculty_id doesn't exist (foreign key constraint)
 */
DROP PROCEDURE IF EXISTS create_session;
CREATE PROCEDURE create_session(
    IN p_session_id CHAR(36),
    IN p_faculty_id CHAR(36),
    IN p_token_hash VARCHAR(64),
    IN p_expires_at DATETIME
)
BEGIN
    -- Validate required fields
    IF p_session_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'session_id is required';
    END IF;

    IF p_faculty_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id is required';
    END IF;

    IF p_token_hash IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'token_hash is required';
    END IF;

    IF p_expires_at IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'expires_at is required';
    END IF;

    -- Insert session record
    INSERT INTO session (
        session_id,
        faculty_id,
        token_hash,
        created_at,
        expires_at,
        revoked
    )
    VALUES (
        p_session_id,
        p_faculty_id,
        p_token_hash,
        UTC_TIMESTAMP(),
        p_expires_at,
        FALSE
    );
END $$

DELIMITER ;

