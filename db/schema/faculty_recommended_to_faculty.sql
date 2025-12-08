-- Written by Aidan Bell

/**
 * Faculty-to-faculty recommendations.
 * ENUM order defines priority (first = highest).
 */
CREATE TABLE IF NOT EXISTS faculty_recommended_to_faculty (
    source_faculty_id   CHAR(36) NOT NULL,
    target_faculty_id   CHAR(36) NOT NULL,
    recommendation_type ENUM(
        'shared_keyword',
        'keyword_to_publication',
        'publication_to_keyword',
        'keyword_to_grant',
        'grant_to_keyword',
        'grant_to_publication',
        'publication_to_grant',
        'shared_grant',
        'shared_department'
    ) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (source_faculty_id, target_faculty_id),

    FOREIGN KEY (source_faculty_id) 
        REFERENCES faculty(faculty_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,

    FOREIGN KEY (target_faculty_id)
        REFERENCES faculty(faculty_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,

    INDEX idx_recommendations_source (source_faculty_id),
    INDEX idx_recommendations_type (recommendation_type)
);
