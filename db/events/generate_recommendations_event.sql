-- Written by Clayton Durepos

DELIMITER $$

/**
 * Scheduled event to generate faculty recommendations every 12 hours.
 * 
 * Runs the generate_all_recommendations procedure twice daily to keep
 * recommendations fresh as new faculty register and update their profiles.
 * 
 * Schedule: Every 12 hours, starting at 2 AM UTC
 */
DROP EVENT IF EXISTS generate_recommendations_event$$

CREATE EVENT generate_recommendations_event
ON SCHEDULE 
    EVERY 12 HOUR
    STARTS CURRENT_DATE + INTERVAL 2 HOUR
COMMENT 'Generate faculty recommendations every 12 hours'
DO
BEGIN
    CALL generate_all_recommendations();
END $$

DELIMITER ;

