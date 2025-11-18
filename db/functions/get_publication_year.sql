DELIMITER $$

CREATE FUNCTION get_publication_year(p_publication_id CHAR(36))
RETURNS INT
BEGIN
    DECLARE v_year INT;

    SELECT year INTO v_year
    FROM publications
    WHERE publication_id = p_publication_id;
    RETURN v_year;
END $$

DELIMITER ;
