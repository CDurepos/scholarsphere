from scraping.utils import get_headers
from scraping.publications import CitationExtractor
from scraping.UMO.dataclass_instances.orono import umaine
from scraping.publications.publication_parser import citation_to_publication_instance

import os
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


class B1Parser:
    """Collect faculty data from biography pages.

    Usage:
        parser = B1Parser()
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
        citation_extractor = CitationExtractor()
        faculty_instances = []
        publication_instances = []
        institution_instance = [umaine]
        for path in self.input_file_paths:
            with open(path, "r") as f:
                bio_urls = [line.strip() for line in f.readlines()]
            for bio_url in bio_urls:
                try:
                    response = requests.get(bio_url, headers=self.headers, timeout=10)
                    if response.status_code != 200:
                        continue
                except requests.RequestException as e:
                    continue
                
                # Extract paper citations
                soup = BeautifulSoup(response.text, "html.parser")
                h_tag = soup.find([f"h{i}" for i in range(1, 7)], string=lambda text: text and "publications" in text.lower())
                citations = None
                if not h_tag:
                    # assume in this case that there must be an href to publications like in forest pages
                    a_tag = soup.find("a", href=True, string=lambda text: text and "publications" in text.lower())
                    if a_tag:
                        # go through href
                        try:
                            response = requests.get(a_tag["href"], headers=self.headers, timeout=10)
                            if response.status_code != 200:
                                continue
                        except requests.RequestException as e:
                            continue
                        # can't guarantee any consistent format, so just try from body
                        publication_soup = BeautifulSoup(response.text, "html.parser")
                        body = publication_soup.find("body")
                        if body:
                            citations = citation_extractor.tag_to_citation(tag=body)
                else:
                    # go through list
                    #TODO: Probably allow more than just list tags. Some pages store citations in <p>
                    list_tag = None
                    for sibling in h_tag.next_siblings:
                        if isinstance(sibling, str):  # skip text nodes like "\n"
                            continue
                        if sibling.name in ("ul", "ol"):
                            list_tag = sibling
                            break
                        list_tag = sibling.find(["ul", "ol"])
                        if list_tag:
                            break
                    if list_tag:
                        citations = citation_extractor.tag_to_citation(tag=list_tag)
                
                if citations:
                    # convert all citations to Publication dataclass instances
                    for citation in citations:
                        pub_inst = citation_to_publication_instance(citation=citation)

if __name__ == "__main__":
    parser = B1Parser()
    parser.parse()