-- Load equipment CSV into existing table

-- Clear existing data if table already exists
TRUNCATE TABLE equipment;

-- Load CSV file into equipment table
LOAD DATA INFILE 'scraping/equipment/equipment_demo.csv'
INTO TABLE equipment
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(eq_id, name, description, availability, institution_id);
