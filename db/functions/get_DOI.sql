DELIMITER $$

CREATE FUNCTION get_DOI(p_id CHAR(36))
RETURNS VARCHAR(64)
BEGIN
    DECLARE v_pub_doi VARCHAR(64);
    SELECT doi INTO v_pub_doi
    FROM publications
    WHERE publication_id = p_id;
    RETURN v_pub_doi;
END $$
DELIMITER ;
