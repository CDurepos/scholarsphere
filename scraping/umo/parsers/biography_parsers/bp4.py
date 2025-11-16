from scraping.utils import get_headers
from scraping.schemas import Faculty
from scraping.publications import CitationExtractor
from scraping.umo.utils.parse_name import split_name
from scraping.publications.publication_parser import citation_to_publication_instance

import os
import re
import csv
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

DEPARTMENTS = (
    ("https://sbe.umaine.edu/personnel/faculty/", "biology_and_ecology.csv"),
    ("https://physics.umaine.edu/people-2/", "physics_and_astronomy.csv"),
)


class B4Parser:
    """Collect faculty data from biography pages.

    Usage:
        parser = B4Parser()
        parser.parse()
    """

    def __init__(self, input_dir:str):
        self.input_dir = input_dir
        # Gather input files
        self.input_file_paths = []
        for url, input_file in DEPARTMENTS:
            if not os.path.exists(os.path.join(self.input_dir, input_file)):
                raise FileNotFoundError(
                    f"The input file '{os.path.join(self.input_dir, input_file)}' could not be found. Make sure you've ran the biography compiler first."
                )
            else:
                self.input_file_paths.append(os.path.join(self.input_dir, input_file))
        self.headers = get_headers("h1")

    def parse(self):
        """
        Parse biography pages into Faculty and Publication schemas.

        Returns:
            fac_instances (list[Faculty]): A list of all Faculty instances obtained from this module's biography lists
            pub_instances (list[list[Publication]]): A list of all Publication instances of each faculty from this module's biography lists
            NOTE: fac_instances and pub_instances indices correspond to each other. pub_instances[0] is a list of all publications by fac_instances[0]
        """
        citation_extractor = CitationExtractor()
        fac_instances = []
        pub_instances = []
        for idx, path in enumerate(self.input_file_paths):
            with open(path, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                fac_titles = []
                bio_urls = []
                for row in reader:
                    fac_titles.append(row[0])
                    bio_urls.append(row[1])
            for fac_title, bio_url in tqdm(
                zip(fac_titles, bio_urls),
                desc=f"Parsing biography for department {idx+1}/{len(DEPARTMENTS)}",
                total=len(fac_titles),
            ):
                try:
                    response = requests.get(bio_url, headers=self.headers, timeout=10)
                    response.raise_for_status()
                except requests.RequestException as e:
                    print(e)
                    continue

                soup = BeautifulSoup(response.text, "html.parser")
                fac_inst = Faculty()
                # Set title
                fac_inst.title = fac_title.split(", ")

                # Set department
                fac_inst.department = os.path.basename(path)[:-4]

                # Set scraped from location
                fac_inst.scraped_from = bio_url

                # Extract name
                name_container = soup.find(["h1"], class_=["page-title single-title"])
                if not name_container:
                    name_container = soup.find(["h2"], class_=["page-title"])
                if name_container:
                    name = name_container.text
                    if name and isinstance(name, str):
                        first, last = split_name(name)
                        fac_inst.first_name = first
                        fac_inst.last_name = last

                # Extract email
                email_container = soup.find("p", class_="people-wrapper__email")
                if email_container:
                    anchor = email_container.find("a", href=True)
                    if anchor:
                        fac_inst.email = anchor["href"].removeprefix("mailto:")

                # Extract publications
                h_tag = soup.find("div", class_="page-content") # This department isn't formatted well, so have to just start from here.
                citations = None
                if h_tag:
                    citations = citation_extractor.tag_to_citations(tag=h_tag)
                pub_insts = []
                if citations:
                    # Convert all citations to Publication dataclass instances
                    citation_lim = (
                        10  # Maximum number of potential citations to process
                    )
                    fac_first_name = fac_inst.first_name if fac_inst.first_name else ""
                    fac_last_name = fac_inst.last_name if fac_inst.last_name else ""
                    for citation in citations[:citation_lim]:
                        pub_inst = citation_to_publication_instance(citation=citation, author_name=fac_first_name + " " + fac_last_name)
                        if pub_inst:
                            pub_insts.append(pub_inst)

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
                pub_instances.append(pub_insts)

        assert len(fac_instances) == len(pub_instances)
        return fac_instances, pub_instances


if __name__ == "__main__":
    parser = B4Parser()
    f, p = parser.parse()
    print("done")
