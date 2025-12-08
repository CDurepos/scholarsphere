DELIMITER $$

/**
 * Recommend: source has grant for keyword X, target researches X.
 * Priority: 5 | UI: "Researches your grant topics"
 */
DROP PROCEDURE IF EXISTS recommend_by_grant_to_keyword$$
CREATE PROCEDURE recommend_by_grant_to_keyword()
BEGIN
    INSERT INTO faculty_recommended_to_faculty (
        source_faculty_id, target_faculty_id, recommendation_type, created_at
    )
    SELECT DISTINCT
        ggf.faculty_id, frk.faculty_id, 'grant_to_keyword', NOW()
    FROM grants_granted_to_faculty ggf
    JOIN grants_for_keyword gfk ON ggf.grant_id = gfk.grant_id
    JOIN faculty_researches_keyword frk ON LOWER(TRIM(gfk.name)) = LOWER(TRIM(frk.name))
    WHERE ggf.faculty_id <> frk.faculty_id
      AND EXISTS (SELECT 1 FROM credentials c WHERE c.faculty_id = ggf.faculty_id)
    ON DUPLICATE KEY UPDATE
        recommendation_type = IF(VALUES(recommendation_type) < recommendation_type, 
                                 VALUES(recommendation_type), recommendation_type),
        updated_at = NOW();
END $$

DELIMITER ;
