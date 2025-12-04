DELIMITER $$

/**
 * Retrieves all keywords associated with a specific publication.
 * 
 * Returns all keyword names that are associated with the specified
 * publication. This shows the research topics and categories for the publication.
 * 
 * @param p_publication_id  Required UUID of the publication
 * 
 * @returns Result set containing:
 *   - name: Keyword name (max 64 characters)
 *   (Multiple rows if the publication is associated with multiple keywords)
 * 
 * @throws SQLSTATE '45000' if publication_id is NULL
 */
DROP PROCEDURE IF EXISTS read_publication_explores_keyword_by_publication$$
CREATE PROCEDURE read_publication_explores_keyword_by_publication(
    IN p_publication_id CHAR(36)
)
BEGIN
    IF p_publication_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'publication_id is required';
    END IF;

    SELECT name
    FROM publication_explores_keyword
    WHERE publication_id = p_publication_id;
END $$
DELIMITER ;
