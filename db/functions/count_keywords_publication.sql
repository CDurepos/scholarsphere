DELIMITER $$

DROP FUNCTION IF EXISTS count_keywords_publication$$
CREATE FUNCTION count_keywords_publication(
    p_publication_id CHAR(36)
)
RETURNS INT
READS SQL DATA
BEGIN
    DECLARE v_total INT;

    SELECT COUNT(*) INTO v_total
    FROM publication_keywords
    WHERE publication_id = p_publication_id;

    RETURN v_total;
END $$

DELIMITER ;
