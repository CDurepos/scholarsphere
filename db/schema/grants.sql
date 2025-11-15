CREATE TABLE grants (
    grant_id    CHAR(36) PRIMARY KEY,
    description TEXT NULL,
    amount      DECIMAL(10,2) NOT NULL,
    start_date  DATE NOT NULL,
    end_date    DATE NOT NULL
);
