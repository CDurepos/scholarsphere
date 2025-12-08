-- Written by Clayton Durepos, Aidan Bell

DELIMITER $$

/**
 * Updates a faculty member's password.
 * 
 * Changes the password for a faculty member's credentials. The old password
 * must be provided and verified before the new password is set. The new
 * password is hashed using the existing salt for security.
 * 
 * @param p_faculty_id    Required UUID of the faculty member
 * @param p_old_password  Required current password (plain text, for verification)
 * @param p_new_password  Required new password (plain text, will be hashed)
 * 
 * @returns No result set. Use validate_login to test the new credentials.
 * 
 * @throws SQLSTATE '45000' if any parameter is NULL
 * @throws SQLSTATE '45000' if faculty_id doesn't exist or has no credentials
 * @throws SQLSTATE '45000' if old_password is incorrect
 */
DROP PROCEDURE IF EXISTS update_password$$
CREATE PROCEDURE update_password(
    IN p_faculty_id     CHAR(36),
    IN p_old_password   VARCHAR(255),
    IN p_new_password   VARCHAR(255)
)
BEGIN
    DECLARE v_salt              VARCHAR(255);
    DECLARE v_expected_hash     VARCHAR(255);
    DECLARE v_old_hash          CHAR(64);

    IF p_faculty_id IS NULL OR p_old_password IS NULL OR p_new_password IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'faculty_id, old_password, and new_password are required';
    END IF;

    -- RETRIEVE CURRENT PW AND SALT
    SELECT  password_salt, password_hash
    INTO    v_salt, v_expected_hash
    FROM    credentials
    WHERE   faculty_id = p_faculty_id;

    IF v_salt IS NULL OR v_expected_hash IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Credentials not found for this faculty_id';
    END IF;

    -- VERIFY OLD PW TO INPUT
    SET v_old_hash = hash_password(p_old_password, v_salt);
    IF v_old_hash <> v_expected_hash THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Old password is incorrect';
    END IF;

    -- UPDATE PASSWORD
    UPDATE credentials
    SET password_hash = hash_password(p_new_password, v_salt)
    WHERE faculty_id = p_faculty_id;
END $$
DELIMITER ;
