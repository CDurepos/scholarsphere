DELIMITER $$

/**
 * Recommend: source has grant for keyword X, target published on X.
 * Priority: 6 | UI: "Published on your grant topics"
 */
DROP PROCEDURE IF EXISTS recommend_by_grant_to_publication$$
CREATE PROCEDURE recommend_by_grant_to_publication()
BEGIN
    INSERT INTO faculty_recommended_to_faculty (
        source_faculty_id, target_faculty_id, recommendation_type, created_at
    )
    SELECT DISTINCT
        ggf.faculty_id, paf.faculty_id, 'grant_to_publication', NOW()
    FROM grants_granted_to_faculty ggf
    JOIN grants_for_keyword gfk ON ggf.grant_id = gfk.grant_id
    JOIN publication_explores_keyword pek ON LOWER(TRIM(gfk.name)) = LOWER(TRIM(pek.name))
    JOIN publication_authored_by_faculty paf ON pek.publication_id = paf.publication_id
    WHERE ggf.faculty_id <> paf.faculty_id
      AND EXISTS (SELECT 1 FROM credentials c WHERE c.faculty_id = ggf.faculty_id)
    ON DUPLICATE KEY UPDATE
        recommendation_type = IF(VALUES(recommendation_type) < recommendation_type, 
                                 VALUES(recommendation_type), recommendation_type),
        updated_at = NOW();
END $$

DELIMITER ;
