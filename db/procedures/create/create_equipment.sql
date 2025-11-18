DELIMITER $$

/**
 * Creates a new equipment record in the database.
 * 
 * Inserts a new equipment record with the provided information. All parameters
 * are required except description, which is optional. The equipment must be
 * associated with an existing institution.
 * 
 * @param p_equipment_id    Required UUID for the equipment record
 * @param p_name            Required equipment name (max 64 characters)
 * @param p_description     Optional description of the equipment (max 2048 characters)
 * @param p_availability    Required availability information (max 2048 characters)
 *                          Describes when and how the equipment is available
 * @param p_institution_id  Required UUID of the institution that owns the equipment
 *                          Must reference an existing institution record
 * 
 * @throws SQLSTATE '23000' if institution_id doesn't exist (foreign key constraint)
 * @throws SQLSTATE '23000' if equipment_id already exists (primary key constraint)
 */
DROP PROCEDURE IF EXISTS create_equipment;
CREATE PROCEDURE create_equipment(
    IN p_equipment_id CHAR(36),
    IN p_name VARCHAR(64),
    IN p_description VARCHAR(2048),
    IN p_availability VARCHAR(2048),
    IN p_institution_id CHAR(36)    
)
BEGIN
    INSERT INTO equipment (
        equipment_id, 
        name, 
        description,
        availability, 
        institution_id
    ) VALUES (
        p_equipment_id, 
        p_name, 
        p_description, 
        p_availability, 
        p_institution_id)
    ;
END $$

DELIMITER ;