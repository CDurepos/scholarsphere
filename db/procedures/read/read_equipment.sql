-- Written by Clayton Durepos

DELIMITER $$

/**
 * Retrieves equipment records from the database with optional filtering.
 * 
 * Returns equipment information based on the provided filters. If both
 * parameters are NULL, all equipment records in the database are returned.
 * Results are ordered alphabetically by equipment name.
 * 
 * @param p_equipment_id     Optional UUID of a specific equipment item to retrieve.
 *                          When provided, only that equipment record is returned.
 * @param p_institution_id  Optional UUID of an institution to filter by.
 *                          When provided, only equipment belonging to that institution is returned.
 * 
 * @returns Result set containing all columns from the equipment table:
 *   - equipment_id
 *   - name
 *   - description
 *   - availability
 *   - institution_id
 * 
 * If both parameters are NULL, returns all equipment records ordered by name.
 */
CREATE PROCEDURE read_equipment (
    IN p_equipment_id   CHAR(36),
    IN p_institution_id CHAR(36)
)
BEGIN
    SELECT e.*
    FROM equipment e
    WHERE (p_equipment_id IS NULL OR e.equipment_id = p_equipment_id)
      AND (p_institution_id IS NULL OR e.institution_id = p_institution_id)
    ORDER BY e.name;
END $$

DELIMITER ;
