-- Written by Clayton Durepos

DELIMITER $$

/**
 * Generate recommendations for a single faculty member (called on signup).
 */
DROP PROCEDURE IF EXISTS generate_recommendations_for_faculty$$
CREATE PROCEDURE generate_recommendations_for_faculty(IN p_faculty_id CHAR(36))
BEGIN
    IF NOT EXISTS (SELECT 1 FROM credentials WHERE faculty_id = p_faculty_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Faculty must have credentials';
    END IF;

    INSERT INTO faculty_recommended_to_faculty (source_faculty_id, target_faculty_id, recommendation_type, created_at)
    SELECT DISTINCT p_faculty_id, fd2.faculty_id, 'shared_department', NOW()
    FROM faculty_department fd1
    JOIN faculty_department fd2 ON normalize_department_name(fd1.department_name) = normalize_department_name(fd2.department_name)
    WHERE fd1.faculty_id = p_faculty_id AND fd2.faculty_id <> p_faculty_id
    ON DUPLICATE KEY UPDATE
        recommendation_type = IF(VALUES(recommendation_type) < recommendation_type, VALUES(recommendation_type), recommendation_type),
        updated_at = NOW();

    INSERT INTO faculty_recommended_to_faculty (source_faculty_id, target_faculty_id, recommendation_type, created_at)
    SELECT DISTINCT p_faculty_id, frk.faculty_id, 'publication_to_keyword', NOW()
    FROM publication_authored_by_faculty paf
    JOIN publication_explores_keyword pek ON paf.publication_id = pek.publication_id
    JOIN faculty_researches_keyword frk ON LOWER(TRIM(pek.name)) = LOWER(TRIM(frk.name))
    WHERE paf.faculty_id = p_faculty_id AND frk.faculty_id <> p_faculty_id
    ON DUPLICATE KEY UPDATE
        recommendation_type = IF(VALUES(recommendation_type) < recommendation_type, VALUES(recommendation_type), recommendation_type),
        updated_at = NOW();

    INSERT INTO faculty_recommended_to_faculty (source_faculty_id, target_faculty_id, recommendation_type, created_at)
    SELECT DISTINCT p_faculty_id, paf.faculty_id, 'keyword_to_publication', NOW()
    FROM faculty_researches_keyword frk
    JOIN publication_explores_keyword pek ON LOWER(TRIM(frk.name)) = LOWER(TRIM(pek.name))
    JOIN publication_authored_by_faculty paf ON pek.publication_id = paf.publication_id
    WHERE frk.faculty_id = p_faculty_id AND paf.faculty_id <> p_faculty_id
    ON DUPLICATE KEY UPDATE
        recommendation_type = IF(VALUES(recommendation_type) < recommendation_type, VALUES(recommendation_type), recommendation_type),
        updated_at = NOW();

    INSERT INTO faculty_recommended_to_faculty (source_faculty_id, target_faculty_id, recommendation_type, created_at)
    SELECT DISTINCT p_faculty_id, frk2.faculty_id, 'shared_keyword', NOW()
    FROM faculty_researches_keyword frk1
    JOIN faculty_researches_keyword frk2 ON LOWER(TRIM(frk1.name)) = LOWER(TRIM(frk2.name))
    WHERE frk1.faculty_id = p_faculty_id AND frk2.faculty_id <> p_faculty_id
    ON DUPLICATE KEY UPDATE
        recommendation_type = IF(VALUES(recommendation_type) < recommendation_type, VALUES(recommendation_type), recommendation_type),
        updated_at = NOW();
END $$

DELIMITER ;
