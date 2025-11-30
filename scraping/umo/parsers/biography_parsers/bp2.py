from scraping.schemas import Faculty
from scraping.utils import get_headers
from scraping.umo.utils.parse_name import split_name
from scraping.umo.utils.normalize_whitespace import norm_ws

import os
import re
import csv
import uuid
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup, NavigableString

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

    def __init__(self, input_dir: str):
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

                # Set faculty ID
                fac_inst.faculty_id = str(uuid.uuid4())

                # Set title
                fac_inst.title = fac_title.split(", ")

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
                        name_text = name.get_text(strip=True)
                        if name_text:
                            cleaned = re.sub(r"\([^)]*\)", "", name_text).strip()
                            first, last = split_name(cleaned)
                            fac_inst.first_name = first
                            fac_inst.last_name = last

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

                # Extract biography / research description
                strong = soup.find(
                    "strong",
                    text=lambda text: text
                    and (
                        "research interest" in text.lower()
                        or "research interests" in text.lower()
                        or "research areas" in text.lower()
                    ),
                )
                if strong:
                    fac_inst.biography = ""
                    parent = strong.parent
                    for sib in parent.next_siblings:
                        # Skip empty whitespace text nodes
                        if isinstance(sib, NavigableString):
                            continue

                        if sib.name not in ["p", "ul", "ol"]:
                            break

                        elif (
                            sib.find("strong") is not None
                            or sib.find([f"h{i}" for i in range(2, 4)]) is not None
                        ):
                            break

                        # Handle paragraphs
                        if sib.name == "p":
                            text = norm_ws(sib.get_text(" ", strip=True))
                            if text:
                                fac_inst.biography += text

                        # Handle list items inside ul/ol
                        elif sib.name in ["ul", "ol"]:
                            for li in sib.find_all("li"):
                                text = norm_ws(li.get_text(" ", strip=True))
                                if text:
                                    fac_inst.biography += text

                else:
                    h_tag = soup.find(
                        [f"h{i}" for i in range(2, 4)],
                        text=lambda text: text
                        and (
                            "research interest" in text.lower()
                            or "research interests" in text.lower()
                            or "research areas" in text.lower()
                        ),
                    )
                    if h_tag:
                        fac_inst.biography = ""
                        parent = h_tag.parent
                        for sib in parent.next_siblings:
                            # Skip empty whitespace text nodes
                            if isinstance(sib, NavigableString):
                                continue

                            if sib.name not in ["p", "ul", "ol"]:
                                break

                            elif (
                                sib.find("strong") is not None
                                or sib.find([f"h{i}" for i in range(2, 4)]) is not None
                            ):
                                break

                            # Handle paragraphs
                            if sib.name == "p":
                                text = norm_ws(sib.get_text(" ", strip=True))
                                if text:
                                    fac_inst.biography += text

                            # Handle list items inside ul/ol
                            elif sib.name in ["ul", "ol"]:
                                for li in sib.find_all("li"):
                                    text = norm_ws(li.get_text(" ", strip=True))
                                    if text:
                                        fac_inst.biography += text

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
                pub_instances.append([])  # No publications for these pages

        assert len(fac_instances) == len(pub_instances)
        return fac_instances, pub_instances


if __name__ == "__main__":
    parser = B2Parser(
        input_dir=os.path.join("scraping", "umo", "scrape_storage", "biography_pages")
    )
    f, p = parser.parse()
    print("done")
