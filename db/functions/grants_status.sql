DROP FUNCTION IF EXISTS grant_status;

CREATE FUNCTION grant_status(
    p_start_date  DATE,
    p_end_date    DATE
) RETURNS VARCHAR(16)
BEGIN
    IF p_start_date > CURDATE() THEN
        RETURN `UPCOMING`;
    END IF;

    IF p_start_date <= CURDATE() and p_end_date >= CURDATE() THEN
        RETURN `ACTIVE`;
    END IF;

    IF p_end_date < CURDATE() THEN
        RETURN `EXPIRED`;
    END IF;
END;