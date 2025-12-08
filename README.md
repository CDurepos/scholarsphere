# Overview

An application built to foster collaboration between Maine researchers. 

Built by students, for the COS457 Database Systems course at the University of Southern Maine.

# How to Run

## Requirements

To run the ScholarSphere application, you must first have a running MySQL server on your machine, `sudo` access on your machine, and a `.env` file at the root of the project repository. This should hold the following variables:

```bash
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=...
DB_PASS=...
DB_NAME=scholarsphere
```

Where `DB_USER` and `DB_PASS` are the appropriate admin credentials for your local MySQL server.

## Keyword Generation

If you would like any API routes involving calls to an LLM to work (just keyword generation at the time of writing this), or the insert.py script to automatically generate keywords, you must have a gpu with cuda and will have to install cuda compatible versions of
pytorch and torchvision. That can be done through here: https://pytorch.org/get-started/locally/. The app will run fine without this, but some
functionality will be limited.

## For General Use

To launch this application for usage, you should only run the following two commands in a bash terminal, from the root of the repository.

1. `bash bin/install.sh`
    
    This script will install `node.js` and `conda` if not already installed on your device. Following this, it will install all dependencies for the application, instantiate the database, and populate the database.

2. `bash bin/run.sh`

    This script will run all components of the application. By default, the backend will run on `localhost:5000` and the frontend will run on `localhost:5173`.

    If you are using a Mac, you may need to disable AirDrop and the AirDrop receiver for the `:5000` port to be available for this application.

## For Development

### Installation

Similar to the quick start, we recommend first running `bash bin/install.sh`

This script will install `node.js` and `conda` if not already installed on your device. Following this, it will install all dependencies for the application, instantiate the database, and populate the database.

### Frontend

You can start the frontend development server with the following commands:

```
cd frontend
npm run dev
```

### Backend

The backend development server is run like so:

```
cd backend
python run.py
```

# Team Member Contributions

ScholarSphere was developed by four undergraduate students, who each primarily worked on individual components of the application. 

Each file is annotated with its author. For files which have more than one author, the order in which authors are listed are organized from most contribution to least.

## GitHub Username to Student Map

aidan073:      Aidan Bell

CDurepos:      Clayton Durepos

abbyPitcairn:  Abby Pitcairn

OwenLeitzell:  Owen Leitzell

# COS457 Phase 2 Task Distribution

### D1 - Recorded Video Demonstration
1. Clayton: Show the database running from scratch (creation, data loading, constraints in action). **deadline**: 11/15
2. Aidan, Owen: Discuss stored procedures, functions, queries, triggers, and indexing. **deadline**: 11/15 
3. Abby: Show at least one example of data scraping and cleaning results. **deadline**: 11/15

### D2 - MySQL Database Schema Scripts
Each member will create tables and indexes with comments for their designated tables:
1. Aidan:  Users[ `users`, `follows`, `recommendations` ]. **deadline**: 11/8
   
2. Abby:  Instutions & Equipment [`institutions`, `works_at`, `equipment`]. **deadline**: 11/8
   
3. Owen:  Publications & Keywords [`publications`, `publication_authors`, `keywords`, `publication_keywords`, `user_keywords`]. **deadline**: 11/8
   
4. Clayton:  Grants & Credentials [`grants`, `grant_providers`, `grant_recipients`, `credentials`]. **deadline**: 11/8

### D3 - Stored Procedures and Functions
Each member will document and implement the key system operations for their designated tables:
1. Aidan:  Users [ `users`, `follows`, `recommendations` ]. **deadline**: 11/12
   
2. Abby:  Instutions & Equipment [`institutions`, `works_at`, `equipment`]. **deadline**: 11/12
   
3. Owen:  Publications & Keywords [`publications`, `publication_authors`, `keywords`, `publication_keywords`, `user_keywords`]. **deadline**: 11/12
   
4. Clayton:  Grants & Credentials [`grants`, `grant_providers`, `grant_recipients`, `credentials`]. **deadline**: 11/12

The primary search procedure will be a joint effort. **deadline**: 11/12

### D4 - Data Scraping Scripts and Documentation
Each member will do the following for their designated Maine University: 
1. Provide scraping source code in python.
2. Document source websites, sample outputs, and cleaning steps.
3. Save scraping results in a .csv or .json file with MySQL import compatible formatting.

