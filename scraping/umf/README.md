# ScholarSphere UMF Scraper

This component of the ScholarSphere data ingestion pipeline was written
by Clayton Durepos, assisted by AI. It collects, normalizes, and exports
faculty information from the University of Maine at Farmington (UMF) for
downstream integration into the ScholarSphere database.

## Source Website

All information is retrieved directly from the UMF faculty directory:

`https://farmington.edu/about/directory/?user_type=faculty`

The scraper identifies all valid faculty profile pages and extracts
structured information such as names, titles, departments, emails, and
scholarly profiles.

# Data Scraping Scripts and Documentation

## Error Handling and Validation

The scraper includes:

-   Basic HTTP failure handling for unreachable or slow pages
-   Polite request throttling to avoid excessive load on the source
    server
-   Fallback logic for missing or malformed fields
-   Standardized parsing of names, titles, and departments
-   Email cleanup to convert obfuscated formats into standard addresses
-   Validation of URLs and scholarly profile links

These safeguards ensure consistent output even when source pages contain
irregular formatting or incomplete data.

## Cleaning and Normalization Steps

The following normalization steps are applied during scraping:

-   Whitespace and unicode normalization
-   Removal of academic prefixes and degree suffixes in names
-   Parsing names into first and last name components
-   Standardizing job titles and inferring departments when embedded in
    title text
-   Extracting ORCID, Google Scholar, and ResearchGate URLs when present
-   Correcting obfuscated email formats such as "name \[at\] domain
    \[dot\] edu"

## Output Format

The scraper produces structured results in CSV format. JSON export can
be enabled if needed.

Default output files:

-   `faculty_umf.csv`
-   `institution_umf.csv`

These files are compatible with MySQL import workflows.

### Sample CSV Row

    faculty_id,first_name,last_name,title,department,email,scraped_from,orcid,google_scholar,rgate
    jdoe,John,Doe,Associate Professor,Mathematics,john.doe@maine.edu,https://farmington.edu/about/directory/jdoe/,https://orcid.org/0000-0002-1825-0097,,

## Importing into MySQL

### CSV Import

    LOAD DATA INFILE 'faculty_umf.csv'
    INTO TABLE faculty
    FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
    IGNORE 1 LINES;

# Running the Scraper

Execute the script directly:

    python umf_scraper.py

The script will:

1.  Fetch all faculty profile links from the UMF directory
2.  Scrape and clean each profile
3.  Validate and normalize all extracted fields
4.  Write final results to CSV files for downstream loading
