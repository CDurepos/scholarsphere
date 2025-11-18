DELIMITER $$

DROP PROCEDURE IF EXISTS last_login;

CREATE PROCEDURE last_login(
    IN  p_username      VARCHAR(255),
    IN  p_password      VARCHAR(255),
    OUT p_faculty_id    CHAR(36),
    OUT p_status_code   TINYINT
)
BEGIN
    DECLARE v_salt          VARCHAR(255);
    DECLARE v_expected_hash VARCHAR(255);
    DECLARE v_computed_hash CHAR(64);

    -- DEFAULT OUTPUT
    SET p_status_code = -1;
    SET p_faculty_id = NULL;

    -- CHECK USERNAME EXISTS
    IF EXISTS (SELECT 1 FROM credentials WHERE username = p_username) THEN

        -- GET EXISTING ID, SALT, & HASH
        SELECT  faculty_id, password_salt, password_hash
        INTO    p_faculty_id, v_salt, v_expected_hash
        FROM    credentials
        WHERE   username = p_username
        LIMIT   1;

        -- COMPUTE INPUT HASH 
        SET v_computed_hash = hash_password(p_password, v_salt);

        -- VALIDATE
        IF v_computed_hash = v_expected_hash THEN

            -- STATUS CODE 0 ON SUCCESS
            SET p_status_code = 0;

            UPDATE credentials
            SET last_login = NOW()
            WHERE faculty_id = p_faculty_id;

        ELSE
            -- STATUS CODE 1 ON INVALID PASSWORD
            SET p_status_code = 1;
            SET p_faculty_id = NULL;
        END IF;

    ELSE
        -- STATUS CODE 2 ON INVALID USERNAME
        SET p_status_code   = 2;
    
    END IF;
END $$

DELIMITER ;
