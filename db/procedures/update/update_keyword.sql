DELIMITER $$

/**
 * Updates a keyword name in the database.
 * 
 * Changes the name of an existing keyword from the old name to a new name.
 * Since keyword name is the primary key, this effectively renames the keyword.
 * All associations with this keyword (faculty, publications, grants) will
 * automatically update due to foreign key constraints.
 * 
 * @param p_old_name  Required current keyword name to be changed
 * @param p_new_name  Required new keyword name (max 64 characters)
 * 
 * @returns No result set. Use read procedures to verify the update.
 * 
 * @throws SQLSTATE '45000' if old_name or new_name is NULL
 * @throws SQLSTATE '45000' if old_name doesn't exist
 * @throws SQLSTATE '23000' if new_name already exists (unique constraint)
 */
CREATE PROCEDURE update_keyword(
    IN p_old_name VARCHAR(64),
    IN p_new_name VARCHAR(64)
)
BEGIN
    IF p_old_name IS NULL OR p_new_name IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'old_name and new_name are required for update_keyword';
    END IF;

    UPDATE keyword
    SET name = p_new_name
    WHERE name = p_old_name;

    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Keyword with old_name does not exist';
    END IF;
END $$