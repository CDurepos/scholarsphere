DROP FUNCTION IF EXISTS is_grant_active;

CREATE FUNCTION is_grant_active(
    start_date DATE,
    end_date   DATE
) RETURNS BOOLEAN
BEGIN
    RETURN grant_status(start_date, end_date) = `ACTIVE`;
END;