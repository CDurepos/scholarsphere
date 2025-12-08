-- Written by Clayton Durepos

DELIMITER $$

/**
 * Updates an existing equipment record in the database.
 * 
 * Performs a partial update on an equipment record. Only non-NULL parameters
 * will update the corresponding fields; NULL parameters leave existing values
 * unchanged. The equipment_id is required to identify which record to update.
 * 
 * @param p_equipment_id    Required UUID of the equipment record to update
 * @param p_name            Optional new equipment name (NULL to keep existing)
 * @param p_description     Optional new description (NULL to keep existing)
 * @param p_availability    Optional new availability text (NULL to keep existing)
 * @param p_institution_id  Optional new institution UUID (NULL to keep existing)
 *                          If provided, the institution must exist in the database
 * 
 * @returns Result set containing:
 *   - equipment_id: UUID of the updated equipment record
 *   - action: Status message ('updated')
 * 
 * @throws SQLSTATE '45000' if equipment_id is NULL, if equipment_id doesn't exist,
 *                    or if p_institution_id is provided but doesn't exist
 */
CREATE PROCEDURE update_equipment (
    IN p_equipment_id    CHAR(36),
    IN p_name            VARCHAR(64),
    IN p_description     VARCHAR(2048),
    IN p_availability    VARCHAR(2048),
    IN p_institution_id  CHAR(36)
)
BEGIN
    DECLARE equipment_exists INT;
    DECLARE institution_exists INT;

    IF p_equipment_id IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'equipment_id is required for update_equipment';
    END IF;

    SELECT COUNT(*) INTO equipment_exists
    FROM equipment
    WHERE equipment_id = p_equipment_id;

    IF equipment_exists = 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'equipment_id does not exist';
    END IF;

    IF p_institution_id IS NOT NULL THEN
        SELECT COUNT(*) INTO institution_exists
        FROM institution
        WHERE institution_id = p_institution_id;

        IF institution_exists = 0 THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'institution_id does not exist';
        END IF;
    END IF;

    -- Update only the fields that are provided (non-NULL)
    -- Use conditional updates to preserve existing values when parameters are NULL
    UPDATE equipment
    SET
        name = IF(p_name IS NOT NULL, p_name, name),
        description = IF(p_description IS NOT NULL, p_description, description),
        availability = IF(p_availability IS NOT NULL, p_availability, availability),
        institution_id = IF(p_institution_id IS NOT NULL, p_institution_id, institution_id)
    WHERE equipment_id = p_equipment_id;

    SELECT p_equipment_id AS equipment_id, 'updated' AS action;
END $$

DELIMITER ;
