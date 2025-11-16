CREATE PROCEDURE remove_keyword_publication(
    IN p_publication_id CHAR(36),
    IN p_name VARCHAR(64)
)
BEGIN
    DELETE FROM publication_keywords
    WHERE publication_id = p_publication_id
      AND name = p_name;
END;