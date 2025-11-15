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

| First Name | Last Name | Title | Department | Email | Phone | URL |
|-----------|-----------|-------|------------|-------|--------|-----|
| Kevin | Doran | Assistant Professor in Educational Leadership & Adult and Higher Education |  | kevin.doran@maine.edu | 207-780-5173 | https://usm.maine.edu/directories/faculty-and-staff/d/ |
| Maureen | Ebben | Professor of Communication |  | maureen.ebben@maine.edu | 207-780-5617 | https://usm.maine.edu/directories/faculty-and-staff/e/ |
| Matthew | Edney | Professor of Geography |  | matthew.edney@maine.edu | 207-780-4767 | https://usm.maine.edu/directories/faculty-and-staff/e/ |
| Muhammad | El-Taha | Professor | Department of Mathematics and Statistics | el-taha@maine.edu | 207-780-4564 | https://usm.maine.edu/directories/faculty-and-staff/e/ |
| Madalyn | Elliott | Associate Director of Donor Relations & Stewardship |  | madalyn.sirois@maine.edu | 207-780-4224 | https://usm.maine.edu/directories/faculty-and-staff/e/ |
