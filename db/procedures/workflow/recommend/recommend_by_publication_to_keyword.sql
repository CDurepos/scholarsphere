DELIMITER $$

/**
 * Recommend: source published on keyword X, target researches X.
 * Score: 0.28 | UI: "Researches your publication topics"
 */
DROP PROCEDURE IF EXISTS recommend_by_publication_to_keyword$$
CREATE PROCEDURE recommend_by_publication_to_keyword()
BEGIN
    INSERT INTO faculty_recommended_to_faculty (
        source_faculty_id, target_faculty_id, match_score, recommendation_type, created_at
    )
    SELECT DISTINCT
        paf.faculty_id, frk.faculty_id, 0.28, 'publication_to_keyword', NOW()
    FROM publication_authored_by_faculty paf
    JOIN publication_explores_keyword pek ON paf.publication_id = pek.publication_id
    JOIN faculty_researches_keyword frk ON LOWER(TRIM(pek.name)) = LOWER(TRIM(frk.name))
    WHERE paf.faculty_id <> frk.faculty_id
      AND EXISTS (SELECT 1 FROM credentials c WHERE c.faculty_id = paf.faculty_id)
    ON DUPLICATE KEY UPDATE
        match_score = match_score + VALUES(match_score),
        recommendation_type = VALUES(recommendation_type),
        updated_at = NOW();
END $$

DELIMITER ;
