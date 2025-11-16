DELIMITER $$

CREATE PROCEDURE add_keyword(
    IN p_name VARCHAR(64)
)
BEGIN
    INSERT INTO keyword (name)
    VALUES (p_name);
END $$
