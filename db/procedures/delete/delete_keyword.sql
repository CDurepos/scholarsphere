DELIMITER $$

/**
 * Deletes a keyword record from the database.
 * 
 * Removes the keyword record identified by the provided name. This operation
 * may cascade delete related records (e.g., faculty_researches_keyword,
 * publication_explores_keyword, grants_for_keyword) depending on foreign key
 * constraints configured in the database schema.
 * 
 * @param p_name  Required keyword name to delete
 * 
 * @returns No result set. Use read procedures to verify the deletion.
 * 
 * @throws SQLSTATE '45000' if keyword name is NULL
 */
CREATE PROCEDURE delete_keyword(
    IN p_name VARCHAR(64)
)
BEGIN
    IF p_name IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'keyword name is required for delete_keyword';
    END IF;

    DELETE FROM keyword
    WHERE name = p_name;
END $$
DELIMITER ;
