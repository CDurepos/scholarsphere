from scraping.utils import get_headers
from scraping.UMO.dataclass_instances.orono import umaine

import os
import requests

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
        for url, input_file in self.departments:
            if not os.path.exists(os.path.join(self.input_dir, input_file)):
                raise FileNotFoundError(
                    f"The input file '{os.path.join(self.input_dir, input_file)}' could not be found. Make sure you've ran the biography compiler first."
                )
            else:
                self.input_file_paths.append(os.path.join(self.input_dir, input_file))

        # Check that output files don't exist and create dirs if needed
        for url, output_file in self.departments:
            if os.path.exists(os.path.join(self.output_dir, output_file)):
                raise FileExistsError(
                    f"The output file '{os.path.join(self.output_dir, output_file)}' already exists."
                )
        os.makedirs(self.output_dir, exist_ok=True)

        self.headers = get_headers("h1")

    def parse(self):
        for path in self.input_file_paths:
            with open(path, "r") as f:
                bio_urls = f.readlines()
            for bio_url in bio_urls:
                requests.get(bio_url, headers=self.headers)
