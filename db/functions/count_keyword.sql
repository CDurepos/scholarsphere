DELIMITER $$

DROP FUNCTION IF EXISTS count_keywords$$
CREATE FUNCTION count_keywords()
RETURNS INT
READS SQL DATA
BEGIN
    DECLARE v_total INT;

    SELECT COUNT(*) INTO v_total
    FROM keyword;

    RETURN v_total;
END $$

DELIMITER ;
