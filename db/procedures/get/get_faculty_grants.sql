DROP PROCEDURE IF EXISTS get_grants_granted_to_faculty;
CREATE PROCEDURE get_grants_granted_to_faculty(
    IN p_faculty_id     CHAR(36)    NOT NULL   
)
BEGIN
    SELECT  g.*,
            grants_status(g.start_date, g.end_date) AS derived_status
    FROM    grants AS g
    JOIN    grants_granted_to_faculty AS ggf
            ON g.grant_id = ggf.grant_id
    WHERE
            ggf.faculty_id = p_faculty_id
    ORDER BY g.start_date;
END;