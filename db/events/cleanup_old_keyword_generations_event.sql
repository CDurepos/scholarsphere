DELIMITER $$

/**
 * Scheduled event to automatically clean up old keyword generation records.
 * 
 * This event runs periodically to remove generation records that are older
 * than a specified threshold (default: 1 hour). This helps maintain the database
 * by automatically removing records that are no longer relevant for rate limiting.
 * 
 * The event is scheduled to run every hour.
 * 
 * Note: Events require the MySQL event scheduler to be enabled.
 * Enable with: SET GLOBAL event_scheduler = ON;
 * 
 * To modify the cleanup threshold, edit the DATE_SUB interval below.
 * Current setting: 1 HOUR (deletes records older than 1 hour)
 */
DROP EVENT IF EXISTS cleanup_old_keyword_generations_event;

CREATE EVENT cleanup_old_keyword_generations_event
ON SCHEDULE EVERY 1 HOUR
STARTS CURRENT_TIMESTAMP
ON COMPLETION PRESERVE
ENABLE
COMMENT 'Automatically cleans up old keyword generation records hourly'
DO
BEGIN
    -- Call the cleanup procedure to delete records older than 1 hour
    CALL cleanup_old_keyword_generations(DATE_SUB(NOW(), INTERVAL 1 HOUR));
END $$

DELIMITER ;

