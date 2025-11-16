DELIMITER $$

/**
 * Retrieves all phone numbers associated with a faculty member.
 * 
 * Returns all phone number records for the specified faculty member.
 * Since faculty members can have multiple phone numbers, this may return
 * multiple rows.
 * 
 * @param p_faculty_id  Required UUID of the faculty member
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the faculty member
 *   - phone_num: One phone number associated with the faculty member
 *   (Multiple rows if the faculty member has multiple phone numbers)
 */
CREATE PROCEDURE read_faculty_phone (
    IN p_faculty_id CHAR(36)
)
BEGIN
    -- Retrieve all phone numbers for the specified faculty member
    -- Returns multiple rows if the faculty member has multiple phone numbers
    -- Each row represents one phone number association
    SELECT faculty_id, phone_num
    FROM faculty_phone
    WHERE faculty_id = p_faculty_id;
END$$

DELIMITER ;