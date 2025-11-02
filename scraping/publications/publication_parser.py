import re
import requests
from scraping.utils import get_headers
from scraping.dataclasses.publication import Publication


def citation_to_publication_instance(citation: str) -> Publication:
    """
    Pipelines functions from this module to convert a citation into an instance
    of the "Publication" dataclass. NOTE: The citation currently needs
    to contain a DOI for this to function properly.

    Args:
        citation (str): A citation that might contain a DOI.

    Returns:
        an instance of the "Publication" dataclass with fields filled in by crossref info
    """
    doi = extract_doi(citation=citation)
    if not doi:
        return
    
    pub_data = fetch_crossref_metadata(doi=doi)
    publication = Publication(
        DOI=doi,
        title=pub_data.get("title", [None])[0],
        abstract=pub_data.get("abstract"),
        year = pub_data.get("created", {}).get("date-parts", [[None]])[0][0],
        citation_count=pub_data.get("is-referenced-by-count"),
        publisher=pub_data.get("publisher")
    )
    return publication

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


def fetch_crossref_metadata(doi: str) -> dict | None:
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
        return None


if __name__ == "__main__":
    # Sample citation
    citation = """Perry, E.S., W.R. Miller & S. Lindsay. 2015. Looking at tardigrades in a new light: using epifluorescence to interpret structure. Journal of Microscopy. 257 (2), 117-122 doi:10.1111/jmi.12190"""
    citation_to_publication_instance(citation)
