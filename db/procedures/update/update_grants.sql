DELIMITER $$

DROP PROCEDURE IF EXISTS update_grants;
CREATE PROCEDURE update_grants(
    IN p_grant_id       CHAR(36)        NOT NULL,
    IN p_description    VARCHAR(2048)   NULL,
    IN p_amount         DECIMAL(10,2)   NOT NULL,
    IN p_start_date     DATE            NOT NULL,
    IN p_end_date       DATE            NULL
)
BEGIN
    UPDATE grants
    SET 
        description = p_description, 
        amount = p_amount, 
        start_date = p_start_date, 
        end_date = p_end_date
    WHERE grant_id = p_grant_id;
END $$