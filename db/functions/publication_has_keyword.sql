-- Written by Owen Leitzell

DELIMITER $$

DROP FUNCTION IF EXISTS publication_has_keyword$$
CREATE FUNCTION publication_has_keyword(
    p_publication_id CHAR(36),
    p_name VARCHAR(64)
)
RETURNS BOOLEAN
READS SQL DATA
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM publication_keywords
        WHERE publication_id = p_publication_id
          AND name = p_name
    );
END $$

DELIMITER ;
