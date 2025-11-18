DELIMITER $$

/**
 * Deletes a faculty-institution relationship record from the database.
 * 
 * Removes a specific faculty_works_at_institution relationship identified by
 * the composite primary key (faculty_id, institution_id, start_date). This
 * allows removing a specific employment period for a faculty member at an
 * institution, even if they have multiple employment periods at the same
 * institution.
 * 
 * @param p_faculty_id      Required UUID of the faculty member
 * @param p_institution_id  Required UUID of the institution
 * @param p_start_date      Required start date of the employment relationship
 *                          (part of the composite primary key)
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the faculty member
 *   - institution_id: UUID of the institution
 *   - start_date: Start date of the deleted relationship
 *   - action: Status message ('deleted')
 * 
 * @throws SQLSTATE '45000' if any required parameter is NULL
 */
CREATE PROCEDURE delete_faculty_works_at_institution (
    IN p_faculty_id      CHAR(36),
    IN p_institution_id  CHAR(36),
    IN p_start_date      DATE
)
BEGIN
    IF p_faculty_id IS NULL OR p_institution_id IS NULL OR p_start_date IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id, institution_id, and start_date are required for delete_faculty_works_at_institution';
    END IF;

    DELETE FROM faculty_works_at_institution
    WHERE faculty_id = p_faculty_id
      AND institution_id = p_institution_id
      AND start_date = p_start_date;

    SELECT p_faculty_id AS faculty_id,
           p_institution_id AS institution_id,
           p_start_date AS start_date,
           'deleted' AS action;
END $$

DELIMITER ;


DELIMITER ;
