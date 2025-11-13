# USM Scraping Documentation

## Source Websites

USM has a faculty and staff directory page that links to alphabetically organized subdirectories. The URL is:

[usm.maine.edu/directories/faculty-and-staff](https://usm.maine.edu/directories/faculty-and-staff/)

and then concatenate each letter of the alphabet to reach each subdirectory, like so:

[usm.maine.edu/directories/faculty-and-staff/a/](https://usm.maine.edu/directories/faculty-and-staff/a/)

Lastly, for each faculty member with a valid first and last name scraped from the subdirectory, we attempt to access their personal webpage by concatenating their name with USM's `people` directory, like so:

[usm.maine.edu/directories/people/first-last/](https://usm.maine.edu/directories/people/behrooz-mansouri/)

## Cleaning Steps

1. `BeautifulSoup` did the initial cleaning of the raw HTML for each page.
2. Used `BeautifulSoup.find` to isolate each faculty within each `personwrapper` on the page.
3. Isolated name information:
    - Removed digits and certain symbols (parentheses, commas, addition sign) using `regex`.
    - Split and stripped name field into separate parts by whitespace.
    - Removed any abbreviations that were not strictly names (MFA, PHD, RN, etc).
    - Handled special cases due to USM HTML source code having little consistency.
    - Assigned first and last name fields.
    - For faculty with an isolated first and last name, attempt to access a personal website by concatenating the name with the directory URL; if found, scrape for biography field using `select_one("div.bio")`.
4. Isolated title information with `select_one("div.people-title li")` and split the string into distinct title and department fields whenever the word "department" appeared in the title text. 
5. Isolated email with `select_one("div.people-email a")`.
6. Isolated phone number with `select_one("div.people-telephone a")`.
7. Built `faculty` object from isolated fields and added to final output csv file. 

## Example Output

| faculty_id | first_name       | last_name   | title                                      | department                          | email                        | phone_num      | biography                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | research_interest | orcid | google_scholar_url | research_gate_url | scraped_from                                                 |
|------------|-----------------|------------|--------------------------------------------|-------------------------------------|-------------------------------|----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------|-------|--------------------|------------------|--------------------------------------------------------------|
|            | Abou El-Makarim | Aboueissa  | Professor                                  | Department of Mathematics and Statistics | abouel.aboueissa@maine.edu   | 207-228-8389   | Professor Aboueissa’s teaching experience includes teaching both undergraduate and graduate courses...                                                                                                                                                                                   |                 |       |                    |                  | https://usm.maine.edu/directories/faculty-and-staff/a/       |
|            | Lex             | Abbatello |                                            |                                     | lex.abbatello@maine.edu      | 207-228-8114   | Lex is originally from Westbrook, Maine. She began working for the University of Southern Maine in 2025 as an Academic Advisor... |                 |       |                    |                  | https://usm.maine.edu/directories/faculty-and-staff/a/       |
|            | Derek           | Abbott     | Police Sergeant                            |                                     | derek.r.abbott@maine.edu     | 207-780-5211   | Sgt. Derek Abbott has worked in law enforcement for the past 14 years, the last 13 here at USM. Sgt. Abbott is a veteran of the U.S. Coast Guard, a graduate of Westfield State College and holds a Masters degree... |                 |       |                    |                  | https://usm.maine.edu/directories/faculty-and-staff/a/       |
|            | Titus           | Abbott     | Artist Faculty in Music Theory & Composition |                                     | titus.abbott@maine.edu       |                | Titus Abbott, saxophonist and composer in both jazz and classical idioms has been performing nationally and internationally for over 25 years. As an improviser and composer... |                 |       |                    |                  | https://usm.maine.edu/directories/faculty-and-staff/a/       |

