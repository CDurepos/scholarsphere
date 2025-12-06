DELIMITER $$

/**
 * Recommend faculty who share a grant.
 * Score: 0.20 | UI: "Co-funded by same grant"
 */
DROP PROCEDURE IF EXISTS recommend_by_shared_grant$$
CREATE PROCEDURE recommend_by_shared_grant()
BEGIN
    INSERT INTO faculty_recommended_to_faculty (
        source_faculty_id, target_faculty_id, match_score, recommendation_type, created_at
    )
    SELECT DISTINCT
        ggf1.faculty_id, ggf2.faculty_id, 0.20, 'shared_grant', NOW()
    FROM grants_granted_to_faculty ggf1
    JOIN grants_granted_to_faculty ggf2 ON ggf1.grant_id = ggf2.grant_id
    WHERE ggf1.faculty_id <> ggf2.faculty_id
      AND EXISTS (SELECT 1 FROM credentials c WHERE c.faculty_id = ggf1.faculty_id)
    ON DUPLICATE KEY UPDATE
        match_score = match_score + VALUES(match_score),
        recommendation_type = VALUES(recommendation_type),
        updated_at = NOW();
END $$

DELIMITER ;
