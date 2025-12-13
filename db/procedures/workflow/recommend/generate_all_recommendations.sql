-- Written by Clayton Durepos

DELIMITER $$

/**
 * Generate recommendations for all registered users.
 * Runs lowest-to-highest priority so higher priority types overwrite.
 * 
 * Priority (ENUM order):
 *   1. shared_keyword
 *   2. keyword_to_publication
 *   3. publication_to_keyword
 *   4. shared_department
 */
DROP PROCEDURE IF EXISTS generate_all_recommendations$$
CREATE PROCEDURE generate_all_recommendations()
BEGIN
    CALL recommend_by_shared_department();
    CALL recommend_by_publication_to_keyword();
    CALL recommend_by_keyword_to_publication();
    CALL recommend_by_shared_keyword();
END $$

DELIMITER ;
