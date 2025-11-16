DROP PROCEDURE IF EXISTS update_password;
CREATE PROCEDURE update_password(
    IN p_faculty_id     CHAR(36),
    IN p_old_password   VARCHAR(255),
    IN p_new_password   VARCHAR(255)
)
BEGIN
    DECLARE v_salt              VARCHAR(255);
    DECLARE v_expected_hash     VARCHAR(255);
    DECLARE v_old_hash          CHAR(64);

    -- RETRIEVE CURRENT PW AND SALT
    SELECT  password_salt, password_hash
    INTO    v_salt, v_expected_hash
    FROM    credentials
    WHERE   faculty_id = p_faculty_id;

    -- VERIFY OLD PW TO INPUT
    SET v_old_hash = hash_password(p_old_password, v_salt);
    IF v_old_hash <> v_expected_hash THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Old password is incorrect';
    END IF;

    -- UPDATE PASSWORD
    UPDATE credentials
    SET password_hash = hash_password(p_new_password, v_salt);
    WHERE faculty_id = p_faculty_id;
END;