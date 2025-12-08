-- Written by Clayton Durepos

DELIMITER $$

/**
 * Recommend faculty who share research keywords.
 * Priority: 1 (highest) | UI: "Similar research interests"
 */
DROP PROCEDURE IF EXISTS recommend_by_shared_keyword$$
CREATE PROCEDURE recommend_by_shared_keyword()
BEGIN
    INSERT INTO faculty_recommended_to_faculty (
        source_faculty_id, target_faculty_id, recommendation_type, created_at
    )
    SELECT DISTINCT
        frk1.faculty_id, frk2.faculty_id, 'shared_keyword', NOW()
    FROM faculty_researches_keyword frk1
    JOIN faculty_researches_keyword frk2 ON LOWER(TRIM(frk1.name)) = LOWER(TRIM(frk2.name))
    WHERE frk1.faculty_id <> frk2.faculty_id
      AND EXISTS (SELECT 1 FROM credentials c WHERE c.faculty_id = frk1.faculty_id)
    ON DUPLICATE KEY UPDATE
        recommendation_type = IF(VALUES(recommendation_type) < recommendation_type, 
                                 VALUES(recommendation_type), recommendation_type),
        updated_at = NOW();
END $$

DELIMITER ;
