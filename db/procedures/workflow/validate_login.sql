DELIMITER $$

/**
 * Validates user login credentials and updates last login timestamp.
 * 
 * This workflow procedure authenticates a user by verifying their username
 * and password. If authentication is successful, it updates the last_login
 * timestamp and returns the faculty_id. The password is verified using
 * the stored salt and hash.
 * 
 * @param p_username    Required username to authenticate
 * @param p_password    Required password (plain text, will be hashed for comparison)
 * @param p_faculty_id  OUT parameter that receives the faculty_id if login succeeds
 *                      Returns NULL if login fails
 * @param p_status_code OUT parameter indicating the login result:
 *                      - 0: Login successful
 *                      - 1: Invalid password
 *                      - 2: Username not found
 *                      - -1: Default/error state
 * 
 * @returns No result set. Check the OUT parameters for login status.
 * 
 * @throws SQLSTATE '45000' if username or password is NULL
 */
DROP PROCEDURE IF EXISTS validate_login;
CREATE PROCEDURE validate_login(
    IN  p_username      VARCHAR(255),
    IN  p_password      VARCHAR(255),
    OUT p_faculty_id    CHAR(36),
    OUT p_status_code   TINYINT
)
BEGIN
    DECLARE v_salt          VARCHAR(255);
    DECLARE v_expected_hash VARCHAR(255);
    DECLARE v_computed_hash CHAR(64);

    IF p_username IS NULL OR p_password IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'username and password are required for validate_login';
    END IF;

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
