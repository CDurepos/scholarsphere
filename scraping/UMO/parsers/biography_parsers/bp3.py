from scraping.utils import get_headers
from scraping.dataclasses import Faculty
from scraping.publications import CitationExtractor
from scraping.publications.publication_parser import citation_to_publication_instance

import os
import re
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

DEPARTMENTS = (("https://umaine.edu/business/faculty-and-staff/", "business.csv"),)


class B3Parser:
    """Collect faculty data from biography pages.

    Usage:
        parser = B3Parser()
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
        citation_extractor = CitationExtractor()
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
                name_container = soup.find(["h1"], class_=["page-title single-title"])
                if name_container:
                    name = name_container.text
                    if name and isinstance(name, str):
                        name = name.split(",")[0]  # Get rid of degree (e.g. ', Ph.D')
                        name_split = name.split()
                        if len(name_split) > 1:
                            fac_inst.first_name = name_split[0]
                            fac_inst.last_name = name_split[-1]
                        else:
                            fac_inst.first_name = name

                # Extract email
                email_container = soup.find("p", class_="people-wrapper__email")
                if email_container:
                    anchor = email_container.find("a", href=True)
                    if anchor:
                        fac_inst.email = anchor[href].removeprefix("mailto:")

                # Extract publications
                h_tag = soup.find(
                    [f"h{i}" for i in range(1, 7)],
                    string=lambda text: text and "publications" in text.lower(),
                )
                citations = None
                if not h_tag:
                    # Assume in this case that there must be an href to publications like in forest pages
                    a_tag = soup.find(
                        "a",
                        href=True,
                        string=lambda text: text and "publications" in text.lower(),
                    )
                    if a_tag:
                        try:
                            response = requests.get(
                                a_tag["href"], headers=self.headers, timeout=10
                            )
                            if response.status_code != 200:
                                continue
                        except requests.RequestException as e:
                            continue
                        # Can't guarantee any consistent format, so just try from body
                        publication_soup = BeautifulSoup(response.text, "html.parser")
                        body = publication_soup.find("body")
                        if body:
                            citations = citation_extractor.tag_to_citation(tag=body)
                else:
                    # Go through list
                    # TODO: Probably allow more than just list tags. Some pages store citations in <p>
                    list_tag = None
                    for sibling in h_tag.next_siblings:
                        if isinstance(sibling, str):  # Skip text nodes like "\n"
                            continue
                        if sibling.name in ("ul", "ol"):
                            list_tag = sibling
                            break
                        list_tag = sibling.find(["ul", "ol"])
                        if list_tag:
                            break
                    if list_tag:
                        citations = citation_extractor.tag_to_citation(tag=list_tag)
                pub_insts = []
                if citations:
                    # Convert all citations to Publication dataclass instances
                    citation_lim = (
                        10  # Maximum number of potential citations to process
                    )
                    for citation in citations[:citation_lim]:
                        pub_insts.append(
                            citation_to_publication_instance(citation=citation)
                        )

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
    parser = B3Parser()
    f, p = parser.parse()
    print("done")
