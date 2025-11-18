DELIMITER $$

/**
 * Deletes an equipment record from the database.
 * 
 * Removes the equipment record identified by the provided equipment_id.
 * Note: This operation may fail if there are foreign key constraints from
 * related tables depending on the database schema configuration.
 * 
 * @param p_equipment_id  Required UUID of the equipment record to delete.
 * 
 * @returns Result set containing:
 *   - equipment_id: UUID of the deleted equipment record
 *   - action: Status message ('deleted')
 * 
 * @throws SQLSTATE '45000' if equipment_id is NULL
 */
CREATE PROCEDURE delete_equipment (
    IN p_equipment_id CHAR(36)
)
BEGIN
    IF p_equipment_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'equipment_id is required for delete_equipment';
    END IF;

    DELETE FROM equipment
    WHERE equipment_id = p_equipment_id;

    SELECT p_equipment_id AS equipment_id, 'deleted' AS action;
END $$

DELIMITER ;


DELIMITER ;
