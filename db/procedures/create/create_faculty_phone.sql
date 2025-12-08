-- Written by Aidan Bell

DELIMITER $$

/**
 * Adds a phone number to a faculty member.
 * 
 * Inserts a new phone number record for the specified faculty member.
 * Faculty members can have multiple phone numbers, so this creates an
 * additional phone number association rather than replacing existing ones.
 * 
 * @param p_faculty_id  Required UUID of the faculty member
 * @param p_phone_num   Required phone number to associate with the faculty member
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the faculty member
 *   - phone_num: The phone number that was inserted
 *   - action: Status message ('inserted')
 */
CREATE PROCEDURE create_faculty_phone (
    IN p_faculty_id CHAR(36),
    IN p_phone_num  VARCHAR(32)
)
BEGIN
    -- Insert a new phone number for the faculty member
    -- Faculty can have multiple phone numbers (e.g., office, mobile, lab)
    -- The combination of faculty_id and phone_num should be unique
    INSERT INTO faculty_phone (faculty_id, phone_num)
    VALUES (p_faculty_id, p_phone_num);

    -- Return confirmation with the inserted values
    SELECT p_faculty_id AS faculty_id,
           p_phone_num AS phone_num,
           'inserted' AS action;
END$$

DELIMITER ;