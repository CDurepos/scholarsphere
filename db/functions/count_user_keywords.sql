DELIMITER $$

DROP FUNCTION IF EXISTS count_user_keywords$$
CREATE FUNCTION count_user_keywords(
    p_faculty_id CHAR(36)
)
RETURNS INT
READS SQL DATA
BEGIN
    DECLARE v_total INT;

    SELECT COUNT(*) INTO v_total
    FROM user_keywords
    WHERE faculty_id = p_faculty_id;

    RETURN v_total;
END $$

DELIMITER ;
