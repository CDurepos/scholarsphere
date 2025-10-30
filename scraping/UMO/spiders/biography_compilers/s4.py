import os
import csv
import requests
from bs4 import BeautifulSoup

DEPARTMENTS = (("https://sbe.umaine.edu/personnel/faculty/", "biology_and_ecology.csv"),)

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
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    bio_links = []
    for p_tag in soup.find_all("p", class_="kt-blocks-info-box-text"):
        if "professor" in p_tag.get_text(strip=True).lower():
            a_tags = p_tag.find_all("a", href=True)
            if a_tags:
                bio_links.append(a_tags[-1]["href"])

    # WRITE
    with open(os.path.join(OUTPUT_DIR, output_file), "x", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for link in bio_links:
            writer.writerow([link])