Designated Universities:
- Aidan:   UMO,  **deadline**: 11/5
- Owen:    UMA,  **deadline**: 11/5
- Abby:    USM,  **deadline**: 11/5
- Clayton: UMF,  **deadline**: 11/5

### D5 - Sample Data and Data Cleaning Documentation
Each member will provide scripts or CSV files showcasing a sample data insert into their designated tables with comments on how the data was validated and cleaned.
1. Aidan:  Users[ `users`, `follows`, `recommendations` ]. **deadline**: 11/6
   
2. Abby:  Instutions & Equipment [`institutions`, `works_at`, `equipment`]. **deadline**: 11/6
   
3. Owen: Publications & Keywords [`publications`, `publication_authors`, `keywords`, `publication_keywords`, `user_keywords`]. **deadline**: 11/6
   
4. Clayton:  Grants & Credentials [`grants`, `grant_providers`, `grant_recipients`, `credentials`]. **deadline**: 11/6

### D6 - Query Optimization Analysis
Clayton and Aidan undertook the query optimization portion of this phase.

### D7 - Comprehensive README file (.md)
For the **Individual Tasks**, each member will document how to run their individual scraping scripts, sample processing scripts, and SQL files. For the **Joint Tasks**, all members will document the full database recreation steps, and document any joint effort procedures such as the primary search procedure.

**Individual Tasks**:
1. Aidan - **deadline**: 11/15
2. Abby - **deadline**: 11/15
3. Owen - **deadline**: 11/15
4. Clayton - **deadline**: 11/15

**Joint Tasks**:
1. Database Recreation Steps - **deadline**: 11/15
2. Key Procedure Usage - **deadline**: 11/15

# COS457 Phase 2 Supplementary Material

## Individual Contribution

Aidan:
* Wrote scraper for the University of Maine faculty and publications, wrote publication scraping utils using crossref api, and made scraping schemas (dataclasses).

    `scraping/umo/*`
    `scraping/publications/*`
    `scraping/schemas/*`

* Refactored data insertion script for publication insertion functionality.

    `scraping/insert.py`

* Created schemas and procedures pertaining to `faculty`. 

    * `schema/`
        `faculty.sql`, `faculty_phone.sql`, `faculty_email.sql`, `faculty_title.sql`, `faculty_follows_faculty.sql`, `faculty_recommended_to_faculty.sql`,     `faculty_department.sql`

    * `procedures/`
        * `create/`

            `create_faculty_department.sql`, `create_faculty_email.sql`, `create_faculty_follows_faculty.sql`, `create_faculty_phone.sql`, `create_faculty_title.sql`, `create_publication_authored_by_faculty.sql`

        * `read/`

            `read_faculty_department.sql`, `read_faculty_email.sql`, `read_faculty_follows_faculty.sql`, `read_faculty_phone.sql`, `read_faculty_publications.sql`, `read_faculty_title.sql`, `read_faculty.sql`

        * `update/`

            `update_faculty_department.sql`, `update_faculty_email.sql`, `update_faculty_phone.sql`, `update_faculty_title.sql`, `update_faculty.sql`

        * `delete/`

            `delete_faculty_department.sql`, `delete_faculty_email.sql`, `delete_faculty_follows_faculty.sql`, `delete_faculty_phone.sql`, `delete_faculty_title.sql`, `delete_faculty.sql`, `delete_publication_authored_by_faculty.sql`

        * `workflow/`

            `search_faculty.sql`, `add_publication_for_faculty.sql`

* Wrote index script for `faculty` entity.
    * `migrations/`

        `003_assign_faculty_index.sql`

* Wrote up **Query Optimization Analysis** for **Query 2** (see below).

Owen:
* Wrote scraper for the University of Maine at Augusta and made a csv of the relevant faculty.
     'scraping/uma/*'
        
  
* Created the schemas, procedures, and functions pertaining to publications, publication_authors, keywords, publication_keywords, and user_keywords.

* 'schema/':
     'faculty_keyword.sql','grants_for_keyword.sql','keyword.sql','publication_authored_by_faculty.sql','publication_keyword.sql', 'publication.sql', 'publication_explores_keyword.sql', 'faculty_researches_keyword.sql'
 
