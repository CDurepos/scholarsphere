DELIMITER $$

/**
 * Deletes old faculty keyword generation records.
 * 
 * This workflow procedure removes generation records that are older than
 * a specified datetime threshold. This is useful for maintaining the
 * database by removing records that are no longer relevant for rate limiting
 * purposes (e.g., records older than 1 hour, 1 day, etc.).
 * 
 * @param p_cutoff_datetime  Required datetime threshold
 *                           All records with generated_at older than this
 *                           datetime will be deleted
 * 
 * @returns Result set containing:
 *   - deleted_count: Number of records that were deleted
 *   - cutoff_datetime: The datetime threshold that was used
 *   - action: Status message ('cleaned')
 * 
 * @throws SQLSTATE '45000' if p_cutoff_datetime is NULL
 * 
 * Example usage:
 *   -- Delete all records older than 1 hour
 *   CALL clean_faculty_generates_keyword(DATE_SUB(NOW(), INTERVAL 1 HOUR));
 *   
 *   -- Delete all records older than 1 day
 *   CALL clean_faculty_generates_keyword(DATE_SUB(NOW(), INTERVAL 1 DAY));
 *   
 *   -- Delete all records before a specific date
 *   CALL clean_faculty_generates_keyword('2024-01-01 00:00:00');
 */
DROP PROCEDURE IF EXISTS clean_faculty_generates_keyword;
CREATE PROCEDURE clean_faculty_generates_keyword(
    IN p_cutoff_datetime DATETIME
)
BEGIN
    DECLARE v_deleted_count INT DEFAULT 0;

    -- Validate that cutoff datetime is provided
    IF p_cutoff_datetime IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'cutoff_datetime is required for clean_faculty_generates_keyword';
    END IF;

    -- Delete records older than the cutoff datetime
    DELETE FROM faculty_generates_keyword
    WHERE generated_at < p_cutoff_datetime;

    -- Get the count of deleted records
    SET v_deleted_count = ROW_COUNT();

    -- Return summary of the cleanup operation
    SELECT 
        v_deleted_count AS deleted_count,
        p_cutoff_datetime AS cutoff_datetime,
        'cleaned' AS action;
END $$

DELIMITER ;

