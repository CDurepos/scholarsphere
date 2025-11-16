DELIMITER $$

CREATE PROCEDURE insert_into_publication(
    IN p_id CHAR(36),
    IN p_title VARCHAR(64),
    IN p_publisher VARCHAR(255),
    IN p_year INT,
    IN p_doi VARCHAR(64),
    IN p_abstract TEXT
    out p_generated_id  CHAR(36)
)
BEGIN
    SET p_generated_id = UUID();
    INSERT INTO publication (publication_id, title, publisher, year, doi, abstract, citation_count)
    VALUES (p_id, p_title, p_publisher, p_year, p_doi, p_abstract, 0);
END $$