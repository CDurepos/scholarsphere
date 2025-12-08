-- Written by Aidan Bell

DELIMITER $$

/**
 * Updates a specific email address for a faculty member.
 * 
 * Changes an existing email address to a new value. Both the old email
 * and new email must be specified to uniquely identify which email record
 * to update, since faculty members can have multiple email addresses.
 * 
 * @param p_faculty_id  Required UUID of the faculty member
 * @param p_old_email   Required current email address to be changed
 * @param p_new_email   Required new email address value
 * 
 * @returns No result set (unlike other update procedures)
 * 
 * @throws SQLSTATE '45000' if any parameter is NULL, or if no matching record exists
 */
CREATE PROCEDURE update_faculty_email (
    IN p_faculty_id   CHAR(36),
    IN p_old_email    VARCHAR(255),
    IN p_new_email    VARCHAR(255)
)
BEGIN
    -- Validate that all required parameters are provided
    IF p_faculty_id IS NULL OR p_old_email IS NULL OR p_new_email IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id, old_email, and new_email are required for update_faculty_email';
    END IF;

    -- Update the specific email address record
    -- Both faculty_id AND old_email are needed in WHERE clause because
    -- a faculty member can have multiple email addresses, so we identify which one to change
    UPDATE faculty_email
    SET email = p_new_email
    WHERE faculty_id = p_faculty_id
      AND email = p_old_email;

    -- Check if any rows were actually updated
    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No matching faculty/email entry to update';
    END IF;
END$$

DELIMITER ;