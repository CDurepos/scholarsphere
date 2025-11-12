# USM Scraping Documentation

## Source Websites

USM has a faculty and staff directory page that links to alphabetically organized subdirectories. The URL is:

[maine.edu/directories/faculty-and-staff](`https://usm.maine.edu/directories/faculty-and-staff/`)

and then concatenate each letter of the alphabet to reach each subdirectory, like so:

[maine.edu/directories/faculty-and-staff/a/](`https://usm.maine.edu/directories/faculty-and-staff/a/`)

## Cleaning Steps

1. `BeautifulSoup` did the initial cleaning of the raw HTML for each page.
2. Used `BeautifulSoup.find` to isolate each faculty within each `personwrapper` on the page.
3. Isolated name information:
    - Removed digits and certain symbols (parentheses, commas, addition sign) using `regex`.
    - Split and stripped name field into separate parts by whitespace.
    - Removed any abbreviations that were not strictly names (MFA, PHD, RN, etc).
    - Handled special cases due to USM HTML source code having little consistency.
    - Assigned first and last name fields.
4. Isolated title information with `select_one("div.people-title li")`.
5. Isolated email with `select_one("div.people-email a")`.
6. Isolated phone number with `select_one("div.people-telephone a")`.
7. Built `faculty` object from isolated fields and added to final output csv file. 

## Example Output

| faculty_id | first_name | last_name   | title                                                                 | department | email                        | phone_num                 | biography | research_interest | orcid | google_scholar_url | research_gate_url | scraped_from                                                 |
|-------------|-------------|-------------|-----------------------------------------------------------------------|-------------|-------------------------------|---------------------------|------------|-------------------|--------|--------------------|------------------|--------------------------------------------------------------|
|             | Abou El-Makarim | Aboueissa | Professor, Department of Mathematics and Statistics                   |             | abouel.aboueissa@maine.edu   | 207-228-8389              |            |                   |        |                    |                  | https://usm.maine.edu/directories/faculty-and-staff/a/       |
|             | Lex         | Abbatello  |                                                                       |             | lex.abbatello@maine.edu      | 207-228-8114              |            |                   |        |                    |                  | https://usm.maine.edu/directories/faculty-and-staff/a/       |
|             | Derek       | Abbott     | Police Sergeant                                                       |             | derek.r.abbott@maine.edu     | 207-780-5211              |            |                   |        |                    |                  | https://usm.maine.edu/directories/faculty-and-staff/a/       |
|             | Titus       | Abbott     | Artist Faculty in Music Theory & Composition                          |             | titus.abbott@maine.edu       |                           |            |                   |        |                    |                  | https://usm.maine.edu/directories/faculty-and-staff/a/       |
|             | Sara        | Abronze    |                                                                       |             | sara.abronze@maine.edu       | 207-780-5774              |            |                   |        |                    |                  | https://usm.maine.edu/directories/faculty-and-staff/a/       |
|             | Anne        | Ackerman   | Part-Time Lecturer of Art Education                                   |             | anne.ackerman@maine.edu      |                           |            |                   |        |                    |                  | https://usm.maine.edu/directories/faculty-and-staff/a/       |
|             | Valerie     | Ackley     | Lecturer II, Part Time Faculty, Department of Mathematics and Statistics |             | valerie.ackley@maine.edu     | 207-240-1599 (text only)  |            |                   |        |                    |                  | https://usm.maine.edu/directories/faculty-and-staff/a/       |
|             | Emery       | Addams     | Counseling Intern                                                     |             | emerson.addams@maine.edu     | 207-780-5040              |            |                   |        |                    |                  | https://usm.maine.edu/directories/faculty-and-staff/a/       |

