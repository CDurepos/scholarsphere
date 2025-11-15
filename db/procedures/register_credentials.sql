DROP FUNCTION IF EXISTS register_credentials;
CREATE PROCEDURE register_credentials(
    IN p_faculty_id CHAR(36),
    IN p_username VARCHAR(255),
    IN p_password VARCHAR(255)
)

BEGIN
    DECLARE p_salt VARCHAR(255);
    DECLARE p_hash CHAR(64);

    IF EXISTS (SELECT 1 FROM credentials WHERE username = p_username) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Username already exists';
    END IF;

    IF EXISTS (SELECT 1 FROM faculty where faculty_id = p_faculty_id) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Credentials already registered for this faculty';
    END IF;

    SET p_salt = UUID();
    set p_hash = SHA2(CONCAT(p_password, p_salt), 256);

    INSERT INTO credentials (faculty_id, username, password_hash, password_salt, last_login)
    VALUES (p_faculty_id, p_username, p_hash, p_salt, NULL);
END;
