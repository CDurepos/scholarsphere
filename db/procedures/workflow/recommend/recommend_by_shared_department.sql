DELIMITER $$

/**
 * Recommend faculty in the same department (case-insensitive match).
 * Score: 0.15 | UI: "Same department"
 */
DROP PROCEDURE IF EXISTS recommend_by_shared_department$$
CREATE PROCEDURE recommend_by_shared_department()
BEGIN
    INSERT INTO faculty_recommended_to_faculty (
        source_faculty_id, target_faculty_id, match_score, recommendation_type, created_at
    )
    SELECT DISTINCT
        fd1.faculty_id, fd2.faculty_id, 0.15, 'shared_department', NOW()
    FROM faculty_department fd1
    JOIN faculty_department fd2 ON LOWER(TRIM(fd1.department_name)) = LOWER(TRIM(fd2.department_name))
    WHERE fd1.faculty_id <> fd2.faculty_id
      AND EXISTS (SELECT 1 FROM credentials c WHERE c.faculty_id = fd1.faculty_id)
    ON DUPLICATE KEY UPDATE
        match_score = match_score + VALUES(match_score),
        recommendation_type = VALUES(recommendation_type),
        updated_at = NOW();
END $$

DELIMITER ;
