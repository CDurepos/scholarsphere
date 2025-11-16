CREATE TABLE IF NOT EXISTS publication (
    publication_id  CHAR(36) NOT NULL PRIMARY KEY,

    title           VARCHAR(64) NOT NULL,
    year            INT NOT NULL,
    doi             VARCHAR(64) UNIQUE,
    abstract        TEXT,
    publisher       VARCHAR(64) NOT NULL,
    citation_count  INT DEFAULT 0
);