* 'procedures/'
  *'create/'
     'create_faculty_researches_keyword.sql', 'create_publication_explores_keyword.sql', 'create_publication.sql', 'create_faculty_researches_keyword.sql', 'create_grants_for_keyword.sql', 'create_keyword.sql', 'create_publication.sql'

  *'delete/'
     'delete_faculty_researches_keyword.sql', 'delete_keyword'.sql', 'delete_publications.sql','delete_publication_explores_keyword.sql'

   * 'read/'
     'read_publication_keyword.sql','read_faculty_keyword.sql'
     
  * 'update/'
     'update_keyword.sql', 'update_publication.sql'
    
*'functions/'
   'count_keywords.sql', 'count_keywords_publications.sql', 'count_user_keywords.sql', 'get_DOI.sql', 'get_citation_count.sql', 'get_publication_title.sql', 'get_publication_year.sql', 'get_publication_year.sql', 'keyword_exists.sql', 'publication_has_keyword.sql', 'user_has_keyword.sql'

Clayton:
* Wrote scraper for the University of Maine at Farmington and associated documentation.

    `scraping/umf/*`

* Wrote unified script for individual scrapers produced by self and teammates.
    
    `scraping/scrape.py`

* Wrote data insertion (to database) script utilizing output from `scrape.py`

    `scraping/insert.py`

*  Created schema, procedures, and functions pertaining to `grants` and `credentials`. Created procedures pertaining to `institution` and `equipment` entities.

    * `schema/`
        `grants.sql`,`grants_granted_to_faculty.sql`, `grants_organization.sql`, `credentials.sql`

    * `procedures/`
        * `create/`

            `create_credentials.sql`, `create_equipment.sql`, `create_grants_granted_to_faculty.sql`, `create_grants.sql`, `create_institution.sql`

        * `delete/`

            `delete_equipment.sql`, `delete_grants.sql`, `delete_grants_granted_to_faculty.sql`, `delete_institution.sql`

        * `read/`

            `read_equipment.sql`, `read_grants_organization.sql`, `read_organization_grants.sql`, `read_institution_faculty.sql`, `read_faculty_institution.sql`

        * `update/`

            `update_equipment.sql`, `update_grants.sql`, `update_grants_organization.sql`, `update_institution.sql`
        
        * `workflow/`

            `recommend_faculty_by_department.sql`, `recommend_faculty_by_grant_keyword.sql`, `recommend_faculty_by_grants.sql`, `recommend_faculty_by_institution.sql`, `recommend_faculty_by_publication.sql`, `recommend_faculty_by_shared_keyword.sql`, `validate_login.sql`

    * `functions/`
        `is_grants_active.sql`, `grants_status.sql`

* Wrote index scripts for `grants` entity. 
    * `migrations/`
    
        `006_assign_grants_organization_index.sql`

* Wrote database initialization scripts, and `*.sh` scripts for generation.
    * `db/`

        `generate_schema.sh`,
        `generate_procedures.sh`,
        `generate_functions.sh`
    * `init/`

        `000_create_database.sql`,
        `001_init_schema.sql`,
        `002_init_procedures.sql`,
        `003_init_functions.sql`,

* Wrote up **Query Optimization Analysis** for **Query 1** (see below).

* Organized file structure and ensured consistent naming across directories and teams' work. Wrote up documentation for naming conventions used in `db/migrations/README.md`, `db/functions/README.md`, and `db/procedures/README.md`.

* Wrote team member contributions and documentation in `db/schema/README.md`

Abby: 
* Scraping - Created the USM faculty scraper to scrape alphabetically organized faculty directory as well as faculty personal webpages using scraped first_name and last_name fields. Additionally created fake equipment data for demonstration purposes. 

* SQL Schemas - Created schema for equipment, institution, and works_at relation table.

   * `equipment.sql`
   * `institution.sql`
   * `faculty_works_at_institution.sql`
   

* SQL Procedures/functions - Created equipment_load.sql and equipment_search.sql functionality.

     * `equipment_load.sql`
     * `euipment_search.sql`

* Query Optimization - Built indexes for equipment and institutions for faster lookup.

* Video - Demonstrated web scraping and data cleaning.

   

## Query Optimization Analysis

### Query 1 — Generating Grant-Based Faculty Recommendations

A subtle feature we implemented is a script that generates recommendations between two faculty members who have both received funds from the same grant. The original procedure looked like this:

