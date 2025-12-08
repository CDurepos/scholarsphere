"""
Author: Aidan Bell
"""

from scraping.utils import get_headers
from scraping.umo.utils.normalize_whitespace import norm_ws

import os
import csv
import requests
from bs4 import BeautifulSoup

DEPARTMENTS = (
    ("https://umaine.edu/marine/people/department/faculty/", "marine_sciences.csv"),
    (
        "https://gsbse.umaine.edu/people/department/faculty/",
        "biomedical_science_and_engineering.csv",
    ),
    (
        "https://forest.umaine.edu/people/department/faculty-staff/",
        "forest_resources.csv",
    ),
)


class B1Compiler:
    """
    Collect biography page links for a set of departments.

    Usage:
        compiler = B1Compiler()
        compiler.collect()
    """

    def __init__(self, output_dir:str):
        self.output_dir = output_dir
        self.departments = DEPARTMENTS
        os.makedirs(self.output_dir, exist_ok=True)
        self.headers = get_headers("h1")

    def collect(self):
        for url, output_file in self.departments:
            output_path = os.path.join(self.output_dir, output_file)
            
            if os.path.exists(output_path):
                print(f"[SKIP] {output_file} already exists, skipping...")
                continue
            
            fac_titles = []
            bio_links = []
            curr_page = 1
            while True:
                try:
                    response = requests.get(
                        url + f"/page/{curr_page}/", headers=self.headers
                    )
                    response.raise_for_status()
                except requests.RequestException as e:
                    break

                soup = BeautifulSoup(response.text, "html.parser")
                faculty = soup.find_all("div", class_="people-wrapper")
                for tag in faculty:
                    fac_position = tag.find("p", class_="people-wrapper__position")
                    if (
                        fac_position
                        and "professor" in fac_position.text.lower()
                        and "retired" not in fac_position.text.lower()
                    ):
                        # Find <a> tags that mention "bio" or "biography" or "staff page"
                        for p_tag in tag.find_all("p", class_=lambda c: c is None):
                            a_tag = p_tag.next_element
                            if (
                                a_tag
                                and " bio" in a_tag.text.lower()
                                or " biography" in a_tag.text.lower()
                                or " staff page" in a_tag.text.lower()
                            ):
                                fac_titles.append(norm_ws(fac_position.text.strip()))
                                bio_links.append(a_tag["href"])

                curr_page += 1

            # WRITE
            with open(
                output_path,
                "w",
                newline="",
                encoding="utf-8",
            ) as f:
                writer = csv.writer(f)
                for faculty in zip(fac_titles, bio_links):
                    writer.writerow(faculty)


if __name__ == "__main__":
    B1Compiler().collect()
