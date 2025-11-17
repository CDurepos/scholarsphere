DELIMITER $$

/**
 * Registers login credentials for a faculty member.
 * 
 * Creates a new credentials record for a faculty member, allowing them to
 * log into the system. The password is hashed using a salt for security.
 * Each faculty member can only have one set of credentials, and each
 * username must be unique across all users.
 * 
 * @param p_faculty_id  Required UUID of the faculty member
 * @param p_username    Required username (must be unique, max 255 characters)
 * @param p_password    Required plain text password (will be hashed and salted)
 * 
 * @returns No result set. Use validate_login to test the credentials.
 * 
 * @throws SQLSTATE '45000' if username already exists
 * @throws SQLSTATE '45000' if credentials already exist for this faculty_id
 * @throws SQLSTATE '23000' if faculty_id doesn't exist (foreign key constraint)
 */
DROP PROCEDURE IF EXISTS register_credentials;
CREATE PROCEDURE register_credentials(
    IN p_faculty_id CHAR(36),
    IN p_username VARCHAR(255),
    IN p_password VARCHAR(255)
)

BEGIN
    -- SALT & HASH FOR PW
    DECLARE p_salt VARCHAR(255);
    DECLARE p_hash CHAR(64);

    -- ENFORCE UNIQUE USERNAME
    IF EXISTS (SELECT 1 FROM credentials WHERE username = p_username) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Username already exists';
    END IF;

    -- FORCE ONE SET OF CREDENTIALS PER FACULTY
    IF EXISTS (SELECT 1 FROM credentials WHERE faculty_id = p_faculty_id) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Credentials already registered for this faculty';
    END IF;

    -- GENERATE SALT & HASH
    SET p_salt = UUID();
    SET p_hash = hash_password(p_password, p_salt);

    INSERT INTO credentials (faculty_id, username, password_hash, password_salt, last_login)
    VALUES (p_faculty_id, p_username, p_hash, p_salt, NULL);
END $$
