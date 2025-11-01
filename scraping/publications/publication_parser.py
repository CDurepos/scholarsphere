import re
import requests
from scraping.utils import get_headers


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


def process_citation(citation: str):
    doi = extract_doi(citation)
    if not doi:
        return

    metadata = fetch_crossref_metadata(doi)
    if metadata:
        print("Sucess")


if __name__ == "__main__":
    # Sample citation
    citation = """Perry, E.S., W.R. Miller & S. Lindsay. 2015. Looking at tardigrades in a new light: using epifluorescence to interpret structure. Journal of Microscopy. 257 (2), 117-122 doi:10.1111/jmi.12190"""
    process_citation(citation)
