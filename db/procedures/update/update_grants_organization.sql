DELIMITER $$

DROP PROCEDURE IF EXISTS update_grants_organization;
CREATE PROCEDURE update_grants_organization(
    IN  p_grant_id  CHAR(36),
    IN  p_name      VARCHAR(255)
)
BEGIN
    INSERT INTO grants_organization (grant_id, name)
    VALUES  (p_grant_id, p_name)
    ON DUPLICATE KEY UPDATE
        name = VALUES(name);
END $$