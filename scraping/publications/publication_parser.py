from scraping.utils import get_headers
from scraping.schemas import Publication
from scraping.umo.utils.normalize_whitespace import norm_ws

import re
import html
import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher


def doi_to_publication_instance(doi: str) -> Publication:
    """
    Pipelines functions from this module to convert a doi into an instance
    of the "Publication" dataclass.
    """
    pub_data = crossref_from_doi(doi=doi)
    if pub_data:
        return pub_data_to_publication_instance(pub_data=pub_data, doi=doi)

    return None


def citation_to_publication_instance(
    citation: str,
    author_name: str = None,
    relevance_threshold: float = 3.0,
    author_sim_threshold: float = 0.75,
) -> Publication:
    """
    Pipelines functions from this module to convert a citation into an instance
    of the "Publication" dataclass.

    Args:
        citation (str): A citation that might contain a DOI.
        author_name (str): The name of the author to aid in filtering incorrect matches ("first_name ?middle_name(s) last_name").
        NOTE: author_name arg is only useful when citation does not contain a DOI.
        relevance_threshold (float): The minimum score to consider a publication match, where score is roughly: (elastic_search_bm25 / citation_word_count).
        author_sim_threshold (float): The minimum similarity score between the provided author_name arg, and an author found in the publication match (0.0 - 1.0).

    Returns:
        an instance of the "Publication" dataclass with fields filled in by crossref info,
        or None if crossref could not find the Publication or an error occured.
    """
    doi = extract_doi(citation=citation)
    if doi:
        return doi_to_publication_instance(doi=doi)
    else:
        pub_data = crossref_from_citation_text(citation=citation)

    if pub_data:
        # TODO: It is important to prevent instances where the wrong paper is returned for the citation.
        # Crossref sorts the returned papers by a relevance score if a query is used in the API call.
        # The scoring is not consistent across queries, so I followed the advice of a crossref dev
        # and normalize by query length for now: https://community.crossref.org/t/query-affiliation/2009/4
        relevance_score = pub_data.get("score", 0) / len(citation.split())
        if relevance_score < relevance_threshold:
            return None
        if author_name:
            author_match_flag = False
            authors = pub_data.get("author")
            # check to see if author_name arg is in author list, with some lenience on non-exact matches
            if authors:
                for author in authors[
                    :200
                ]:  # Only check first 200 authors in case of very long author list
                    given_name = author.get("given", "")
                    family_name = author.get("family", "")
                    author_match_score = SequenceMatcher(
                        None, given_name + " " + family_name, author_name
                    ).ratio()
                    if author_match_score > author_sim_threshold:
                        author_match_flag = True
            if not author_match_flag:
                return None
        return pub_data_to_publication_instance(pub_data)
    return None


def pub_data_to_publication_instance(pub_data: dict, doi: str = None):
    """
    Take in pub_data dict returned from crossref, and return a publication dataclass instance.

    Args:
        pub_data (dict): Dict of publication data returned from crossref.
        doi (str): Optional doi to add to publication instance. TODO: Check if this can be obtained from crossref.
    """
    # Strip title and abstract of possible html tags
    title = pub_data.get("title", [None])[0]
    if title:
        title = html.unescape(title)
        title = BeautifulSoup(norm_ws(title), "html.parser").get_text()

    abstract = pub_data.get("abstract")
    if abstract:
        abstract = html.unescape(abstract)
        abstract = BeautifulSoup(norm_ws(abstract), "html.parser").get_text()
        abstract = re.sub(r"\s+", " ", abstract)

    # Create publication instance
    publication = Publication(
        doi=doi,
        title=title,
        abstract=abstract,
        year=pub_data.get("created", {}).get("date-parts", [[None]])[0][0],
        citation_count=pub_data.get("is-referenced-by-count"),
        publisher=pub_data.get("publisher"),
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


def crossref_from_doi(doi: str) -> dict:
    """
    Query Crossref's REST API for JSON metadata given a DOI.

    Args:
        doi (str): The DOI to query crossref with.

    Returns:
        a dict with JSON metadata or empty dict if request fails.
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
    Returns only the top match for the given query.
    NOTE: If the citation has a DOI, crossref_from_doi will be
    more reliable.

    Args:
        citation (str): The citation to query crossref with.

    Returns:
        a dict with JSON metadata or empty dict if request fails.
    """
    query = citation[:2000]  # Safety against query length limits
    url = f"https://api.crossref.org/works"
    headers = get_headers("h1")
    try:
        response = requests.get(
            url,
            headers=headers,
            params={"query.bibliographic": query, "rows": 1},
            timeout=10,
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
    from scraping.utils.conversion import dataclass_instances_to_csv

    inst = citation_to_publication_instance(citation3)
    dataclass_instances_to_csv(
        [inst],
        os.path.join("scraping", "umo", "scrape_storage", "pub_test.csv"),
        overwrite=True,
    )
