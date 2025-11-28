DELIMITER $$

/**
 * Retrieves faculty keyword generation records.
 * 
 * Fetches records of when faculty members requested keyword generation.
 * Can filter by faculty_id and optionally by time range for rate limiting checks.
 * 
 * @param p_generation_id  Optional UUID of a specific generation record to retrieve
 *                         If provided, returns only that record
 * @param p_faculty_id     Optional UUID of the faculty member
 *                         If provided, returns all generation records for that faculty
 * @param p_start_date     Optional start date for filtering by time range
 *                         If provided with p_end_date, returns records within range
 * @param p_end_date       Optional end date for filtering by time range
 *                         If provided with p_start_date, returns records within range
 * 
 * @returns Result set containing:
 *   - generation_id: UUID of the generation record
 *   - faculty_id: UUID of the faculty member
 *   - generated_at: Timestamp when the request was made
 * 
 * If both p_generation_id and p_faculty_id are NULL, returns an error.
 * Results are ordered by generated_at descending (most recent first).
 */
CREATE PROCEDURE read_faculty_generates_keyword(
    IN p_generation_id CHAR(36),
    IN p_faculty_id CHAR(36),
    IN p_start_date DATETIME,
    IN p_end_date DATETIME
)
BEGIN

    IF p_generation_id IS NULL AND p_faculty_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Either generation_id or faculty_id must be provided for read_faculty_generates_keyword';
    END IF;

    SELECT 
        generation_id,
        faculty_id,
        generated_at
    FROM faculty_generates_keyword
    WHERE 
        (p_generation_id IS NULL OR generation_id = p_generation_id)
        AND (p_faculty_id IS NULL OR faculty_id = p_faculty_id)
        AND (p_start_date IS NULL OR generated_at >= p_start_date)
        AND (p_end_date IS NULL OR generated_at <= p_end_date)
    ORDER BY generated_at DESC;
END $$

DELIMITER ;

