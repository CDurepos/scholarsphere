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
 */
CREATE PROCEDURE update_faculty_email (
    IN p_faculty_id   CHAR(36),
    IN p_old_email    VARCHAR(255),
    IN p_new_email    VARCHAR(255)
)
BEGIN
    -- Update the specific email address record
    -- Both faculty_id AND old_email are needed in WHERE clause because
    -- a faculty member can have multiple email addresses, so we identify which one to change
    -- Note: This procedure does not return a result set (unlike other update procedures)
    UPDATE faculty_email
    SET email = p_new_email
    WHERE faculty_id = p_faculty_id
      AND email = p_old_email;
END$$

DELIMITER ;