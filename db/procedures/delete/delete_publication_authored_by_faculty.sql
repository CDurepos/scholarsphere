-- Written by Aidan Bell

DELIMITER $$

/**
 * Deletes a publication-author association from the database.
 * 
 * Removes a specific publication_authored_by_faculty relationship, disassociating
 * a faculty member from a publication. This does not delete the faculty member
 * or the publication, only the authorship relationship between them.
 * 
 * @param p_faculty_id      Required UUID of the faculty member
 * @param p_publication_id  Required UUID of the publication
 * 
 * @returns No result set. Use read procedures to verify the deletion.
 * 
 * @throws SQLSTATE '45000' if faculty_id or publication_id is NULL
 */
CREATE PROCEDURE delete_publication_authored_by_faculty(
    IN p_faculty_id CHAR(36),
    IN p_publication_id CHAR(36)
)
BEGIN
    IF p_faculty_id IS NULL OR p_publication_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id and publication_id are required for delete_publication_authored_by_faculty';
    END IF;

    DELETE FROM publication_authored_by_faculty
    WHERE faculty_id = p_faculty_id AND publication_id = p_publication_id;
END $$
DELIMITER ;
