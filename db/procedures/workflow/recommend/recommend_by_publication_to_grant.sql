DELIMITER $$

/**
 * Recommend: source published on keyword X, target has grant for X.
 * Score: 0.22 | UI: "Has funding for your publication topics"
 */
DROP PROCEDURE IF EXISTS recommend_by_publication_to_grant$$
CREATE PROCEDURE recommend_by_publication_to_grant()
BEGIN
    INSERT INTO faculty_recommended_to_faculty (
        source_faculty_id, target_faculty_id, match_score, recommendation_type, created_at
    )
    SELECT DISTINCT
        paf.faculty_id, ggf.faculty_id, 0.22, 'publication_to_grant', NOW()
    FROM publication_authored_by_faculty paf
    JOIN publication_explores_keyword pek ON paf.publication_id = pek.publication_id
    JOIN grants_for_keyword gfk ON LOWER(TRIM(pek.name)) = LOWER(TRIM(gfk.name))
    JOIN grants_granted_to_faculty ggf ON gfk.grant_id = ggf.grant_id
    WHERE paf.faculty_id <> ggf.faculty_id
      AND EXISTS (SELECT 1 FROM credentials c WHERE c.faculty_id = paf.faculty_id)
    ON DUPLICATE KEY UPDATE
        match_score = match_score + VALUES(match_score),
        recommendation_type = VALUES(recommendation_type),
        updated_at = NOW();
END $$

DELIMITER ;
