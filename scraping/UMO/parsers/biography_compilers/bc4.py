import os
import csv
import requests
from bs4 import BeautifulSoup
from scraping.UMO.utils import get_header

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
            for p_tag in soup.find_all("p", class_="kt-blocks-info-box-text"):
                p_text = p_tag.get_text(strip=True).lower()
                if (
                    "professor" in p_text
                    and "emeritus" not in p_text
                    and "emerita" not in p_text
                ):
                    a_tags = p_tag.find_all("a", href=True)
                    if a_tags:
                        bio_links.append(a_tags[-1]["href"])

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

if __name__ == "__main__":
    B4Compiler().collect()