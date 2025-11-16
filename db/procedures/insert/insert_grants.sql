DROP PROCEDURE IF EXISTS insert_into_grants;
CREATE PROCEDURE insert_into_grants(
    IN      p_grant_id      CHAR(36),
    IN      p_description   TEXT,
    IN      p_amount        DECIMAL(10,2),
    IN      p_start_date    DATE,
    IN      p_end_date      DATE
)

BEGIN
    INSERT INTO grants(
        grant_id, description, amount, start_date, end_date
    ) VALUES (
        p_grant_id, p_description, p_amount, p_start_date, p_end_date
    );
END;
