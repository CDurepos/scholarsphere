CREATE TABLE IF NOT EXISTS faculty_recommended_to_faculty (
    -- Model as directional relationship 
    -- Allows for different match scoring dependent on user properties & data
    source_faculty_id  CHAR(36)    NOT NULL,
    target_faculty_id  CHAR(36)    NOT NULL,
    
    match_score     FLOAT,
    created_at      DATE        NOT NULL,

    PRIMARY KEY (source_faculty_id, target_faculty_id),

    FOREIGN KEY (source_faculty_id) 
        REFERENCES faculty(faculty_id) 
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (target_faculty_id)
        REFERENCES faculty(faculty_id) 
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    ON DUPLICATE KEY UPDATE match_score = VALUES(match_score);

);