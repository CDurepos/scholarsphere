DELIMITER $$

/**
 * Deletes a faculty keyword generation record from the database.
 * 
 * Removes a specific generation record. This can be used to clean up old records
 * or remove specific entries for administrative purposes.
 * 
 * @param p_generation_id  Required UUID of the generation record to delete
 * 
 * @returns No result set. Use read procedures to verify the deletion.
 * 
 * @throws SQLSTATE '45000' if generation_id is NULL or empty
 */
CREATE PROCEDURE delete_faculty_generates_keyword(
    IN p_generation_id CHAR(36)
)
BEGIN
    IF p_generation_id IS NULL OR TRIM(p_generation_id) = '' THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'generation_id is required for delete_faculty_generates_keyword';
    END IF;

    DELETE FROM faculty_generates_keyword
    WHERE generation_id = p_generation_id;
END $$

DELIMITER ;

