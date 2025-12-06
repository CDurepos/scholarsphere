DELIMITER $$

/**
 * Recommend faculty at the same institution.
 * Score: 0.10 | UI: "Same institution"
 */
DROP PROCEDURE IF EXISTS recommend_by_shared_institution$$
CREATE PROCEDURE recommend_by_shared_institution()
BEGIN
    INSERT INTO faculty_recommended_to_faculty (
        source_faculty_id, target_faculty_id, match_score, recommendation_type, created_at
    )
    SELECT DISTINCT
        fwi1.faculty_id, fwi2.faculty_id, 0.10, 'shared_institution', NOW()
    FROM faculty_works_at_institution fwi1
    JOIN faculty_works_at_institution fwi2 ON fwi1.institution_id = fwi2.institution_id
    WHERE fwi1.faculty_id <> fwi2.faculty_id
      AND fwi1.end_date IS NULL
      AND fwi2.end_date IS NULL
      AND EXISTS (SELECT 1 FROM credentials c WHERE c.faculty_id = fwi1.faculty_id)
    ON DUPLICATE KEY UPDATE
        match_score = match_score + VALUES(match_score),
        recommendation_type = VALUES(recommendation_type),
        updated_at = NOW();
END $$

DELIMITER ;
