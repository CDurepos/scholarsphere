-- Written by Clayton Durepos

DELIMITER $$

/**
 * Deletes all institution relationships for a faculty member.
 * 
 * Removes all faculty_works_at_institution records for a given faculty_id.
 * Used when updating a faculty member's institution (delete all, then add new).
 * 
 * @param p_faculty_id  Required UUID of the faculty member
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the faculty member
 *   - rows_deleted: Number of relationships deleted
 *   - action: Status message ('deleted')
 */
CREATE PROCEDURE delete_faculty_works_at_institution_by_faculty (
    IN p_faculty_id CHAR(36)
)
BEGIN
    DECLARE v_rows_deleted INT DEFAULT 0;
    
    IF p_faculty_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id is required for delete_faculty_works_at_institution_by_faculty';
    END IF;

    DELETE FROM faculty_works_at_institution
    WHERE faculty_id = p_faculty_id;
    
    SET v_rows_deleted = ROW_COUNT();

    SELECT p_faculty_id AS faculty_id,
           v_rows_deleted AS rows_deleted,
           'deleted' AS action;
END $$

DELIMITER ;

