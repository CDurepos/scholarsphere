CREATE FUNCTION publication_has_keyword(
    IN p_publication_id CHAR(36),
    IN p_name VARCHAR(64)
)
RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM publication_keywords
        WHERE publication_id = p_publication_id
          AND name = p_name
    );
END;
