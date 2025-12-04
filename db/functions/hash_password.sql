DELIMITER $$

DROP FUNCTION IF EXISTS hash_password$$
CREATE FUNCTION hash_password(
    p_plain_text     VARCHAR(255),
    p_salt          VARCHAR(255)
) RETURNS CHAR(64)
DETERMINISTIC
BEGIN
    -- Hex-encoded SHA-256 = 64 characters
    RETURN SHA2(CONCAT(p_plain_text, p_salt), 256);
END $$

DELIMITER ;
