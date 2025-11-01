import os
import csv
import requests
from bs4 import BeautifulSoup
from scraping.UMO.utils import get_header

DEPARTMENTS = (("https://umaine.edu/history/faculty/", "history.csv"),)


class B5Compiler:
    """
    Collect biography page links for a set of departments.

    Usage:
        compiler = B5Compiler()
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
            for profile_anchor in soup.find_all(
                "a", class_="wp-block-kadence-singlebtn"
            ):
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
                os.path.join(self.output_dir, output_file),
                "x",
                newline="",
                encoding="utf-8",
            ) as f:
                writer = csv.writer(f)
                for link in bio_links:
                    writer.writerow([link])

if __name__ == "__main__":
    B5Compiler().collect()