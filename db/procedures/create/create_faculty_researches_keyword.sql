DELIMITER $$

/**
 * Associates a keyword with a faculty member's research interests.
 * 
 * Inserts a record into the faculty_researches_keyword join table, establishing
 * that a specific faculty member researches a specific keyword. This allows
 * faculty members to have multiple research interests and enables searching
 * faculty by their research areas.
 * 
 * @param p_faculty_id  Required UUID of the faculty member
 *                      Must reference an existing faculty record
 * @param p_name        Required keyword name (max 64 characters)
 *                      Must reference an existing keyword record
 * 
 * @returns No result set. Use read procedures to verify the insert.
 * 
 * @throws SQLSTATE '23000' if faculty_id doesn't exist (foreign key constraint)
 * @throws SQLSTATE '23000' if keyword name doesn't exist (foreign key constraint)
 * @throws SQLSTATE '23000' if the faculty-keyword association already exists (unique constraint)
 */
CREATE PROCEDURE create_faculty_researches_keyword(
    IN p_faculty_id CHAR(36),
    IN p_name VARCHAR(64)
)
BEGIN
    INSERT INTO faculty_researches_keyword (name, faculty_id)
    VALUES (p_name, p_faculty_id);
END $$

DELIMITER ;
