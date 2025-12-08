DELIMITER $$

/**
 * Recommend faculty in the same department (normalized comparison).
 * Priority: 9 | UI: "Same department"
 */
DROP PROCEDURE IF EXISTS recommend_by_shared_department$$
CREATE PROCEDURE recommend_by_shared_department()
BEGIN
    INSERT INTO faculty_recommended_to_faculty (
        source_faculty_id, target_faculty_id, recommendation_type, created_at
    )
    SELECT DISTINCT
        fd1.faculty_id, fd2.faculty_id, 'shared_department', NOW()
    FROM faculty_department fd1
    JOIN faculty_department fd2 
        ON normalize_department_name(fd1.department_name) = normalize_department_name(fd2.department_name)
    WHERE fd1.faculty_id <> fd2.faculty_id
      AND EXISTS (SELECT 1 FROM credentials c WHERE c.faculty_id = fd1.faculty_id)
    ON DUPLICATE KEY UPDATE
        recommendation_type = IF(VALUES(recommendation_type) < recommendation_type, 
                                 VALUES(recommendation_type), recommendation_type),
        updated_at = NOW();
END $$

DELIMITER ;
