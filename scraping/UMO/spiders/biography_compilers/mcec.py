import os
import csv
import requests
from bs4 import BeautifulSoup

# CONFIG
URL = "https://mcec.umaine.edu/eleceng/#fac"
script_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(script_dir, "../../scrape_storage/biography_pages/mcec.csv")
if os.path.exists(OUTPUT_FILE):
    raise FileExistsError(f"The output file {OUTPUT_FILE} already exists.")
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

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
for div in soup.find_all("div", class_="entry-content"):
    if "professor" in div.get_text(strip=True).lower():
        header = div.find_previous_sibling("header")
        if header:
            a_tag = header.find("a", href=True)
            if a_tag:
                bio_links.append(a_tag["href"])

# WRITE
with open(OUTPUT_FILE, "x", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for link in bio_links:
        writer.writerow([link])
