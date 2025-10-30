import os
import csv
import requests
from bs4 import BeautifulSoup

DEPARTMENTS = (
    ("https://umaine.edu/marine/people/department/faculty/", "marine_sciences.csv"),
    ("https://gsbse.umaine.edu/people/department/faculty/", "biomedical_science_and_engineering.csv"),
)

# CONFIG
script_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(script_dir, "../../scrape_storage/biography_pages/")
for url, output_file in DEPARTMENTS:
    if os.path.exists(os.path.join(OUTPUT_DIR, output_file)):
        raise FileExistsError(f"The output file {output_file} already exists.")
os.makedirs(os.path.dirname(OUTPUT_DIR), exist_ok=True)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# SCRAPE
for url, output_file in DEPARTMENTS:
    bio_links = []
    curr_page = 1
    while True:
        response = requests.get(url + f"/page/{curr_page}/", headers=headers)
        if response.status_code != 200:
            break
        soup = BeautifulSoup(response.text, "html.parser")

        faculty = soup.find_all("div", class_="people-wrapper")

        for tag in faculty:
            fac_position = tag.find("p", class_="people-wrapper__position")
            if (
                fac_position
                and "professor" in fac_position.text.lower()
                and "retired" not in fac_position.text.lower()
            ):
                # Find <a> tags that mention "Bio" or "Biography"
                for p_tag in tag.find_all("p", class_=lambda c: c is None):
                    a_tag = p_tag.next_element
                    if (
                        a_tag
                        and " bio" in a_tag.text.lower()
                        or " biography" in a_tag.text.lower()
                    ):
                        bio_links.append(a_tag["href"])

        curr_page += 1

    # WRITE
    with open(
        os.path.join(OUTPUT_DIR, output_file), "x", newline="", encoding="utf-8"
    ) as f:
        writer = csv.writer(f)
        for link in bio_links:
            writer.writerow([link])
