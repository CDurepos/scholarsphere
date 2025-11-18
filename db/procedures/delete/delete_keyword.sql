DELIMITER $$

CREATE PROCEDURE delete_keyword(
    IN p_name VARCHAR(64)
)
BEGIN
    DELETE FROM keyword
    WHERE name = p_name;
END $$

DELIMITER ;