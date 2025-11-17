DELIMITER $$

/**
 * Retrieves all research keywords associated with a faculty member.
 * 
 * Returns all keyword names that the specified faculty member researches.
 * This shows the research interests/areas for the faculty member.
 * 
 * @param p_faculty_id  Required UUID of the faculty member
 * 
 * @returns Result set containing:
 *   - name: Keyword name (max 64 characters)
 *   (Multiple rows if the faculty member researches multiple keywords)
 * 
 * @throws SQLSTATE '45000' if faculty_id is NULL
 */
CREATE PROCEDURE read_faculty_keyword(
    IN p_faculty_id CHAR(36)
)
BEGIN
    IF p_faculty_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id is required';
    END IF;

    SELECT name
    FROM faculty_researches_keyword
    WHERE faculty_id = p_faculty_id;
END $$