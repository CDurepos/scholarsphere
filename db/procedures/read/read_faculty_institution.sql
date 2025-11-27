DELIMITER $$

/**
 * Retrieves faculty-institution relationship records from the database.
 * 
 * Returns faculty_works_at_institution records based on optional filters.
 * This is an alias/alternative name for read_faculty_works_at_institution.
 * If both parameters are NULL, all relationship records are returned.
 * Results are ordered by faculty_id, institution_id, and start_date (descending).
 * 
 * @param p_faculty_id      Optional UUID of a faculty member to filter by.
 *                         When provided, only relationships for that faculty member are returned.
 * @param p_institution_id  Optional UUID of an institution to filter by.
 *                         When provided, only relationships for that institution are returned.
 * 
 * @returns Result set containing all columns from the faculty_works_at_institution table:
 *   - faculty_id
 *   - institution_id
 *   - start_date
 *   - end_date
 * 
 * If both parameters are NULL, returns all relationship records.
 */
CREATE PROCEDURE read_faculty_institution (
    IN p_faculty_id      CHAR(36),
    IN p_institution_id  CHAR(36)
)
BEGIN
    SELECT fwi.*
    FROM faculty_works_at_institution fwi
    WHERE (p_faculty_id IS NULL OR fwi.faculty_id = p_faculty_id)
      AND (p_institution_id IS NULL OR fwi.institution_id = p_institution_id)
    ORDER BY fwi.faculty_id, fwi.institution_id, fwi.start_date DESC;
END $$

DELIMITER ;
