DELIMITER $$

/**
 * Updates an existing faculty-institution relationship record in the database.
 * 
 * Updates the start_date and end_date for a faculty-institution relationship.
 * The record is identified using only faculty_id and institution_id (the composite
 * primary key). Both dates are updated directly using a simple UPDATE statement.
 * 
 * @param p_faculty_id      Required UUID of the faculty member
 * @param p_institution_id  Required UUID of the institution
 * @param p_start_date      Required new start date for the relationship
 * @param p_end_date        Optional new end date for the relationship (NULL allowed)
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the faculty member
 *   - institution_id: UUID of the institution
 *   - start_date: The new start date
 *   - end_date: The new end date
 *   - action: Status message ('updated')
 * 
 * @throws SQLSTATE '45000' if faculty_id, institution_id, or start_date is NULL
 * @throws SQLSTATE '45000' if no relationship exists for the given faculty_id and institution_id
 */
CREATE PROCEDURE update_faculty_works_at_institution (
    IN p_faculty_id      CHAR(36),
    IN p_institution_id  CHAR(36),
    IN p_start_date      DATE,
    IN p_end_date        DATE
)
BEGIN
    DECLARE rel_exists INT;

    -- Validate required parameters
    IF p_faculty_id IS NULL OR p_institution_id IS NULL OR p_start_date IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id, institution_id, and start_date are required for update_faculty_works_at_institution';
    END IF;

    -- Check if the relationship exists
    SELECT COUNT(*) INTO rel_exists
    FROM faculty_works_at_institution
    WHERE faculty_id = p_faculty_id
      AND institution_id = p_institution_id;

    IF rel_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_works_at_institution entry not found';
    END IF;

    -- Update the start_date and end_date directly
    -- Since start_date is no longer part of the primary key, we can do a simple UPDATE
    UPDATE faculty_works_at_institution
    SET
        start_date = p_start_date,
        end_date = p_end_date
    WHERE faculty_id = p_faculty_id
      AND institution_id = p_institution_id;

    -- Return the updated values
    SELECT p_faculty_id AS faculty_id,
           p_institution_id AS institution_id,
           p_start_date AS start_date,
           p_end_date AS end_date,
           'updated' AS action;
END $$

DELIMITER ;

