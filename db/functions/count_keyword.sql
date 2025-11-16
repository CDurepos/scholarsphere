DELIMITER $$

CREATE FUNCTION count_keywords()
RETURNS INT
BEGIN
    DECLARE v_total INT;

    SELECT COUNT(*) INTO v_total
    FROM keyword;

    RETURN v_total;
END $$
