CREATE TABLE IF NOT EXISTS faculty_follows_faculty(
    follower_id     CHAR(36)    NOT NULL,
    followee_id     CHAR(36)    NOT NULL,

    PRIMARY KEY (follower_id, followee_id),
    FOREIGN KEY (follower_id) 
        REFERENCES faculty(faculty_id) 
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    FOREIGN KEY (followee_id) 
        REFERENCES faculty(faculty_id) 
        ON DELETE CASCADE
        ON UPDATE CASCADE
);