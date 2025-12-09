# ScholarSphere Scraping

Written by Clayton Durepos

Data scraping and ingestion pipeline for collecting faculty and publication data from Maine universities and inserting it into the ScholarSphere database.

## Overview

The scraping directory contains scripts and utilities for:
1. **Scraping** faculty and publication data from university websites
2. **Normalizing** and cleaning scraped data
3. **Inserting** data into the ScholarSphere database

## Directory Structure

```
scraping/
├── umo/              # University of Maine (Orono) scraper
├── uma/              # University of Maine at Augusta scraper
├── umf/              # University of Maine at Farmington scraper
├── usm/              # University of Southern Maine scraper
├── schemas/          # Data classes (Pydantic/dataclass models)
├── publications/     # Publication scraping utilities
├── utils/            # Shared utility functions
├── equipment/        # Equipment demo data
├── out/              # Output directory (JSONL files)
├── scrape.py         # Main orchestration script
├── insert.py         # Database insertion script
└── requirements.txt  # Python dependencies
```

## Main Scripts

### `scrape.py` - Scraper Orchestration

Unified script that runs all institution scrapers and collects their output.

**Usage:**
```bash
python scraping/scrape.py
```

**What it does:**
- Runs scrapers for UMA, UMF, UMO, and USM
- Collects JSONL output from each scraper
- Writes results to `scraping/out/` directory:
  - `{institution}_faculty.jsonl` - Faculty records
  - `{institution}_publications.jsonl` - Publication records (UMO only)

**Output format:** Newline-delimited JSON (JSONL), one record per line.

### `insert.py` - Database Insertion

Reads JSONL files from `scraping/out/` and inserts all data into the database using stored procedures.

**Usage:**
```bash
python scraping/insert.py
```

**What it does:**
- Reads all `*.jsonl` files from `scraping/out/`
- Generates UUIDs for entities (faculty, institutions, publications)
- Calls MySQL stored procedures to insert data
- Optionally generates keywords using LLM (Qwen model) if available
- Handles relationships between entities (faculty-institution, faculty-publication, etc.)

**Requirements:**
- Database connection configured in `.env` file
- MySQL stored procedures must be initialized
- Optional: CUDA-enabled GPU for LLM keyword generation

## Institution Scrapers

Each institution has its own scraper directory with institution-specific logic.

### `umo/` - University of Maine (Orono)

**Author:** Aidan Bell, Clayton Durepos

**Features:**
- Scrapes faculty directory pages organized by department
- Extracts faculty profiles with biography parsing
- Scrapes publications using Crossref API
- Complex parsing pipeline with multiple biography parsers and compilers

**Output:**
- `umo_faculty.jsonl`
- `umo_publications.jsonl`

### `uma/` - University of Maine at Augusta

**Author:** Owen Leitzell

**Features:**
- Scrapes faculty directory
- Extracts faculty information

**Output:**
- `uma_faculty.jsonl`

### `umf/` - University of Maine at Farmington

**Author:** Clayton Durepos

**Features:**
- Scrapes faculty directory from `https://farmington.edu/about/directory/`
- Extracts names, titles, departments, emails, phone numbers
- Cleans biography text (removes cookie notices, boilerplate)
- Normalizes email formats (handles obfuscated emails like "name [at] domain [dot] edu")
- Validates scholarly profile URLs (ORCID, Google Scholar, ResearchGate)

**Output:**
- `umf_faculty.jsonl`

### `usm/` - University of Southern Maine

**Author:** Clayton Durepos, Abby Pitcairn

**Features:**
- Scrapes alphabetically organized faculty directory
- Attempts to access individual faculty webpages
- Extracts biography from personal pages
- Handles inconsistent HTML structure

**Output:**
- `usm_faculty.jsonl`

## Schemas (`schemas/`)

Python dataclasses that define the structure of scraped data.

**Purpose:**
- Type validation for scraped data
- Consistent data structure across scrapers
- Serialization to JSON for output

**Examples:**
- `faculty.py` - Faculty data structure
- `publication.py` - Publication data structure
- `faculty_email.py` - Email relationship
- `faculty_department.py` - Department relationship

## Publications (`publications/`)

Utilities for scraping and processing publication data.

**Files:**
- `publication_parser.py` - Parses publication data from various sources
- `citations_from_tags.py` - Extracts citation information

**Used by:** UMO scraper for publication data collection.

## Utils (`utils/`)

Shared utility functions used across scrapers.

**Files:**
- `conversion.py` - Data conversion utilities
- `json_output.py` - JSON/JSONL output formatting
- `headers.py` - HTTP request headers for scraping

## Equipment (`equipment/`)

Demo equipment data for testing and demonstration purposes.

**Files:**
- `equipment_demo.csv` - Sample equipment data

## Output Directory (`out/`)

Contains the final scraped data in JSONL format, ready for database insertion.

**Files:**
- `{institution}_faculty.jsonl` - Faculty records (one JSON object per line)
- `{institution}_publications.jsonl` - Publication records (UMO only)

**Format:** Newline-delimited JSON (JSONL)
- One complete JSON object per line
- Each line is a valid JSON document
- Easy to process line-by-line

## Data Cleaning and Normalization

All scrapers apply consistent normalization:

- **Name parsing**: Split into first/last name, remove prefixes/suffixes
- **Whitespace normalization**: Clean up extra spaces, unicode characters
- **Email cleaning**: Convert obfuscated formats to standard addresses
- **URL validation**: Verify scholarly profile links
- **Biography cleaning**: Remove cookie notices, boilerplate, unwanted content
- **Department extraction**: Parse departments from titles when embedded
- **Title standardization**: Normalize job titles

## Workflow

1. **Scrape data:**
   ```bash
   python scraping/scrape.py
   ```
   This generates JSONL files in `scraping/out/`.

2. **Insert into database:**
   ```bash
   python scraping/insert.py
   ```
   This reads the JSONL files and inserts data using stored procedures.

## Dependencies

Install scraping dependencies:

```bash
pip install -r scraping/requirements.txt
```

**Key dependencies:**
- `beautifulsoup4` - HTML parsing
- `requests` - HTTP requests
- `mysql-connector-python` - Database connection
- `tqdm` - Progress bars
- Optional: `transformers`, `torch` - For LLM keyword generation

## Notes

- **Rate limiting**: Scrapers include polite request throttling to avoid overloading source servers
- **Error handling**: All scrapers include error handling for network failures and malformed data
- **UUID generation**: UUIDs are generated in Python (UUID v4) before database insertion
- **Keyword generation**: Optional LLM-based keyword generation requires CUDA-enabled GPU
- **Output format**: JSONL is used for efficient line-by-line processing of large datasets

