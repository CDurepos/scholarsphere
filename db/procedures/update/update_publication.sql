DELIMITER $$

-- Update publication, any parameters left null will be unchanged
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

DELIMITER ;
