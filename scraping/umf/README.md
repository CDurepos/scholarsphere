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
-   Cleaning biography text to remove cookie notices, boilerplate, and other unwanted content

## Output Format

The scraper produces structured results in CSV format, with one CSV file per database table. This allows for direct import into MySQL tables that match the schema structure.

Default output files:

-   `faculty_umf.csv` - Main faculty records (faculty_id, first_name, last_name, biography, orcid, google_scholar_url, research_gate_url, scraped_from)
-   `faculty_email_umf.csv` - Faculty email addresses (faculty_id, email)
-   `faculty_phone_umf.csv` - Faculty phone numbers (faculty_id, phone_num)
-   `faculty_department_umf.csv` - Faculty departments (faculty_id, department_name)
-   `faculty_title_umf.csv` - Faculty titles (faculty_id, title)
-   `institution_umf.csv` - Institution information
-   `faculty_works_at_institution_umf.csv` - Faculty-institution relationships (faculty_id, institution_id, start_date, end_date)

These files are compatible with MySQL import workflows and can be directly loaded into their respective tables.

### Biography Cleaning

The scraper includes automatic cleaning of biography text to filter out unwanted content such as:
- Cookie notices and privacy policy text
- Website boilerplate content
- University name-only entries
- Text that is too short or contains mostly university-related terms

Only meaningful biography content is retained in the output.

## Importing into MySQL

### CSV Import

Each CSV file can be imported into its corresponding table:

    LOAD DATA INFILE 'faculty_umf.csv'
    INTO TABLE faculty
    FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
    IGNORE 1 LINES;

    LOAD DATA INFILE 'faculty_email_umf.csv'
    INTO TABLE faculty_email
    FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
    IGNORE 1 LINES;

    -- Repeat for other tables as needed

# Running the Scraper

Execute the script directly:

    python umf_scraper.py

The script will:

1.  Fetch all faculty profile links from the UMF directory
2.  Scrape and clean each profile
3.  Validate and normalize all extracted fields
4.  Write final results to CSV files for downstream loading
