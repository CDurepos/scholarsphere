CREATE PROCEDURE add_keyword_to_publication(
    IN p_publication_id CHAR(36),
    IN p_name VARCHAR(64)
)
BEGIN
    INSERT INTO publication_keywords (publication_id, name)
    VALUES (p_publication_id, p_name);
END;
