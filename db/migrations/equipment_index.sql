-- Index on institution_id for faster lookup related to institution
CREATE INDEX idx_equipment_institution_id
    ON equipment(institution_id);

-- Index on equipment name
CREATE INDEX idx_equipment_name
    ON equipment(name);

-- Quickly check availability
CREATE INDEX idx_equipment_availability
    ON equipment(availability);
