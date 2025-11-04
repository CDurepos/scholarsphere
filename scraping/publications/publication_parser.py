from scraping.utils import get_headers
from scraping.dataclasses import Publication

import re
import requests


def citation_to_publication_instance(citation: str) -> Publication:
    """
    Pipelines functions from this module to convert a citation into an instance
    of the "Publication" dataclass.

    Args:
        citation (str): A citation that might contain a DOI.

    Returns:
        an instance of the "Publication" dataclass with fields filled in by crossref info,
        or None if crossref could not find the Publication or an error occured.
    """
    doi = extract_doi(citation=citation)
    if doi:
        pub_data = crossref_from_doi(doi=doi)
    else:
        pub_data = crossref_from_citation_text(citation=citation)
        # TODO: It is important to prevent instances where the wrong paper is returned for the citation.
        # Crossref sorts the returned papers by a relevance score if a query is used in the API call.
        # The scoring is not consistent across queries, so I followed the advice of a crossref dev
        # and normalize by query length for now: https://community.crossref.org/t/query-affiliation/2009/4
        threshold = 2 #TODO Tune this
        relevance_score = pub_data.get("score", 0) / len(citation)
        if relevance_score < threshold:
            return None

    if pub_data:
        publication = Publication(
            doi=doi,
            title=pub_data.get("title", [None])[0],
            abstract=pub_data.get("abstract"),
            year=pub_data.get("created", {}).get("date-parts", [[None]])[0][0],
            citation_count=pub_data.get("is-referenced-by-count"),
            publisher=pub_data.get("publisher"),
        )
        return publication
    return None


def extract_doi(citation: str) -> str | None:
    """
    Extract a DOI from a text string using a regex.

    Args:
        citation (str): A citation that might contain a DOI.

    Returns:
        the DOI (str) or None if not found.
    """
    # DOI pattern per Crossref specs (prefix/suffix)
    doi_pattern = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
    match = doi_pattern.search(citation)
    if match:
        # Clean up trailing punctuation
        return match.group(0).rstrip(".,);")
    return None


def crossref_from_doi(doi: str) -> dict:
    """
    Query Crossref's REST API for JSON metadata given a DOI.

    Args:
        doi (str): The DOI to query crossref with.

    Returns:
        a dict with JSON metadata or None if request fails.
    """
    url = f"https://api.crossref.org/works/{doi}"
    headers = get_headers("h1")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json().get("message", {})
    except requests.RequestException as e:
        print(f"Error fetching Crossref metadata: {e}")
        return {}


def crossref_from_citation_text(citation: str) -> dict:
    """
    Query Crossref's REST API for JSON metadata given a citation.
    NOTE: If the citation has a DOI, crossref_from_doi will be
    more reliable.

    Args:
        citation (str): The citation to query crossref with.

    Returns:
        a dict with JSON metadata or None if request fails.
    """
    query = citation[:2000]  # Safety against query length limits
    url = f"https://api.crossref.org/works"
    headers = get_headers("h1")
    try:
        response = requests.get(
            url, headers=headers, params={"query.bibliographic": query}, timeout=10
        )
        response.raise_for_status()
        items = response.json().get("message", {}).get("items", [])
        if items:
            return items[0]
        else:
            return {}
    except requests.RequestException as e:
        print(f"Error fetching Crossref metadata: {e}")
        return {}


if __name__ == "__main__":
    # Sample DOI citations
    citation1 = """Perry, E.S., W.R. Miller & S. Lindsay. 2015. Looking at tardigrades in a new light: using epifluorescence to interpret structure. Journal of Microscopy. 257 (2), 117-122 doi:10.1111/jmi.12190"""
    citation2 = """Burman, M.A., Erickson, K.J., Deal, A.L. & Jacobson, R.E. (2014) Contextual and Auditory Fear Conditioning Continue to Emerge during the Periweaning Period in Rats. PLoS ONE 9(6): e100807. doi:10.1371/journal.pone.0100807."""
    citation3 = """Inserting an 'Atomic Trap' for Directional Dopant Migration in Core/Multi-Shell Quantum Dots.” C. Chu, E. Hofman, C. Gao, S. Li, H. Lin, W. MacSwain, J. M. Franck, R. W. Meulenberg, A. Chakraborty, W. Zheng, Chem. Sci., 14, 14115-14123 (2023). https://doi.org/10.1039/D3SC04165D"""

    # Sample no DOI citations
    citation4 = """N.S. Mandal, A. Sen, and R.D. Astumian, “Kinetic Asymmetry versus Dissipation in the Evolution of Chemical Systems as Exemplified by Single Enzyme Chemotaxis,” J Am Chem Soc 145(10), 5730-5738 (2023)."""

    import os
    from scraping.processing.csv_converter import dataclass_instances_to_csv

    inst = citation_to_publication_instance(citation3)
    dataclass_instances_to_csv(
        [inst],
        os.path.join("scraping", "UMO", "scrape_storage", "pub_test.csv"),
        overwrite=True,
    )
