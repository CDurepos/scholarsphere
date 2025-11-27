DELIMITER $$

DROP FUNCTION IF EXISTS get_citation_count;
CREATE FUNCTION get_citation_count(p_publication_id CHAR(36))
RETURNS INT
READS SQL DATA
BEGIN
    DECLARE v_count INT;

    SELECT citation_count INTO v_count
    FROM publications
    WHERE publication_id = p_publication_id;

    RETURN v_count;
END $$

DELIMITER ;
