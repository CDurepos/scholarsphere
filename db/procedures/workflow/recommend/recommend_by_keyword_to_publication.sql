-- Written by Clayton Durepos

DELIMITER $$

/**
 * Recommend: source researches keyword X, target published on X.
 * Priority: 2 | UI: "Published in your research area"
 */
DROP PROCEDURE IF EXISTS recommend_by_keyword_to_publication$$
CREATE PROCEDURE recommend_by_keyword_to_publication()
BEGIN
    INSERT INTO faculty_recommended_to_faculty (
        source_faculty_id, target_faculty_id, recommendation_type, created_at
    )
    SELECT DISTINCT
        frk.faculty_id, paf.faculty_id, 'keyword_to_publication', NOW()
    FROM faculty_researches_keyword frk
    JOIN publication_explores_keyword pek ON LOWER(TRIM(frk.name)) = LOWER(TRIM(pek.name))
    JOIN publication_authored_by_faculty paf ON pek.publication_id = paf.publication_id
    WHERE frk.faculty_id <> paf.faculty_id
      AND EXISTS (SELECT 1 FROM credentials c WHERE c.faculty_id = frk.faculty_id)
    ON DUPLICATE KEY UPDATE
        recommendation_type = IF(VALUES(recommendation_type) < recommendation_type, 
                                 VALUES(recommendation_type), recommendation_type),
        updated_at = NOW();
END $$

DELIMITER ;
