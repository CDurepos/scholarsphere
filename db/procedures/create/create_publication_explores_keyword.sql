DELIMITER $$

/**
 * Associates a keyword with a publication.
 * 
 * Inserts a record into the publication_explores_keyword join table, establishing
 * that a specific publication explores or is related to a specific keyword.
 * This allows publications to be tagged with multiple keywords for categorization
 * and searching.
 * 
 * @param p_publication_id  Required UUID of the publication
 *                          Must reference an existing publication record
 * @param p_name            Required keyword name (max 64 characters)
 *                          Must reference an existing keyword record
 * 
 * @returns No result set. Use read procedures to verify the insert.
 * 
 * @throws SQLSTATE '23000' if publication_id doesn't exist (foreign key constraint)
 * @throws SQLSTATE '23000' if keyword name doesn't exist (foreign key constraint)
 * @throws SQLSTATE '23000' if the publication-keyword association already exists (unique constraint)
 */
CREATE PROCEDURE create_publication_explores_keyword(
    IN p_publication_id CHAR(36),
    IN p_name VARCHAR(64)
)
BEGIN
    INSERT INTO publication_explores_keyword(publication_id, name)
    VALUES (p_publication_id, p_name);
END $$
