DELIMITER $$

/**
 * Deletes expired and old revoked sessions from the database.
 * 
 * Removes:
 *   - All sessions that have passed their expiration date
 *   - All revoked sessions older than 30 days (for audit trail retention)
 * 
 * This is a maintenance procedure that should be run periodically.
 * 
 * @returns Result set containing:
 *   - deleted_count: Number of sessions deleted
 */
DROP PROCEDURE IF EXISTS clean_session$$
CREATE PROCEDURE clean_session()
BEGIN
    DELETE FROM session
    WHERE expires_at < UTC_TIMESTAMP()
       OR (revoked = TRUE AND created_at < DATE_SUB(UTC_TIMESTAMP(), INTERVAL 30 DAY));
    
    SELECT ROW_COUNT() AS deleted_count;
END $$

DELIMITER ;

