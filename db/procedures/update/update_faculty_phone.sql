DELIMITER $$

/**
 * Updates a specific phone number for a faculty member.
 * 
 * Changes an existing phone number to a new value. Both the old phone number
 * and new phone number must be specified to uniquely identify which phone
 * record to update, since faculty members can have multiple phone numbers.
 * 
 * @param p_faculty_id  Required UUID of the faculty member
 * @param p_old_phone   Required current phone number to be changed
 * @param p_new_phone   Required new phone number value
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the faculty member
 *   - old_phone: The previous phone number
 *   - new_phone: The new phone number
 *   - action: Status message ('updated')
 */
CREATE PROCEDURE update_faculty_phone (
    IN p_faculty_id   CHAR(36),
    IN p_old_phone    VARCHAR(32),
    IN p_new_phone    VARCHAR(32)
)
BEGIN
    -- Update the specific phone number record
    -- Both faculty_id AND old_phone are needed in WHERE clause because
    -- a faculty member can have multiple phone numbers, so we identify which one to change
    UPDATE faculty_phone
    SET phone_num = p_new_phone
    WHERE faculty_id = p_faculty_id
      AND phone_num  = p_old_phone;

    -- Return confirmation showing both old and new phone numbers
    SELECT p_faculty_id AS faculty_id,
           p_old_phone AS old_phone,
           p_new_phone AS new_phone,
           'updated' AS action;
END$$

DELIMITER ;