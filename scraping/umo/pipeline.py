from scraping.umo.dataclass_instances.orono import umaine
from scraping.utils.conversion import dataclass_instances_to_csv
from scraping.schemas import Faculty, Publication, PublicationAuthoredByFaculty
from scraping.umo.processing.post_process_pipeline import post_process_faculty_csv

import os
import importlib
from tqdm import tqdm
from itertools import chain
from typing import Union, List, Any

# CFG
COMPILER_OUTPUT_DIR = os.path.join(
    "scraping", "umo", "scrape_storage", "biography_pages"
)  # Relative to cwd

TOTAL_COMPILERS = 5
TOTAL_PARSERS = 5

FAC_OUTPUT_FILE = os.path.join("scraping", "out", "umo_faculty_raw.csv")
PUB_OUTPUT_FILE = os.path.join("scraping", "out", "umo_publication_raw.csv")
JOIN_OUTPUT_FILE = os.path.join(
    "scraping", "out", "umo_publication_authored_by_faculty_raw.csv"
)
FAC_FILTERED_OUTPUT_FILE = os.path.join("scraping", "out", "umo_faculty_filtered.csv")

os.makedirs(os.path.dirname(FAC_OUTPUT_FILE), exist_ok=True)
os.makedirs(os.path.dirname(PUB_OUTPUT_FILE), exist_ok=True)
os.makedirs(os.path.dirname(JOIN_OUTPUT_FILE), exist_ok=True)
os.makedirs(os.path.dirname(FAC_FILTERED_OUTPUT_FILE), exist_ok=True)

if os.path.exists(FAC_OUTPUT_FILE):
    raise FileExistsError(f"The output file '{FAC_OUTPUT_FILE}' already exists.")
if os.path.exists(PUB_OUTPUT_FILE):
    raise FileExistsError(f"The output file '{PUB_OUTPUT_FILE}' already exists.")
if os.path.exists(JOIN_OUTPUT_FILE):
    raise FileExistsError(f"The output file '{JOIN_OUTPUT_FILE}' already exists.")
if os.path.exists(FAC_FILTERED_OUTPUT_FILE):
    raise FileExistsError(
        f"The output file '{FAC_FILTERED_OUTPUT_FILE}' already exists."
    )


def pipeline(steps: Union[int, list[int]] = None) -> None:
    """
    Run the full UMO faculty data scraping pipeline, or specific steps of the pipeline.

    Args:
        steps: A single int value specifying which step to start at, or a list of ints specifying which steps to perform. If None, all steps will be performed.
    """
    STEPS = [step_1, step_2, step_3]
    if steps is None:
        step_choices = STEPS
    elif type(steps) == int:
        step_choices = [STEPS[i] for i in range(steps - 1, len(STEPS))]
    elif type(steps) == list:
        step_choices = [STEPS[i] for i in steps]
    else:
        print("Invalid type for 'steps' arg. No steps were performed.")
        return

    for step in step_choices:
        step()


def step_1():
    # Output .csv files containing links to faculty biography pages
    compiler_names = ["bc" + str(i + 1) for i in range(TOTAL_COMPILERS)]
    for idx, name in enumerate(
        tqdm(compiler_names, "Gathering biography links", total=len(compiler_names))
    ):
        module = importlib.import_module(
            f"scraping.umo.parsers.biography_compilers.{name}"
        )
        compiler_class = getattr(module, f"B{idx+1}Compiler")
        compiler_class(COMPILER_OUTPUT_DIR).collect()


def step_2():
    # Scrape faculty biography pages and build "Faculty" and "Publication" dataclass instances
    all_fac_instances: List[Faculty] = []
    all_pub_instances: List[List[Publication]] = []
    parser_names = ["bp" + str(i + 1) for i in range(TOTAL_PARSERS)]
    for idx, name in enumerate(
        tqdm(parser_names, "Scraping biographys", total=len(parser_names))
    ):
        module = importlib.import_module(
            f"scraping.umo.parsers.biography_parsers.{name}"
        )
        parser_class = getattr(module, f"B{idx+1}Parser")
        fac_instances, pub_instances = parser_class(COMPILER_OUTPUT_DIR).parse()
        all_fac_instances += fac_instances
        all_pub_instances += pub_instances

    assert len(all_fac_instances) == len(all_pub_instances)
    # TODO: Make join table here, and then unwind publications
    # Make join table and generate temporary incremental ids
    temp_fac_id = 0
    temp_pub_id = 0
    join_table_instances = []
    for fac, publication_list in zip(all_fac_instances, all_pub_instances):
        fac.faculty_id = temp_fac_id
        temp_fac_id += 1
        for pub in publication_list:
            pub.publication_id = temp_pub_id
            temp_pub_id += 1
            join_table_instances.append(
                PublicationAuthoredByFaculty(fac.faculty_id, pub.publication_id)
            )

    all_pub_instances = list(
        chain.from_iterable(all_pub_instances)
    )  # Flatten nested lists
    dataclass_instances_to_csv(
        all_fac_instances, output_path=FAC_OUTPUT_FILE, overwrite=True
    )
    dataclass_instances_to_csv(
        all_pub_instances, output_path=PUB_OUTPUT_FILE, overwrite=True
    )
    dataclass_instances_to_csv(
        join_table_instances, output_path=JOIN_OUTPUT_FILE, overwrite=True
    )


def step_3():
    # Post-process faculty data: remove duplicates and entries without first names
    post_process_faculty_csv(
        fac_input_file=FAC_OUTPUT_FILE, join_input_file=JOIN_OUTPUT_FILE, pub_input_file=PUB_OUTPUT_FILE, fac_output_file=FAC_FILTERED_OUTPUT_FILE
    )


if __name__ == "__main__":
    pipeline(2)
