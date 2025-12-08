-- Written by Aidan Bell

DELIMITER $$

/**
 * Removes a specific phone number from a faculty member.
 * 
 * Deletes a phone number association for the specified faculty member.
 * Both faculty_id and phone_num must be provided to uniquely identify
 * which phone record to remove, since faculty members can have multiple
 * phone numbers.
 * 
 * @param p_faculty_id  Required UUID of the faculty member
 * @param p_phone_num   Required phone number to remove
 * 
 * @returns Result set containing:
 *   - faculty_id: UUID of the faculty member
 *   - phone_num: The phone number that was deleted
 *   - action: Status message ('deleted')
 */
CREATE PROCEDURE delete_faculty_phone (
    IN p_faculty_id CHAR(36),
    IN p_phone_num  VARCHAR(32)
)
BEGIN
    -- Delete the specific phone number association
    -- Both faculty_id AND phone_num are required in WHERE clause to uniquely
    -- identify which phone number to remove (since faculty can have multiple phones)
    DELETE FROM faculty_phone
    WHERE faculty_id = p_faculty_id
      AND phone_num  = p_phone_num;

    -- Return confirmation of what was deleted
    SELECT p_faculty_id AS faculty_id,
           p_phone_num AS phone_num,
           'deleted' AS action;
END$$

DELIMITER ;