```sql
DROP PROCEDURE IF EXISTS recommend_faculty_grants;
DELIMITER $$

CREATE PROCEDURE recommend_faculty_grants()
BEGIN

    -- INSERT directional recommendations
    INSERT INTO faculty_recommended_to_faculty (
        source_faculty_id,
        target_faculty_id,
        match_score,
        created_at
    )
    SELECT
        fA.faculty_id      AS source_faculty_id,
        fB.faculty_id      AS target_faculty_id,
        NULL               AS match_score,
        CURDATE()          AS created_at
    FROM grants_granted_to_faculty AS gA
    JOIN grants_granted_to_faculty AS gB
         ON gA.grant_id = gB.grant_id
    JOIN faculty AS fA
         ON fA.faculty_id = gA.faculty_id
    JOIN faculty AS fB
         ON fB.faculty_id = gB.faculty_id
    WHERE fA.faculty_id <> fB.faculty_id
    GROUP BY
        fA.faculty_id,
        fB.faculty_id;

END$$
DELIMITER ;
```

While this worked, we quickly noticed redundancy:

- Joining the `faculty` table is unnecessary for this query, since we only need the `faculty_id` values, which are already present in `grants_granted_to_faculty`.
- The `GROUP BY` clause is also redundant. Its only purpose here was to avoid duplicate insertions, but our **PRIMARY KEY** and **ON DUPLICATE KEY** constraint already enforce uniqueness for `(source_faculty_id, target_faculty_id)`.

To optimize, we removed the extra joins and dropped the `GROUP BY`:

```sql
DROP PROCEDURE IF EXISTS recommend_faculty_grants;
DELIMITER $$

CREATE PROCEDURE recommend_faculty_grants()
BEGIN

    -- INSERT directional recommendations
    INSERT INTO faculty_recommended_to_faculty (
        source_faculty_id,
        target_faculty_id,
        match_score,
        created_at
    )
    SELECT
        g1.faculty_id      AS source_faculty_id,
        g2.faculty_id      AS target_faculty_id,
        NULL               AS match_score,
        CURDATE()          AS created_at
    FROM grants_granted_to_faculty AS g1
    JOIN grants_granted_to_faculty AS g2
         ON g1.grant_id = g2.grant_id
    WHERE g1.faculty_id <> g2.faculty_id;

END$$
DELIMITER ;
```

---

### Query 2 — Faculty Search Procedure

A core feature of **ScholarSphere** is the ability to search for faculty. For now, we implement this as a straightforward SQL stored procedure, with the idea of layering in embedding-based similarity scoring later on for certain attributes.

```sql
CREATE PROCEDURE search_faculty(
    IN p_first_name    VARCHAR(128),
    IN p_last_name     VARCHAR(128),
    IN p_department    VARCHAR(128),
    IN p_institution   VARCHAR(255)
)
BEGIN
    -- Use DISTINCT to handle cases where a faculty member
    -- has multiple departments or institutions
    SELECT DISTINCT
        f.faculty_id,
        f.first_name,
        f.last_name,
        d.department_name,
        i.name AS institution_name
    FROM faculty AS f
    -- LEFT JOIN ensures we get faculty even if they have no department
    LEFT JOIN faculty_department AS d
        ON f.faculty_id = d.faculty_id
    -- LEFT JOIN to get institution information through the works_at relationship
    LEFT JOIN faculty_works_at_institution AS w
        ON f.faculty_id = w.faculty_id
    LEFT JOIN institution AS i
        ON w.institution_id = i.institution_id
    WHERE
        -- If a parameter is NULL, we ignore that filter
        (p_first_name   IS NULL OR f.first_name        LIKE CONCAT(p_first_name, '%'))
        AND (p_last_name  IS NULL OR f.last_name       LIKE CONCAT(p_last_name, '%'))
        AND (p_department IS NULL OR d.department_name LIKE CONCAT(p_department, '%'))
        AND (p_institution IS NULL OR i.name           LIKE CONCAT(p_institution, '%'));
END $$
```

### Supporting Indexes

```sql
CREATE INDEX idx_faculty_last_first_name
    ON faculty(last_name, first_name);

CREATE INDEX idx_faculty_department_dept_name
    ON faculty_department(department_name);
```

Since the procedure uses prefix LIKE searches (LIKE 'prefix%') on both last_name and first_name, the index allows MySQL to scan only the relevant portion of the faculty table rather than performing a full table scan. 

The index can be used when filtering by last_name alone or by both last_name and first_name, significantly improving query performance. Similarly, the index idx_faculty_department_dept_name on department_name allows the database to quickly locate matching department records without scanning the entire table. 

We anticipate that the department will be an important attribute for faculty to search on. These indexes ensure that both the join operations and the filtering conditions are efficient.
