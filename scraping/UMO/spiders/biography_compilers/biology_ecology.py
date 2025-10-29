import os
import csv
import requests
from bs4 import BeautifulSoup

# CONFIG
URL = "https://sbe.umaine.edu/personnel/faculty/"
script_dir = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(script_dir, "../../scrape_storage/biography_pages/biology_ecology.csv")
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
for p_tag in soup.find_all("p", class_="kt-blocks-info-box-text"):
    if "professor" in p_tag.get_text(strip=True).lower():
        a_tags = p_tag.find_all("a", href=True)
        if a_tags:
            bio_links.append(a_tags[-1]["href"])

# WRITE
with open(OUTPUT_FILE, "x", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for link in bio_links:
        writer.writerow([link])
