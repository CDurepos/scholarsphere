DROP PROCEDURE IF EXISTS recommend_faculty_by_grants;
DELIMITER $$

CREATE PROCEDURE recommend_faculty_grants()
BEGIN

    -- INSERT directional recommendations
    INSERT INTO faculty_recommended_to_faculty (
        source_faculty_id,
        target_faculty_id,
        match_score,
        created_at
    )
    SELECT
        g1.faculty_id      AS source_faculty_id,
        g2.faculty_id      AS target_faculty_id,
        NULL               AS match_score,
        CURDATE()          AS created_at
    FROM grants_granted_to_faculty AS g1
    JOIN grants_granted_to_faculty AS g2
         ON g1.grant_id = g2.grant_id
    WHERE g1.faculty_id <> g2.faculty_id

END$$
DELIMITER;