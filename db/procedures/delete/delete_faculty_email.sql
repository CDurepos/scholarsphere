DELIMITER $$

/**
 * Removes a specific email address from a faculty member.
 * 
 * Deletes an email association for the specified faculty member. Both
 * faculty_id and email must be provided to uniquely identify which email
 * record to remove, since faculty members can have multiple email addresses.
 * 
 * @param p_faculty_id  Required UUID of the faculty member
 * @param p_email       Required email address to remove
 * 
 * @returns No result set (unlike other delete procedures)
 */
CREATE PROCEDURE delete_faculty_email (
    IN p_faculty_id CHAR(36),
    IN p_email      VARCHAR(255)
)
BEGIN
    -- Delete the specific email address association
    -- Both faculty_id AND email are required in WHERE clause to uniquely
    -- identify which email to remove (since faculty can have multiple emails)
    -- Note: This procedure does not return a result set (unlike other delete procedures)
    DELETE FROM faculty_email
    WHERE faculty_id = p_faculty_id
      AND email = p_email;
END$$

DELIMITER ;