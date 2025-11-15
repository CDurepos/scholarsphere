DROP PROCEDURE IF EXISTS last_login;
CREATE PROCEDURE last_login(
    IN p_username VARCHAR(255),
    IN p_password VARCHAR(255)
    OUT p_faculty_id CHAR(36),
    OUT p_is_valid TINYINT
)
BEGIN
    DECLARE v_salt          VARCHAR(255);
    DECLARE v_expected_hash VARCHAR(255);
    DECLARE v_computed_hash CHAR(64);
    DECLARE v_not_found     TINYINT DEFAULT 0;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_not_found = 1;

    SELECT faculty_id, password_salt, password_hash
    INTO p_faculty_id, v_salt, v_expected_hash
    FROM credentials
    WHERE username = p_username;
    LIMIT 1;

    IF v_not_found = 1 THEN
        SET p_is_valid   = 0;
        SET p_faculty_id = NULL;
    ELSE
        SET v_computed_hash = fn_hash_password(p_plain_password, v_salt);

        IF v_computed_hash = v_expected_hash THEN
            SET p_is_valid = 1;

            UPDATE credentials
            SET last_login = NOW()
            WHERE faculty_id = p_faculty_id;
        ELSE
            SET p_is_valid   = 0;
            SET p_faculty_id = NULL;
        END IF;
    END IF;
END;