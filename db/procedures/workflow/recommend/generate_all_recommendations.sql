DELIMITER $$

/**
 * Generate recommendations for all registered users.
 * 
 * Uses additive scoring: multiple matching criteria increase the total score.
 * Procedures run lowest-to-highest priority so the type reflects the best match.
 * 
 * Score reference:
 *   0.10 shared_institution     | 0.22 publication_to_grant  | 0.28 publication_to_keyword
 *   0.15 shared_department      | 0.23 grant_to_publication  | 0.29 keyword_to_publication
 *   0.20 shared_grant           | 0.25 grant_to_keyword      | 0.30 shared_keyword
 *                               | 0.26 keyword_to_grant      |
 */
DROP PROCEDURE IF EXISTS generate_all_recommendations$$
CREATE PROCEDURE generate_all_recommendations()
BEGIN
    CALL recommend_by_shared_institution();
    CALL recommend_by_shared_department();
    CALL recommend_by_shared_grant();
    CALL recommend_by_publication_to_grant();
    CALL recommend_by_grant_to_publication();
    CALL recommend_by_grant_to_keyword();
    CALL recommend_by_keyword_to_grant();
    CALL recommend_by_publication_to_keyword();
    CALL recommend_by_keyword_to_publication();
    CALL recommend_by_shared_keyword();
END $$

DELIMITER ;
