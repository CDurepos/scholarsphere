import os
import csv
import requests
from bs4 import BeautifulSoup
from scraping.UMO.utils import get_header

DEPARTMENTS = (("https://umaine.edu/business/faculty-and-staff/", "business.csv"),)


class B3Compiler:
    """
    Collect biography page links for a set of departments.

    Usage:
        compiler = B3Compiler()
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
            faculty_header = soup.find(
                "h2",
                class_="kt-adv-heading28745_a68738-c8 wp-block-kadence-advancedheading",
            )

            if faculty_header and faculty_header.find("strong", string="Faculty"):
                next_section = faculty_header.find_next_sibling()

                if next_section:
                    for parent_div in next_section.find_all(
                        "div", class_="kt-infobox-textcontent"
                    ):
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
    B3Compiler().collect()