/**
 * Stores faculty-to-faculty recommendations.
 * 
 * Directional: source_faculty_id is the user receiving the recommendation,
 * target_faculty_id is the recommended collaborator.
 * 
 * Scores are additive - multiple matching criteria increase the total score.
 * The recommendation_type reflects the highest-priority matching criterion.
 */
CREATE TABLE IF NOT EXISTS faculty_recommended_to_faculty (
    source_faculty_id   CHAR(36)        NOT NULL,
    target_faculty_id   CHAR(36)        NOT NULL,
    match_score         DECIMAL(5,4)    NOT NULL DEFAULT 0.0,
    recommendation_type ENUM(
        'shared_keyword',
        'keyword_to_publication',
        'publication_to_keyword',
        'keyword_to_grant',
        'grant_to_keyword',
        'grant_to_publication',
        'publication_to_grant',
        'shared_grant',
        'shared_department',
        'shared_institution'
    ) NOT NULL,
    created_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (source_faculty_id, target_faculty_id),

    FOREIGN KEY (source_faculty_id) 
        REFERENCES faculty(faculty_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,

    FOREIGN KEY (target_faculty_id)
        REFERENCES faculty(faculty_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,

    INDEX idx_recommendations_source (source_faculty_id),
    INDEX idx_recommendations_score (source_faculty_id, match_score DESC),
    INDEX idx_recommendations_type (recommendation_type)
);
