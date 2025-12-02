DELIMITER $$

/**
 * Retrieves all faculty-institution relationship records from the database.
 * 
 * Returns all records from the faculty_works_at_institution table.
 * Results are ordered by faculty_id, institution_id, and start_date (descending).
 * 
 * @returns Result set containing all columns from the faculty_works_at_institution table:
 *   - faculty_id
 *   - institution_id
 *   - start_date
 *   - end_date
 */
DROP PROCEDURE IF EXISTS read_faculty_works_at_institution;
CREATE PROCEDURE read_faculty_works_at_institution()
BEGIN
    SELECT fwi.*
    FROM faculty_works_at_institution fwi
    ORDER BY fwi.faculty_id, fwi.institution_id, fwi.start_date DESC;
END $$

DELIMITER ;

