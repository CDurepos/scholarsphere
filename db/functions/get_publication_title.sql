DELIMITER $$

DROP FUNCTION IF EXISTS get_publication_title$$
CREATE FUNCTION get_publication_title(p_publication_id CHAR(36))
RETURNS VARCHAR(128)
READS SQL DATA
BEGIN
    DECLARE v_title VARCHAR(128);

    SELECT title INTO v_title
    FROM publications
    WHERE publication_id = p_publication_id;

    RETURN v_title;
END $$

DELIMITER ;
