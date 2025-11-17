DELIMITER $$

/**
 * Updates an existing publication record in the database.
 * 
 * Performs a partial update on a publication record. Only non-NULL parameters
 * will update the corresponding fields; NULL parameters leave existing values
 * unchanged. The publication_id is required to identify which record to update.
 * 
 * @param p_publication_id  Required UUID of the publication record to update
 * @param p_title            Optional new publication title (NULL to keep existing)
 * @param p_publisher        Optional new publisher name (NULL to keep existing)
 * @param p_year             Optional new publication year (NULL to keep existing)
 * @param p_doi              Optional new Digital Object Identifier (NULL to keep existing)
 * @param p_abstract          Optional new abstract text (NULL to keep existing)
 * @param p_citation_count   Optional new citation count (NULL to keep existing)
 * 
 * @returns No result set. Use read procedures to verify the update.
 * 
 * @throws SQLSTATE '45000' if publication_id is NULL
 * @throws SQLSTATE '45000' if publication_id doesn't exist
 */
CREATE PROCEDURE update_publication(
    IN p_publication_id CHAR(36),
    IN p_title VARCHAR(64),
    IN p_publisher VARCHAR(255),
    IN p_year INT,
    IN p_doi VARCHAR(64),
    IN p_abstract TEXT,
    IN p_citation_count INT
)
BEGIN
    IF p_publication_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'publication_id is required for update_publication';
    END IF;

    -- Title
    IF p_title IS NOT NULL THEN
        UPDATE publication
        SET title = p_title
        WHERE publication_id = p_publication_id;
    END IF;

    -- Publisher
    IF p_publisher IS NOT NULL THEN
        UPDATE publication
        SET publisher = p_publisher
        WHERE publication_id = p_publication_id;
    END IF;

    -- Year
    IF p_year IS NOT NULL THEN
        UPDATE publication
        SET year = p_year
        WHERE publication_id = p_publication_id;
    END IF;

    -- DOI
    IF p_doi IS NOT NULL THEN
        UPDATE publication
        SET doi = p_doi
        WHERE publication_id = p_publication_id;
    END IF;

    -- Abstract
    IF p_abstract IS NOT NULL THEN
        UPDATE publication
        SET abstract = p_abstract
        WHERE publication_id = p_publication_id;
    END IF;

    -- Citation Count
    IF p_citation_count IS NOT NULL THEN
        UPDATE publication
        SET citation_count = p_citation_count
        WHERE publication_id = p_publication_id;
    END IF;
END $$