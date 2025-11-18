from scraping.utils import get_headers
from scraping.umo.utils.normalize_whitespace import norm_ws

import os
import csv
import requests
from bs4 import BeautifulSoup, NavigableString

DEPARTMENTS = (("https://umaine.edu/business/faculty-and-staff/", "business.csv"),)


class B3Compiler:
    """
    Collect biography page links for a set of departments.

    Usage:
        compiler = B3Compiler()
        compiler.collect()
    """

    def __init__(self, output_dir: str):
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
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            fac_titles = []
            bio_links = []
            people_divs = {
                "faculty_div": soup.find("div", class_="kb-row-layout-wrap kb-row-layout-id28745_1da6a3-f0 alignnone wp-block-kadence-rowlayout"),
                "admin_div": soup.find("div", class_="kb-row-layout-wrap kb-row-layout-id28745_6ef6ea-b0 alignnone wp-block-kadence-rowlayout"),
            }


            for people_div in people_divs.values():
                if not people_div:
                    continue
                for parent_div in people_div.find_all(
                    "div", class_="kt-infobox-textcontent"
                ):
                    child_div = parent_div.find("p", class_="kt-blocks-info-box-text")
                    if not child_div:
                        continue
                    else:
                        title = child_div.contents[0]
                        if (
                            not title
                            or not isinstance(title, NavigableString)
                            or not "professor" in title.lower()
                        ):
                            continue
                        # Find <a> tags that mention "Bio"
                        for a_tag in child_div.find_all("a", href=True):
                            if "bio" in a_tag.text.lower():
                                fac_titles.append(norm_ws(title))
                                bio_links.append(a_tag["href"])

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
    B3Compiler("test.csv").collect()
