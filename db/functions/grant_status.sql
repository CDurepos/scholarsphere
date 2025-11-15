DROP FUNCTION IF EXISTS grant_status;

CREATE FUNCTION grant_status(
    start_date  DATE,
    end_date    DATE
) RETURNS VARCHAR(16)
BEGIN
    IF start_date > CURDATE() THEN
        RETURN `UPCOMING`;
    END IF;

    IF start_date <= CURDATE() and end_date >= CURDATE() THEN
        RETURN `ACTIVE`;
    END IF;

    IF end_date < CURDATE() THEN
        RETURN `EXPIRED`;
    END IF;
END;