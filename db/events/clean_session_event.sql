DELIMITER $$

/**
 * Scheduled event to automatically clean up expired and old revoked sessions.
 * 
 * This event runs periodically to remove:
 *   - All sessions that have passed their expiration date
 *   - All revoked sessions older than 30 days (for audit trail retention)
 * 
 * This helps maintain the database by automatically removing sessions that are
 * no longer valid or needed for auditing purposes.
 * 
 * The event is scheduled to run daily at 2:00 AM UTC.
 * 
 * Note: Events require the MySQL event scheduler to be enabled.
 * Enable with: SET GLOBAL event_scheduler = ON;
 */
DROP EVENT IF EXISTS clean_session_event$$

CREATE EVENT clean_session_event
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE + INTERVAL 1 DAY + INTERVAL 2 HOUR
ON COMPLETION PRESERVE
ENABLE
COMMENT 'Automatically cleans up expired and old revoked sessions daily'
DO
BEGIN
    -- Call the cleanup procedure to delete expired sessions and old revoked sessions
    CALL clean_session();
END $$

DELIMITER ;

