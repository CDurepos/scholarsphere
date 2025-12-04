DELIMITER $$

/**
 * Retrieves all phone number records from the database.
 * 
 * Returns all records from the faculty_phone table.
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the faculty member
 *   - phone_num: Phone number
 * 
 * Results are ordered by faculty_id, then phone_num.
 */
DROP PROCEDURE IF EXISTS read_faculty_phone$$
CREATE PROCEDURE read_faculty_phone()
BEGIN
    SELECT faculty_id, phone_num
    FROM faculty_phone
    ORDER BY faculty_id, phone_num;
END $$

DELIMITER ;

