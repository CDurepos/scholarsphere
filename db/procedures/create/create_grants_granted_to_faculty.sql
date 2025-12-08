-- Written by Clayton Durepos

DELIMITER $$

/**
 * Associates a grant with a faculty member.
 * 
 * Inserts a record into the grants_granted_to_faculty join table, establishing
 * that a specific faculty member is a recipient of a specific grant. This
 * allows tracking which faculty members have received which grants.
 * 
 * @param p_faculty_id  Required UUID of the faculty member
 *                      Must reference an existing faculty record
 * @param p_grant_id    Required UUID of the grant
 *                      Must reference an existing grant record
 * 
 * @returns No result set. Use read procedures to verify the insert.
 * 
 * @throws SQLSTATE '23000' if faculty_id doesn't exist (foreign key constraint)
 * @throws SQLSTATE '23000' if grant_id doesn't exist (foreign key constraint)
 * @throws SQLSTATE '23000' if the faculty-grant association already exists (unique constraint)
 */
DROP PROCEDURE IF EXISTS create_grants_granted_to_faculty$$
CREATE PROCEDURE create_grants_granted_to_faculty(
    IN p_faculty_id    CHAR(36),
    IN p_grant_id      CHAR(36)
)
BEGIN
    INSERT INTO grants_granted_to_faculty(faculty_id, grant_id)
    VALUES(p_faculty_id, p_grant_id);
END $$
DELIMITER ;
