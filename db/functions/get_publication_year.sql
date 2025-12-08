-- Written by Owen Leitzell

DELIMITER $$

DROP FUNCTION IF EXISTS get_publication_year$$
CREATE FUNCTION get_publication_year(p_publication_id CHAR(36))
RETURNS INT
READS SQL DATA
BEGIN
    DECLARE v_year INT;

    SELECT year INTO v_year
    FROM publications
    WHERE publication_id = p_publication_id;
    RETURN v_year;
END $$

DELIMITER ;
