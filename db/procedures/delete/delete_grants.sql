DELIMITER $$

/**
 * Deletes a grant record from the database.
 * 
 * Removes the grant record identified by the provided grant_id. This operation
 * may cascade delete related records (e.g., grants_granted_to_faculty,
 * grants_for_keyword, grants_organization) depending on foreign key
 * constraints configured in the database schema.
 * 
 * @param p_grant_id  Required UUID of the grant record to delete
 * 
 * @returns No result set. Use read procedures to verify the deletion.
 * 
 * @throws SQLSTATE '45000' if grant_id is NULL
 */
CREATE PROCEDURE delete_grants(
    IN p_grant_id CHAR(36)
)
BEGIN
    IF p_grant_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'grant_id is required for delete_grants';
    END IF;

    DELETE FROM grants
    WHERE grant_id = p_grant_id;
END $$
DELIMITER ;
