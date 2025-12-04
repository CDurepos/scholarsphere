DELIMITER $$

DROP FUNCTION IF EXISTS get_DOI$$
CREATE FUNCTION get_DOI(p_id CHAR(36))
RETURNS VARCHAR(64)
READS SQL DATA
BEGIN
    DECLARE v_pub_doi VARCHAR(64);
    SELECT doi INTO v_pub_doi
    FROM publications
    WHERE publication_id = p_id;
    RETURN v_pub_doi;
END $$
DELIMITER ;
