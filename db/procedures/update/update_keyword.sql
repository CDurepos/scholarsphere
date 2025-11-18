DELIMITER $$

CREATE PROCEDURE update_keyword(
    IN p_old_name VARCHAR(64),
    IN p_new_name VARCHAR(64)
)
BEGIN
    UPDATE keyword
    SET name = p_new_name
    WHERE name = p_old_name;
END $$

DELIMITER ;