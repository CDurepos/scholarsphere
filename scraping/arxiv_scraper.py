#!/usr/bin/env python3
"""
arxiv_ar5iv_scraper.py

Fetches publication metadata from the official arXiv API
and normalizes into your Publication schema:

    publication_id = arXiv ID
    doi
    title
    abstract
    year
    citation_count = (not populated here; left as None)
    publisher = "arXiv"

Ar5iv HTML URL can be derived in your app as:
    f"https://ar5iv.labs.arxiv.org/html/{publication_id}"
"""

from __future__ import annotations

import csv
import json
import os
import re
import time
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
from typing import Iterable, List, Optional, Dict

import certifi
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from schemas import Publication
from utils import get_headers

# ----------------
# Config
# ----------------
ARXIV_API_URL = "http://export.arxiv.org/api/query"
REQ_TIMEOUT = 30
PAUSE = 0.5
MAX_RETRIES = 3

INSECURE = os.getenv("ARXIV_SCRAPER_INSECURE", "0") == "1"

def build_session() -> requests.Session:
    sess = requests.Session()
    sess.headers.update(get_headers("h1"))
    sess.verify = False if INSECURE else certifi.where()

    retry = Retry(
        total=MAX_RETRIES,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    sess.mount("https://", adapter)
    sess.mount("http://", adapter)
    return sess


SESSION = build_session()


# ----------------
# Helpers
# ----------------
def norm_ws(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("\xa0", " ")
    s = re.sub(r"[ \t\r\f\v]+", " ", s).strip()
    return s or None


def write_jsonl(rs: Iterable[dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in rs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_csv(rs: Iterable[dict], path: str) -> None:
    rs = list(rs)
    if not rs:
        return
    keys = sorted({k for r in rs for k in r.keys()})
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rs:
            w.writerow(r)


# --------------------------
# arXiv API core
# --------------------------
def fetch_arxiv_feed(params: Dict[str, str]) -> str:
    resp = SESSION.get(
        ARXIV_API_URL,
        params=params,
        timeout=REQ_TIMEOUT,
        verify=(False if INSECURE else certifi.where()),
    )
    resp.raise_for_status()
    time.sleep(PAUSE)
    return resp.text


def parse_arxiv_entry(entry: ET.Element) -> Publication:
    """
    Convert a single <entry> from arXiv Atom -> Publication.
    """
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }

    def gettext(path: str) -> Optional[str]:
        el = entry.find(path, ns)
        return norm_ws(el.text) if el is not None and el.text else None

    # arXiv ID (from <id>)
    id_full = gettext("atom:id")  # e.g. http://arxiv.org/abs/1706.03762v5
    arxiv_id = None
    if id_full:
        m = re.search(r"arxiv\.org/(?:abs|pdf)/([^/]+)", id_full)
        if m:
            arxiv_id = m.group(1)

    title = gettext("atom:title")
    abstract = gettext("atom:summary")

    # Published year
    published = gettext("atom:published") or gettext("atom:updated")
    year = None
    if published and len(published) >= 4 and published[:4].isdigit():
        year = published[:4]

    # DOI
    doi = gettext("arxiv:doi")

    # We’re not resolving citation counts here; leave as None for now.
    citation_count = None

    publisher = "arXiv" if arxiv_id else None

    return Publication(
        publication_id=arxiv_id,
        doi=doi,
        title=title,
        abstract=abstract,
        year=year,
        citation_count=citation_count,
        publisher=publisher,
    )


def fetch_publications_by_query(
    search_query: str,
    max_results: int = 100,
    batch_size: int = 50,
) -> List[Publication]:
    """
    Fetch publications matching an arXiv search query.
    Example search_query:
      - 'au:"Lastname, Firstname"'
      - 'au:"Bailey, Allen" AND cat:math*'
    """
    pubs: List[Publication] = []
    start = 0

    while start < max_results:
        to_get = min(batch_size, max_results - start)
        params = {
            "search_query": search_query,
            "start": str(start),
            "max_results": str(to_get),
        }
        xml_text = fetch_arxiv_feed(params)
        root = ET.fromstring(xml_text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)

        if not entries:
            break

        for entry in entries:
            pubs.append(parse_arxiv_entry(entry))

        start += len(entries)
        if len(entries) < to_get:
            break

    return pubs


def fetch_publications_by_ids(arxiv_ids: List[str]) -> List[Publication]:
    """
    Fetch publications for a list of arXiv IDs using id_list=...
    """
    pubs: List[Publication] = []
    if not arxiv_ids:
        return pubs

    batch_size = 50
    for i in range(0, len(arxiv_ids), batch_size):
        batch = arxiv_ids[i : i + batch_size]
        params = {"id_list": ",".join(batch)}
        xml_text = fetch_arxiv_feed(params)
        root = ET.fromstring(xml_text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        for entry in root.findall("atom:entry", ns):
            pubs.append(parse_arxiv_entry(entry))

    return pubs


# ----------------
# Example wiring
# ----------------
def main():
    # Example: You’ll likely generate queries per faculty.
    # For testing, plug any arXiv query:
    #   search_query = 'au:"Goodfellow, Ian"'
    #   search_query = 'all:"machine learning"'
    search_query = 'all:"quantum information"'  # placeholder
    pubs = fetch_publications_by_query(search_query, max_results=50)

    print(f"[INFO] Retrieved {len(pubs)} publications")

    write_jsonl([asdict(p) for p in pubs], "publications_arxiv.jsonl")
    write_csv([asdict(p) for p in pubs], "publications_arxiv.csv")
    print("[INFO] Wrote publications_arxiv.jsonl and publications_arxiv.csv")


if __name__ == "__main__":
    main()
