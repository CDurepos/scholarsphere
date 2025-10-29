import os
import csv
import requests
from bs4 import BeautifulSoup

# CONFIG
URL = "https://umaine.edu/business/faculty-and-staff/"
script_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(
    script_dir, "../../scrape_storage/biography_pages/maine_business_school.csv"
)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# SCRAPE
response = requests.get(URL, headers=headers)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

bio_links = []
faculty_header = soup.find(
    "h2", class_="kt-adv-heading28745_a68738-c8 wp-block-kadence-advancedheading"
)

if faculty_header and faculty_header.find("strong", string="Faculty"):
    next_section = faculty_header.find_next_sibling()

    if next_section:
        for parent_div in next_section.find_all("div", class_="kt-infobox-textcontent"):
            child_div = parent_div.find(
                "p", class_="kt-blocks-info-box-text", recursive=False
            )
            if not child_div:
                continue

            # Find <a> tags that mention "Bio"
            for a_tag in child_div.find_all("a", href=True):
                if "bio" in a_tag.text.lower():
                    bio_links.append(a_tag["href"])

# WRITE
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for link in bio_links:
        writer.writerow([link])
