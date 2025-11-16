DELIMITER $$

CREATE PROCEDURE IF EXISTS read_grants_organization;
CREATE PROCEDURE read_grants_organization(
    IN p_grant_id   CHAR(36)
)
BEGIN
    SELECT name
    FROM grants_organization
    WHERE grant_id = p_grant_id;
END $$