from scraping.utils import get_headers
from scraping.dataclasses import Faculty

import os
import re
import requests
from tqdm import tqdm
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


class B2Parser:
    """Collect faculty data from biography pages.

    Usage:
        parser = B2Parser()
        parser.parse()
    """

    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.input_dir = os.path.join(
            script_dir, "../../scrape_storage/biography_pages/"
        )
        self.output_dir = os.path.join(script_dir, "../../scrape_storage/faculty_data/")
        # Gather input files
        self.input_file_paths = []
        for url, input_file in DEPARTMENTS:
            if not os.path.exists(os.path.join(self.input_dir, input_file)):
                raise FileNotFoundError(
                    f"The input file '{os.path.join(self.input_dir, input_file)}' could not be found. Make sure you've ran the biography compiler first."
                )
            else:
                self.input_file_paths.append(os.path.join(self.input_dir, input_file))

        # Check that output files don't exist and create dirs if needed
        for url, output_file in DEPARTMENTS:
            if os.path.exists(os.path.join(self.output_dir, output_file)):
                raise FileExistsError(
                    f"The output file '{os.path.join(self.output_dir, output_file)}' already exists."
                )
        os.makedirs(self.output_dir, exist_ok=True)

        self.headers = get_headers("h1")

    def parse(self):
        """
        Parse biography pages into Faculty and Publication dataclasses.

        Returns:
            fac_instances (list[Faculty]): A list of all Faculty instances obtained from this module's biography lists
            pub_instances (list[list[Publication]]): A list of all Publication instances of each faculty from this module's biography lists
            NOTE: fac_instances and pub_instances indices correspond to each other. pub_instances[0] is a list of all publications by fac_instances[0]
        """
        fac_instances = []
        pub_instances = []
        for idx, path in enumerate(self.input_file_paths):
            with open(path, "r") as f:
                fac_titles = []
                bio_urls = []
                for line in f.readlines():
                    items = line.strip().split(",")
                    fac_titles.append(items[0])
                    bio_urls.append(items[1])
            for fac_title, bio_url in tqdm(
                zip(fac_titles, bio_urls),
                desc=f"Parsing biography for department {idx+1}/{len(DEPARTMENTS)}",
                total=len(fac_titles),
            ):
                try:
                    response = requests.get(bio_url, headers=self.headers, timeout=10)
                    if response.status_code != 200:
                        continue
                except requests.RequestException as e:
                    continue

                soup = BeautifulSoup(response.text, "html.parser")
                fac_inst = Faculty()
                # Set title
                fac_inst.title = fac_title

                # Set department
                fac_inst.department = os.path.basename(path)[:-4]

                # Set scraped from location
                fac_inst.scraped_from = bio_url

                # Extract name
                name_container = soup.find(
                    ["h2"], class_=["wp-block-kadence-advancedheading"]
                )
                if name_container:
                    name = name_container.find("strong")
                    if name:
                        name_split = name.split()
                        if len(name_split) > 1:
                            fac_inst.first_name = name_split[0]
                            fac_inst.last_name = name_split[-1]
                        else:
                            fac_inst.first_name = name

                # Extract email
                email_pattern = re.compile(
                    r"(?:mailto:)?([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})",
                    re.IGNORECASE,
                )
                possible_email_containers = soup.find_all(
                    "div", class_="kt-inside-inner-col"
                )
                for div in possible_email_containers:
                    if fac_inst.email is not None:
                        break  # Must have found a match in anchor loop
                    anchors = div.find_all("a", href=True)
                    for (
                        anchor
                    ) in (
                        anchors
                    ):  # TODO: Some emails aren't links, so this won't always work
                        possible_email_match = email_pattern.search(
                            anchor.get_text(" ", strip=True)
                        )
                        if possible_email_match:
                            fac_inst.email = possible_email_match.group()
                            break

                # Extract google scholar, research gate, and orcid urls
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if "scholar.google." in href:
                        fac_inst.google_scholar_url = href
                    elif "researchgate.net" in href:
                        fac_inst.research_gate_url = href
                    elif "orcid.org" in href:
                        orcid_match = re.search(
                            r"(\d{4}-\d{4}-\d{4}-\d{3}[0-9X])", href
                        )
                        if orcid_match:
                            fac_inst.orcid = orcid_match.group(1)

                fac_instances.append(fac_inst)
                pub_instances.append([]) # No publications for these pages

        assert len(fac_instances) == len(pub_instances)
        return fac_instances, pub_instances


if __name__ == "__main__":
    parser = B2Parser()
    f, p = parser.parse()
    print("done")
