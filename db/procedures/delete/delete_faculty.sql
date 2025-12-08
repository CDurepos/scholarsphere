-- Written by Aidan Bell

DELIMITER $$

/**
 * Deletes a faculty member record from the database.
 * 
 * Removes the faculty record identified by the provided faculty_id.
 * Note: This may fail if there are foreign key constraints from related tables
 * (e.g., publications, departments, emails, etc.) depending on database schema.
 * 
 * @param p_faculty_id  Required UUID of the faculty member to delete
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the deleted faculty member
 *   - action: Status message ('deleted')
 */
CREATE PROCEDURE delete_faculty (
    IN p_faculty_id CHAR(36)
)
BEGIN
    -- Delete the faculty record matching the provided ID
    DELETE FROM faculty
    WHERE faculty_id = p_faculty_id;

    -- Return confirmation with the deleted ID and status message
    SELECT p_faculty_id AS faculty_id, 'deleted' AS action;
END$$

DELIMITER ;