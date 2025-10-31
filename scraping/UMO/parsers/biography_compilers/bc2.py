import os
import csv
import requests
from bs4 import BeautifulSoup
from scraping.UMO.utils import get_header

DEPARTMENTS = (
    ("https://mcec.umaine.edu/eleceng/#fac", "electrical_and_computer_engineering.csv"),
    ("https://mcec.umaine.edu/civil/#fac", "civil_and_environmental_engineering.csv"),
    ("https://mcec.umaine.edu/depts/scis/", "computing_and_information_science.csv"),
    ("https://mcec.umaine.edu/depts/mee/", "mechanical_engineering.csv"),
    ("https://mcec.umaine.edu/depts/set/", "engineering_technology.csv"),
    (
        "https://mcec.umaine.edu/depts/chembio/",
        "chemical_and_biomedical_engineering.csv",
    ),
)


class B2Compiler:
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(
            script_dir, "../../scrape_storage/biography_pages/"
        )
        self.departments = DEPARTMENTS

        for url, output_file in self.departments:
            if os.path.exists(os.path.join(self.output_dir, output_file)):
                raise FileExistsError(f"The output file {output_file} already exists.")

        os.makedirs(os.path.dirname(self.output_dir), exist_ok=True)

        self.headers = get_header("h1")

    def collect(self):
        for url, output_file in self.departments:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            bio_links = []
            fac = soup.find("div", id="fac")
            if not fac:
                fac = soup  # some depts don't have fac id, so just start from soup
            for div in fac.find_all("div", class_="entry-content"):
                if "professor" in div.get_text(strip=True).lower():
                    header = div.find_previous_sibling("header")
                    if header:
                        a_tag = header.find("a", href=True)
                        if a_tag:
                            bio_links.append(a_tag["href"])

            # WRITE
            with open(
                os.path.join(self.output_dir, output_file),
                "x",
                newline="",
                encoding="utf-8",
            ) as f:
                writer = csv.writer(f)
                for link in bio_links:
                    writer.writerow([link])
