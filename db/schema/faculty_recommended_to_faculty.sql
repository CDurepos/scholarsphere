CREATE TABLE IF NOT EXISTS faculty_recommended_to_faculty (
    recommender_id CHAR(36) NOT NULL,
    recommended_id CHAR(36) NOT NULL,
    match_score FLOAT,
    created_at DATE NOT NULL,

    PRIMARY KEY (recommender_id, recommended_id),
    FOREIGN KEY (recommender_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE,
    FOREIGN KEY (recommended_id) REFERENCES faculty(faculty_id) ON DELETE CASCADE
);