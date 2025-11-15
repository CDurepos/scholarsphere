CREATE TABLE publications (
    publication_id  CHAR(36)        PRIMARY KEY,
    title           VARCHAR(64)     NOT NULL,
    year            INT             NOT NULL,
    doi             VARCHAR(64)     UNIQUE,

    -- Abstracts are our exception to `VARCHAR(2055)`
    abstract        TEXT,
    publisher       VARCHAR(255)    NOT NULL,
    citation_count  INT             DEFAULT 0
);
