DELIMITER $$

/**
 * Deletes a publication-keyword association from the database.
 * 
 * Removes a specific publication_explores_keyword relationship, disassociating
 * a keyword from a publication. This does not delete the publication or the
 * keyword, only the association between them.
 * 
 * @param p_publication_id  Required UUID of the publication
 * @param p_name            Required keyword name to disassociate
 * 
 * @returns No result set. Use read procedures to verify the deletion.
 * 
 * @throws SQLSTATE '45000' if publication_id or keyword name is NULL
 */
CREATE PROCEDURE delete_publication_explores_keyword(
    IN p_publication_id CHAR(36),
    IN p_name VARCHAR(64)
)
BEGIN
    IF p_publication_id IS NULL OR p_name IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'publication_id and keyword name are required for delete_publication_explores_keyword';
    END IF;

    DELETE FROM publication_explores_keyword
    WHERE publication_id = p_publication_id
      AND name = p_name;
END $$