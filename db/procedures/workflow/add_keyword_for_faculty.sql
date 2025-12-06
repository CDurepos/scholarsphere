DELIMITER $$

/**
 * Adds a keyword and associates it with a faculty member.
 * 
 * This workflow procedure:
 * 1. Normalizes the keyword name to lowercase for comparison
 * 2. Checks if the keyword already exists (case-insensitive)
 * 3. Creates the keyword if it doesn't exist
 * 4. Links the keyword to the specified faculty member via the join table
 * 
 * Keywords are normalized to lowercase to ensure "NLP" and "nlp" are treated
 * as the same keyword. The keyword is stored in lowercase in the database.
 * 
 * @param p_faculty_id    Required UUID of the faculty member
 * @param p_name          Required keyword name (max 64 characters, will be normalized to lowercase)
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the associated faculty member
 *   - keyword_name: The normalized keyword name that was used
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
    DECLARE v_normalized_name VARCHAR(64);
    DECLARE v_existing_name VARCHAR(64);
    DECLARE v_action VARCHAR(20);
    
    -- Validate input
    IF p_faculty_id IS NULL OR p_name IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id and keyword name are required.';
    END IF;

    -- Normalize keyword to lowercase for comparison and storage
    SET v_normalized_name = LOWER(TRIM(p_name));
    
    -- Check if keyword already exists (case-insensitive)
    SELECT name INTO v_existing_name
    FROM keyword
    WHERE LOWER(name) = v_normalized_name
    LIMIT 1;
    
    -- If keyword doesn't exist, create it
    IF v_existing_name IS NULL THEN
        INSERT INTO keyword (name)
        VALUES (v_normalized_name)
        ON DUPLICATE KEY UPDATE name = name; -- Handle race condition
        SET v_action = 'inserted';
    ELSE
        -- Use the existing keyword name (preserve original casing if different)
        SET v_normalized_name = v_existing_name;
        SET v_action = 'linked';
    END IF;

    -- Link the keyword to the faculty member (using normalized name)
    INSERT INTO faculty_researches_keyword (faculty_id, name)
    VALUES (p_faculty_id, v_normalized_name)
    ON DUPLICATE KEY UPDATE name = name; -- Ignore if relationship already exists

    -- Return confirmation
    SELECT 
        p_faculty_id AS faculty_id,
        v_normalized_name AS keyword_name,
        v_action AS action;
END $$
DELIMITER ;