DELIMITER $$

/**
 * Updates an existing faculty keyword generation record.
 * 
 * Allows updating the timestamp of a generation record. This is useful
 * if you need to correct or adjust when a generation request was recorded.
 * 
 * @param p_generation_id  Required UUID of the generation record to update
 * @param p_generated_at   Optional new timestamp (NULL to keep existing)
 * 
 * @returns Result set containing:
 *   - generation_id: UUID of the updated generation record
 *   - action: Status message ('updated')
 * 
 * @throws SQLSTATE '45000' if generation_id is NULL or doesn't exist
 */
CREATE PROCEDURE update_faculty_generates_keyword(
    IN p_generation_id CHAR(36),
    IN p_generated_at DATETIME
)
BEGIN
    -- Variable to check if the generation record exists
    DECLARE existing_count INT;

    -- Validate that generation_id is provided and not empty
    IF p_generation_id IS NULL OR TRIM(p_generation_id) = '' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'generation_id is required for update_faculty_generates_keyword';
    END IF;

    -- Verify that the generation record exists before attempting update
    SELECT COUNT(*) INTO existing_count
    FROM faculty_generates_keyword
    WHERE generation_id = p_generation_id;

    IF existing_count = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'generation_id does not exist';
    END IF;

    -- Perform partial update using COALESCE
    -- If p_generated_at is NULL, keep existing value
    UPDATE faculty_generates_keyword
    SET generated_at = COALESCE(p_generated_at, generated_at)
    WHERE generation_id = p_generation_id;

    -- Return confirmation of the update
    SELECT p_generation_id AS generation_id, 'updated' AS action;
END $$

DELIMITER ;

