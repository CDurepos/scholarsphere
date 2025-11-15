DROP PROCEDURE IF EXISTS change_password;
CREATE PROCEDURE change_password(
    IN p_faculty_id CHAR(36),
    IN p_old_password VARCHAR(255),
    IN p_new_password VARCHAR(255)
)
BEGIN
    DECLARE v_salt          VARCHAR(255);
    DECLARE v_expected_hash VARCHAR(255);
    DECLARE v_old_hash CHAR(64);

    SELECT password_salt, password_hash
    INTO v_salt, v_expect_hash
    FROM credentials
    WHERE faculty_id = p_faculty_id;

    SET v_old_hash = SHA2(CONCAT(p_old_password, v_salt), 256);
    IF v_old_hash <> v_expected_hash THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Old password is incorrect';
    END IF;

    UPDATE credentials
    SET password_hash = SHA2(CONCAT(p_new_password, v_salt), 256)
    WHERE faculty_id = p_faculty_id;
END;