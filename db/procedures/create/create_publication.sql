-- Written by Owen Leitzell

DELIMITER $$

/**
 * Creates a new publication record in the database.
 * 
 * Inserts a new publication with the provided information. Publications
 * represent scholarly works such as papers, articles, books, etc. The
 * citation_count is automatically initialized to 0.
 * 
 * @param p_id         Required UUID for the publication record
 * @param p_title      Required publication title (max 128 characters)
 * @param p_publisher  Optional publisher name (max 255 characters)
 * @param p_year       Optional publication year (INT)
 * @param p_doi        Optional Digital Object Identifier (max 64 characters)
 * @param p_abstract   Optional abstract text (TEXT field)
 * @param p_citation_count Optional citation count (INT)
 * 
 * @returns No result set. Use read procedures to verify the insert.
 * 
 * @throws SQLSTATE '23000' if publication_id already exists (primary key constraint)
 */
CREATE PROCEDURE create_publication(
    IN p_id CHAR(36),
    IN p_title VARCHAR(128),
    IN p_publisher VARCHAR(255),
    IN p_year INT,
    IN p_doi VARCHAR(64),
    IN p_abstract TEXT,
    IN p_citation_count INT
)
BEGIN
    -- Validate input: publication_id must be provided
    IF p_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'publication_id is required.';
    END IF;

    INSERT INTO publication (publication_id, title, publisher, year, doi, abstract, citation_count)
    VALUES (p_id, p_title, p_publisher, p_year, p_doi, p_abstract, p_citation_count);
END $$
DELIMITER ;
