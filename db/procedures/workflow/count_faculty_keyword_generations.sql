DELIMITER $$

/**
 * Counts keyword generation records for a faculty member after a specified datetime.
 * 
 * This workflow procedure is used for rate limiting by checking how many times
 * a faculty member has requested keyword generation within a specific time period.
 * Returns the count of records where generated_at is greater than or equal to
 * the provided datetime threshold.
 * 
 * @param p_faculty_id      Required UUID of the faculty member to check
 * @param p_since_datetime  Required datetime threshold
 *                          Counts all records with generated_at >= this datetime
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the faculty member
 *   - generation_count: Number of generation records since the datetime
 *   - since_datetime: The datetime threshold that was used
 * 
 * @throws SQLSTATE '45000' if p_faculty_id or p_since_datetime is NULL
 * 
 * Example usage:
 *   -- Count generations in the last hour
 *   CALL count_faculty_keyword_generations('faculty-uuid', DATE_SUB(NOW(), INTERVAL 1 HOUR));
 *   
 *   -- Count generations in the last 24 hours
 *   CALL count_faculty_keyword_generations('faculty-uuid', DATE_SUB(NOW(), INTERVAL 24 HOUR));
 *   
 *   -- Count generations since a specific date
 *   CALL count_faculty_keyword_generations('faculty-uuid', '2024-01-01 00:00:00');
 */
CREATE PROCEDURE count_faculty_keyword_generations(
    IN p_faculty_id CHAR(36),
    IN p_since_datetime DATETIME,
    OUT p_generation_count INT
)
BEGIN
    -- Validate required parameters
    IF p_faculty_id IS NULL OR TRIM(p_faculty_id) = '' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id is required for count_faculty_keyword_generations';
    END IF;

    IF p_since_datetime IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'since_datetime is required for count_faculty_keyword_generations';
    END IF;

    -- Count records for this faculty member generated at or after the datetime threshold
    SELECT COUNT(*) INTO p_generation_count
    FROM faculty_generates_keyword
    WHERE faculty_id = p_faculty_id
      AND generated_at >= p_since_datetime;
END $$

DELIMITER ;

