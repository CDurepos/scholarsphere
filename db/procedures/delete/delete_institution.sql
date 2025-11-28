DELIMITER $$

/**
 * Deletes an institution record from the database.
 * 
 * Removes the institution record identified by the provided institution_id.
 * Note: This operation may cascade delete related records (e.g., equipment,
 * faculty_works_at_institution relationships) depending on foreign key
 * constraints configured in the database schema.
 * 
 * @param p_institution_id  Required UUID of the institution record to delete.
 * 
 * @returns Result set containing:
 *   - institution_id: UUID of the deleted institution record
 *   - action: Status message ('deleted')
 * 
 * @throws SQLSTATE '45000' if institution_id is NULL
 */
CREATE PROCEDURE delete_institution (
    IN p_institution_id CHAR(36)
)
BEGIN
    IF p_institution_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'institution_id is required for delete_institution';
    END IF;

    DELETE FROM institution
    WHERE institution_id = p_institution_id;

    SELECT p_institution_id AS institution_id, 'deleted' AS action;
END $$

DELIMITER ;
