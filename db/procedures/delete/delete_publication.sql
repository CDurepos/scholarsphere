DELIMITER $$

/**
 * Deletes a publication record from the database.
 * 
 * Removes the publication record identified by the provided publication_id.
 * This operation may cascade delete related records (e.g.,
 * publication_authored_by_faculty, publication_explores_keyword) depending
 * on foreign key constraints configured in the database schema.
 * 
 * @param p_id  Required UUID of the publication record to delete
 * 
 * @returns No result set. Use read procedures to verify the deletion.
 * 
 * @throws SQLSTATE '45000' if publication_id is NULL
 */
CREATE PROCEDURE delete_author_publication(
    IN p_id CHAR(36)
)
BEGIN
    IF p_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'publication_id is required for delete_author_publication';
    END IF;

    DELETE FROM publication
    WHERE publication_id = p_id;
END $$

DELIMITER ;
