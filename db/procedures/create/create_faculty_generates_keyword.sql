DELIMITER $$

/**
 * Creates a new faculty keyword generation record.
 * 
 * Inserts a record tracking when a faculty member requested keyword generation
 * using an LLM. This is used to enforce rate limiting on LLM usage.
 * 
 * @param p_generation_id  Required UUID for the generation record
 * @param p_faculty_id     Required UUID of the faculty member making the request
 *                         Must reference an existing faculty record
 * @param p_generated_at   Optional timestamp of when the request was made
 *                         If NULL, uses current timestamp
 * 
 * @returns No result set. Use read procedures to verify the insert.
 * 
* @throws SQLSTATE '45000' if generation_id or faculty_id is NULL
 */
CREATE PROCEDURE create_faculty_generates_keyword(
    IN p_generation_id CHAR(36),
    IN p_faculty_id CHAR(36),
    IN p_generated_at DATETIME
)
BEGIN
    -- Validate required parameters
    IF p_generation_id IS NULL OR TRIM(p_generation_id) = '' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'generation_id is required for create_faculty_generates_keyword';
    END IF;

    IF p_faculty_id IS NULL OR TRIM(p_faculty_id) = '' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id is required for create_faculty_generates_keyword';
    END IF;

    -- Insert record, using current timestamp if p_generated_at is NULL
    INSERT INTO faculty_generates_keyword (generation_id, faculty_id, generated_at)
    VALUES (p_generation_id, p_faculty_id, COALESCE(p_generated_at, NOW()));
END $$

DELIMITER ;

