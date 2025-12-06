DELIMITER $$

/**
 * Recommend: source researches keyword X, target has grant for X.
 * Score: 0.26 | UI: "Has funding in your research area"
 */
DROP PROCEDURE IF EXISTS recommend_by_keyword_to_grant$$
CREATE PROCEDURE recommend_by_keyword_to_grant()
BEGIN
    INSERT INTO faculty_recommended_to_faculty (
        source_faculty_id, target_faculty_id, match_score, recommendation_type, created_at
    )
    SELECT DISTINCT
        frk.faculty_id, ggf.faculty_id, 0.26, 'keyword_to_grant', NOW()
    FROM faculty_researches_keyword frk
    JOIN grants_for_keyword gfk ON LOWER(TRIM(frk.name)) = LOWER(TRIM(gfk.name))
    JOIN grants_granted_to_faculty ggf ON gfk.grant_id = ggf.grant_id
    WHERE frk.faculty_id <> ggf.faculty_id
      AND EXISTS (SELECT 1 FROM credentials c WHERE c.faculty_id = frk.faculty_id)
    ON DUPLICATE KEY UPDATE
        match_score = match_score + VALUES(match_score),
        recommendation_type = VALUES(recommendation_type),
        updated_at = NOW();
END $$

DELIMITER ;
