DELIMITER $$

/**
 * Creates a new keyword record in the database.
 * 
 * Inserts a new keyword with the provided name. Keywords are used to tag
 * and categorize research areas, publications, and faculty interests.
 * 
 * @param p_name  Required keyword name (max 64 characters)
 * 
 * @returns No result set. Use read procedures to verify the insert.
 * 
 * @throws SQLSTATE '23000' if a keyword with the same name already exists (unique constraint)
 */
CREATE PROCEDURE create_keyword(
    IN p_name VARCHAR(64)
)
BEGIN
    INSERT INTO keyword (name)
    VALUES (p_name);
END $$

DELIMITER ;
