DELIMITER $$

/**
 * Adds an email address to a faculty member.
 * 
 * Inserts a new email record for the specified faculty member. Faculty
 * members can have multiple email addresses, so this creates an additional
 * email association rather than replacing existing ones.
 * 
 * @param p_faculty_id  Required UUID of the faculty member
 * @param p_email       Required email address to associate with the faculty member
 * 
 * @returns No result set (unlike other create procedures)
 */
CREATE PROCEDURE create_faculty_email (
    IN p_faculty_id CHAR(36),
    IN p_email      VARCHAR(255)
)
BEGIN
    -- Insert a new email address for the faculty member
    -- Faculty can have multiple email addresses (e.g., work, personal, lab)
    -- The combination of faculty_id and email should be unique
    -- Note: This procedure does not return a result set (unlike other create procedures)
    INSERT INTO faculty_email (faculty_id, email)
    VALUES (p_faculty_id, p_email);
END$$

DELIMITER ;