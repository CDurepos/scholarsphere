DELIMITER $$

/**
 * Adds a keyword and associates it with a faculty member.
 * 
 * This workflow procedure:
 * 1. Trims the keyword name
 * 2. Checks if the keyword already exists (case-insensitive)
 * 3. Creates the keyword if it doesn't exist (preserving original casing)
 * 4. Links the keyword to the specified faculty member via the join table
 * 
 * Keywords are matched case-insensitively to ensure "NLP" and "nlp" are treated
 * as the same keyword, but the original casing is preserved when storing new keywords.
 * This allows abbreviations like "NLP" to remain in uppercase.
 * 
 * @param p_faculty_id    Required UUID of the faculty member
 * @param p_name          Required keyword name (max 64 characters, original casing preserved)
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the associated faculty member
 *   - keyword_name: The keyword name that was used (existing or newly created)
 *   - action: Status message ('inserted' or 'linked')
 * 
 * @throws SQLSTATE '45000' if faculty_id or keyword name is NULL
 */
DROP PROCEDURE IF EXISTS add_keyword_for_faculty$$
CREATE PROCEDURE add_keyword_for_faculty(
    IN p_faculty_id CHAR(36),
    IN p_name VARCHAR(64)
)
BEGIN
    DECLARE v_trimmed_name VARCHAR(64);
    DECLARE v_existing_name VARCHAR(64);
    DECLARE v_action VARCHAR(20);
    
    -- Validate input
    IF p_faculty_id IS NULL OR p_name IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id and keyword name are required.';
    END IF;

    -- Trim the keyword name (preserve original casing)
    SET v_trimmed_name = TRIM(p_name);
    
    -- Check if keyword already exists (case-insensitive)
    SELECT name INTO v_existing_name
    FROM keyword
    WHERE LOWER(name) = LOWER(v_trimmed_name)
    LIMIT 1;
    
    -- If keyword doesn't exist, create it with original casing
    IF v_existing_name IS NULL THEN
        INSERT INTO keyword (name)
        VALUES (v_trimmed_name)
        ON DUPLICATE KEY UPDATE name = name; -- Handle race condition
        SET v_action = 'inserted';
        -- Use the trimmed name (original casing)
    ELSE
        -- Use the existing keyword name (preserve existing casing)
        SET v_trimmed_name = v_existing_name;
        SET v_action = 'linked';
    END IF;

    -- Link the keyword to the faculty member
    INSERT INTO faculty_researches_keyword (faculty_id, name)
    VALUES (p_faculty_id, v_trimmed_name)
    ON DUPLICATE KEY UPDATE name = name; -- Ignore if relationship already exists

    -- Return confirmation
    SELECT 
        p_faculty_id AS faculty_id,
        v_trimmed_name AS keyword_name,
        v_action AS action;
END $$
DELIMITER ;