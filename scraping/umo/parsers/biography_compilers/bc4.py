from scraping.utils import get_headers
from scraping.umo.utils.normalize_whitespace import norm_ws

import os
import csv
import requests
from bs4 import BeautifulSoup, NavigableString

DEPARTMENTS = (
    ("https://sbe.umaine.edu/personnel/faculty/", "biology_and_ecology.csv"),
    ("https://physics.umaine.edu/people-2/", "physics_and_astronomy.csv"),
)


class B4Compiler:
    """
    Collect biography page links for a set of departments.

    Usage:
        compiler = B4Compiler()
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
            for p_tag in soup.find_all("p", class_="kt-blocks-info-box-text"):
                p_text = p_tag.contents[0]
                if (
                    p_text
                    and isinstance(p_text, NavigableString)
                    and "professor" in p_text.lower()
                    and "emeritus" not in p_text.lower()
                    and "emerita" not in p_text.lower()
                ):
                    a_tags = p_tag.find_all("a", href=True)
                    if a_tags:
                        p_text = p_text.replace(" |", "")
                        fac_titles.append(norm_ws(p_text.strip()))
                        bio_links.append(a_tags[-1]["href"])
                        
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
    B4Compiler().collect()
