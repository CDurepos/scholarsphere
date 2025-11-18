DELIMITER $$

/**
 * Deletes a faculty-keyword research association from the database.
 * 
 * Removes a specific faculty_researches_keyword relationship, disassociating
 * a keyword from a faculty member's research interests. This does not delete
 * the faculty member or the keyword, only the association between them.
 * 
 * @param p_faculty_id  Required UUID of the faculty member
 * @param p_name        Required keyword name to disassociate
 * 
 * @returns No result set. Use read procedures to verify the deletion.
 * 
 * @throws SQLSTATE '45000' if faculty_id or keyword name is NULL
 */
CREATE PROCEDURE delete_faculty_researches_keyword(
    IN p_faculty_id CHAR(36),
    IN p_name VARCHAR(64)
)
BEGIN
    IF p_faculty_id IS NULL OR p_name IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id and keyword name are required for delete_faculty_researches_keyword';
    END IF;

    DELETE FROM faculty_researches_keyword
    WHERE faculty_id = p_faculty_id
      AND name = p_name;
END $$

DELIMITER ;
