DELIMITER $$

/**
 * Generate recommendations for a single faculty member (called on signup).
 * Uses the same additive scoring logic as generate_all_recommendations.
 */
DROP PROCEDURE IF EXISTS generate_recommendations_for_faculty$$
CREATE PROCEDURE generate_recommendations_for_faculty(IN p_faculty_id CHAR(36))
BEGIN
    IF NOT EXISTS (SELECT 1 FROM credentials WHERE faculty_id = p_faculty_id) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Faculty must have credentials';
    END IF;

    INSERT INTO faculty_recommended_to_faculty (source_faculty_id, target_faculty_id, match_score, recommendation_type, created_at)
    SELECT DISTINCT p_faculty_id, fwi2.faculty_id, 0.10, 'shared_institution', NOW()
    FROM faculty_works_at_institution fwi1
    JOIN faculty_works_at_institution fwi2 ON fwi1.institution_id = fwi2.institution_id
    WHERE fwi1.faculty_id = p_faculty_id AND fwi2.faculty_id <> p_faculty_id
      AND fwi1.end_date IS NULL AND fwi2.end_date IS NULL
    ON DUPLICATE KEY UPDATE match_score = match_score + VALUES(match_score), recommendation_type = VALUES(recommendation_type), updated_at = NOW();

    INSERT INTO faculty_recommended_to_faculty (source_faculty_id, target_faculty_id, match_score, recommendation_type, created_at)
    SELECT DISTINCT p_faculty_id, fd2.faculty_id, 0.15, 'shared_department', NOW()
    FROM faculty_department fd1
    JOIN faculty_department fd2 ON LOWER(TRIM(fd1.department_name)) = LOWER(TRIM(fd2.department_name))
    WHERE fd1.faculty_id = p_faculty_id AND fd2.faculty_id <> p_faculty_id
    ON DUPLICATE KEY UPDATE match_score = match_score + VALUES(match_score), recommendation_type = VALUES(recommendation_type), updated_at = NOW();

    INSERT INTO faculty_recommended_to_faculty (source_faculty_id, target_faculty_id, match_score, recommendation_type, created_at)
    SELECT DISTINCT p_faculty_id, ggf2.faculty_id, 0.20, 'shared_grant', NOW()
    FROM grants_granted_to_faculty ggf1
    JOIN grants_granted_to_faculty ggf2 ON ggf1.grant_id = ggf2.grant_id
    WHERE ggf1.faculty_id = p_faculty_id AND ggf2.faculty_id <> p_faculty_id
    ON DUPLICATE KEY UPDATE match_score = match_score + VALUES(match_score), recommendation_type = VALUES(recommendation_type), updated_at = NOW();

    INSERT INTO faculty_recommended_to_faculty (source_faculty_id, target_faculty_id, match_score, recommendation_type, created_at)
    SELECT DISTINCT p_faculty_id, ggf.faculty_id, 0.22, 'publication_to_grant', NOW()
    FROM publication_authored_by_faculty paf
    JOIN publication_explores_keyword pek ON paf.publication_id = pek.publication_id
    JOIN grants_for_keyword gfk ON LOWER(TRIM(pek.name)) = LOWER(TRIM(gfk.name))
    JOIN grants_granted_to_faculty ggf ON gfk.grant_id = ggf.grant_id
    WHERE paf.faculty_id = p_faculty_id AND ggf.faculty_id <> p_faculty_id
    ON DUPLICATE KEY UPDATE match_score = match_score + VALUES(match_score), recommendation_type = VALUES(recommendation_type), updated_at = NOW();

    INSERT INTO faculty_recommended_to_faculty (source_faculty_id, target_faculty_id, match_score, recommendation_type, created_at)
    SELECT DISTINCT p_faculty_id, paf.faculty_id, 0.23, 'grant_to_publication', NOW()
    FROM grants_granted_to_faculty ggf
    JOIN grants_for_keyword gfk ON ggf.grant_id = gfk.grant_id
    JOIN publication_explores_keyword pek ON LOWER(TRIM(gfk.name)) = LOWER(TRIM(pek.name))
    JOIN publication_authored_by_faculty paf ON pek.publication_id = paf.publication_id
    WHERE ggf.faculty_id = p_faculty_id AND paf.faculty_id <> p_faculty_id
    ON DUPLICATE KEY UPDATE match_score = match_score + VALUES(match_score), recommendation_type = VALUES(recommendation_type), updated_at = NOW();

    INSERT INTO faculty_recommended_to_faculty (source_faculty_id, target_faculty_id, match_score, recommendation_type, created_at)
    SELECT DISTINCT p_faculty_id, frk.faculty_id, 0.25, 'grant_to_keyword', NOW()
    FROM grants_granted_to_faculty ggf
    JOIN grants_for_keyword gfk ON ggf.grant_id = gfk.grant_id
    JOIN faculty_researches_keyword frk ON LOWER(TRIM(gfk.name)) = LOWER(TRIM(frk.name))
    WHERE ggf.faculty_id = p_faculty_id AND frk.faculty_id <> p_faculty_id
    ON DUPLICATE KEY UPDATE match_score = match_score + VALUES(match_score), recommendation_type = VALUES(recommendation_type), updated_at = NOW();

    INSERT INTO faculty_recommended_to_faculty (source_faculty_id, target_faculty_id, match_score, recommendation_type, created_at)
    SELECT DISTINCT p_faculty_id, ggf.faculty_id, 0.26, 'keyword_to_grant', NOW()
    FROM faculty_researches_keyword frk
    JOIN grants_for_keyword gfk ON LOWER(TRIM(frk.name)) = LOWER(TRIM(gfk.name))
    JOIN grants_granted_to_faculty ggf ON gfk.grant_id = ggf.grant_id
    WHERE frk.faculty_id = p_faculty_id AND ggf.faculty_id <> p_faculty_id
    ON DUPLICATE KEY UPDATE match_score = match_score + VALUES(match_score), recommendation_type = VALUES(recommendation_type), updated_at = NOW();

    INSERT INTO faculty_recommended_to_faculty (source_faculty_id, target_faculty_id, match_score, recommendation_type, created_at)
    SELECT DISTINCT p_faculty_id, frk.faculty_id, 0.28, 'publication_to_keyword', NOW()
    FROM publication_authored_by_faculty paf
    JOIN publication_explores_keyword pek ON paf.publication_id = pek.publication_id
    JOIN faculty_researches_keyword frk ON LOWER(TRIM(pek.name)) = LOWER(TRIM(frk.name))
    WHERE paf.faculty_id = p_faculty_id AND frk.faculty_id <> p_faculty_id
    ON DUPLICATE KEY UPDATE match_score = match_score + VALUES(match_score), recommendation_type = VALUES(recommendation_type), updated_at = NOW();

    INSERT INTO faculty_recommended_to_faculty (source_faculty_id, target_faculty_id, match_score, recommendation_type, created_at)
    SELECT DISTINCT p_faculty_id, paf.faculty_id, 0.29, 'keyword_to_publication', NOW()
    FROM faculty_researches_keyword frk
    JOIN publication_explores_keyword pek ON LOWER(TRIM(frk.name)) = LOWER(TRIM(pek.name))
    JOIN publication_authored_by_faculty paf ON pek.publication_id = paf.publication_id
    WHERE frk.faculty_id = p_faculty_id AND paf.faculty_id <> p_faculty_id
    ON DUPLICATE KEY UPDATE match_score = match_score + VALUES(match_score), recommendation_type = VALUES(recommendation_type), updated_at = NOW();

    INSERT INTO faculty_recommended_to_faculty (source_faculty_id, target_faculty_id, match_score, recommendation_type, created_at)
    SELECT DISTINCT p_faculty_id, frk2.faculty_id, 0.30, 'shared_keyword', NOW()
    FROM faculty_researches_keyword frk1
    JOIN faculty_researches_keyword frk2 ON LOWER(TRIM(frk1.name)) = LOWER(TRIM(frk2.name))
    WHERE frk1.faculty_id = p_faculty_id AND frk2.faculty_id <> p_faculty_id
    ON DUPLICATE KEY UPDATE match_score = match_score + VALUES(match_score), recommendation_type = VALUES(recommendation_type), updated_at = NOW();
END $$

DELIMITER ;
