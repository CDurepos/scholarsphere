DELIMITER $$

/**
 * Retrieves all publications authored by a specific faculty member.
 * 
 * Returns all publication records where the specified faculty member
 * is listed as an author. This shows the faculty member's publication
 * history and scholarly output.
 * 
 * @param p_faculty_id  Required UUID of the faculty member
 * 
 * @returns Result set containing all columns from the publication table:
 *   - publication_id
 *   - title
 *   - publisher
 *   - year
 *   - doi
 *   - abstract
 *   - citation_count
 *   (Multiple rows if the faculty member has authored multiple publications)
 * 
 * @throws SQLSTATE '45000' if faculty_id is NULL
 */
CREATE PROCEDURE read_faculty_publications(
    IN p_faculty_id CHAR(36)
)
BEGIN
    IF p_faculty_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id is required';
    END IF;

    SELECT p.*
    FROM publication p
    JOIN publication_authored_by_faculty pa
        ON p.publication_id = pa.publication_id
    WHERE pa.faculty_id = p_faculty_id;
END $$

DELIMITER ;