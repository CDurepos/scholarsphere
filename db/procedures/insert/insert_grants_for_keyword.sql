DROP PROCEDURE IF EXISTS insert_grants_for_keyword
CREATE PROCEDURE insert_grants_for_keyword(
    p_grant_id  CHAR(36),
    p_name      VARCHAR(64)
)
BEGIN
    INSERT INTO grants_for_keyword(grant_id, name) 
    VALUES(p_grant_id, p_name);
END