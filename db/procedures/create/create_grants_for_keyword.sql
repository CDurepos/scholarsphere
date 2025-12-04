DELIMITER $$

/**
 * Associates a grant with a keyword.
 * 
 * Inserts a record into the grants_for_keyword join table, establishing
 * that a specific grant is related to a specific keyword. This allows
 * grants to be categorized and searched by research keywords.
 * 
 * @param p_grant_id  Required UUID of the grant
 *                    Must reference an existing grant record
 * @param p_name      Required keyword name (max 64 characters)
 *                    Must reference an existing keyword record
 * 
 * @returns No result set. Use read procedures to verify the insert.
 * 
 * @throws SQLSTATE '23000' if grant_id doesn't exist (foreign key constraint)
 * @throws SQLSTATE '23000' if keyword name doesn't exist (foreign key constraint)
 * @throws SQLSTATE '23000' if the grant-keyword association already exists (unique constraint)
 */
DROP PROCEDURE IF EXISTS create_grants_for_keyword$$
CREATE PROCEDURE create_grants_for_keyword(
    IN p_grant_id  CHAR(36),
    IN p_name      VARCHAR(64)
)
BEGIN
    INSERT INTO grants_for_keyword(grant_id, name) 
    VALUES(p_grant_id, p_name);
END $$
DELIMITER ;
