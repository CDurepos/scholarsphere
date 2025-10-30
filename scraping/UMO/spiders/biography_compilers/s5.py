import os
import csv
import requests
from bs4 import BeautifulSoup

DEPARTMENTS = (("https://umaine.edu/history/faculty/", "history.csv"),)

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
    for profile_anchor in soup.find_all("a", class_="wp-block-kadence-singlebtn"):
        sibs = profile_anchor.parent.find_previous_siblings()
        if len(sibs) == 4:
            text = sibs[2].get_text(strip=True)
            if (
                text
                and "professor" in text.lower()
                and "emeritus" not in text.lower()
                and "emerita" not in text.lower()
            ):
                bio_links.append(profile_anchor["href"])

    # WRITE
    with open(
        os.path.join(OUTPUT_DIR, output_file), "x", newline="", encoding="utf-8"
    ) as f:
        writer = csv.writer(f)
        for link in bio_links:
            writer.writerow([link])
