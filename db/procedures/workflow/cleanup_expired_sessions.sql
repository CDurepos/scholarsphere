DELIMITER $$

/**
 * Deletes expired sessions from the database.
 * 
 * Removes all sessions that have passed their expiration date.
 * This is a maintenance procedure that should be run periodically.
 * 
 * @returns Result set containing:
 *   - deleted_count: Number of sessions deleted
 */
DROP PROCEDURE IF EXISTS cleanup_expired_sessions;
CREATE PROCEDURE cleanup_expired_sessions()
BEGIN
    DELETE FROM session
    WHERE expires_at < UTC_TIMESTAMP();
    
    SELECT ROW_COUNT() AS deleted_count;
END $$

DELIMITER ;

