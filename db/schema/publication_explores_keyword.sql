CREATE TABLE publication_keywords (
    publication_id CHAR(36) NOT NULL,
    name VARCHAR(64) NOT NULL,

    PRIMARY KEY (publication_id, name),

    FOREIGN KEY (publication_id)
        REFERENCES publications(publication_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    FOREIGN KEY (name)
        REFERENCES keywords(name)
        ON DELETE CASCADE
        ON UPDATE CASCADE

);
