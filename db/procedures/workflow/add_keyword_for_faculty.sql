/**
 * Adds a new keyword and associates it with a faculty member.
 * 
 * This workflow procedure combines two operations:
 * 1. Creates a new keyword record
 * 2. Links the keyword to the specified faculty member via the join table
 * 
 * This is a convenience procedure that handles the complete workflow of
 * adding a keyword for a faculty member in a single call.
 * 
 * @param p_faculty_id    Required UUID of the faculty member
 * @param p_name          Required keyword name (max 64 characters)
 * 
 * @returns Result set containing:
 *   - keyword_id: UUID of the newly created keyword
 *   - faculty_id: UUID of the associated faculty member
 *   - action: Status message ('inserted')
 * 
 * @throws SQLSTATE '45000' if faculty_id is NULL
 */
 CREATE PROCEDURE add_keyword_for_faculty(
    IN p_faculty_id CHAR(36),
    IN p_name VARCHAR(64)
)
BEGIN
    -- Validate input: faculty_id must be provided
    IF p_faculty_id IS NULL OR p_name IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id and keyword name are required.';
    END IF;

    -- Step 1: Create the keyword record
    CALL create_keyword(p_name);

    -- Step 2: Link the keyword to the faculty member
    CALL create_faculty_researches_keyword(p_faculty_id, p_name);

    -- Step 3: Return confirmation with both IDs for reference
    SELECT p_faculty_id AS faculty_id,
           p_name AS keyword_id,
           'inserted' AS action;
END $$
DELIMITER ;