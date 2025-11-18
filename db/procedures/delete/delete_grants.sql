DELIMITER $$

CREATE PROCEDURE delete_grants(
    IN p_grant_id CHAR(36)
)
BEGIN
    DELETE FROM grants
    WHERE grant_id = p_grant_id;
END $$

DELIMITER ;