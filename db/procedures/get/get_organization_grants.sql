DROP PROCEDURE IF EXISTS get_grants_by_organization;
CREATE PROCEDURE get_grants_by_organization(
    IN  p_name  VARCHAR(256)
)
BEGIN   
    SELECT  g.*
            grants_status(g.start_date, g.end_date) AS derived_status,
    FROM    grants AS g
    JOIN    grants_organization AS go
            ON g.grant_id = go.grant_id
    WHERE go.name = p_name
    ORDER BY g.start_date DESC;
END;