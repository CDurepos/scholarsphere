from scraping.utils import get_headers
from scraping.umo.utils.normalize_whitespace import norm_ws

import os
import csv
import requests
from bs4 import BeautifulSoup

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
    """
    Collect biography page links for a set of departments.

    Usage:
        compiler = B2Compiler()
        compiler.collect()
    """

    def __init__(self, output_dir:str):
        self.output_dir = output_dir
        self.departments = DEPARTMENTS

        for url, output_file in self.departments:
            if os.path.exists(os.path.join(self.output_dir, output_file)):
                raise FileExistsError(f"The output file {output_file} already exists.")

        os.makedirs(self.output_dir, exist_ok=True)
        self.headers = get_headers("h1")

    def collect(self):
        for url, output_file in self.departments:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            fac_titles = []
            bio_links = []
            fac = soup.find("div", id="fac")
            if not fac:
                fac = soup  # some depts don't have fac id, so just start from soup
            for div in fac.find_all("div", class_="entry-content"):
                div_text = div.get_text(strip=True)
                if (
                    div_text
                    and "professor" in div_text.lower()
                    and "emeritus" not in div_text.lower()
                    and "emerita" not in div_text.lower()
                ):
                    header = div.find_previous_sibling("header")
                    if header:
                        a_tag = header.find("a", href=True)
                        if a_tag:
                            fac_titles.append(norm_ws(div_text))
                            bio_links.append(a_tag["href"])

            # WRITE
            with open(
                os.path.join(self.output_dir, output_file),
                "x",
                newline="",
                encoding="utf-8",
            ) as f:
                writer = csv.writer(f)
                for faculty in zip(fac_titles, bio_links):
                    writer.writerow(faculty)


if __name__ == "__main__":
    B2Compiler().collect()
