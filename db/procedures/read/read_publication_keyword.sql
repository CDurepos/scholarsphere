DELIMITER $$

CREATE PROCEDURE read_keyword_publication(
    IN p_publication_id CHAR(36)
)
BEGIN
    SELECT name
    FROM publication_keywords
    WHERE publication_id = p_publication_id;
END $$