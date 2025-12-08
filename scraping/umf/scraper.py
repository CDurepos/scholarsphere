"""
Author:Clayton Durepos
"""

#!/usr/bin/env python3
"""
UMF Faculty Scraper (enhanced with ORCID lookup)
- Crawls the UMF Directory (faculty filter) and visits each profile page to extract:
  first/last name, title, department, email, phone, biography, and external scholarly links.
- Optionally cross-checks the UMF Catalog faculty listings for backfill (names + roles).
- Attempts to enrich ORCID IDs via the public ORCID search API using name + affiliation.
- Outputs: CSV files for Faculty and Institution records.

Run:
  python scraper.py
"""

from __future__ import annotations

import os
import re
import time
import unicodedata
from typing import Optional, Iterable, List, Dict, Tuple

# Institution name must match exactly what's in data/institutions.json
INSTITUTION_NAME = "University of Maine at Farmington"
from datetime import date

import certifi
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from scraping.schemas import Faculty
from scraping.utils import get_headers
from scraping.utils.json_output import write_faculty_jsonl

UMF_DIR_URL = "https://farmington.edu/about/directory/?user_type=faculty"
UMF_DIR_BASE = "https://farmington.edu"

UMF_NAME = "University of Maine at Farmington"

REQ_TIMEOUT = 30
PAUSE = 0.5  # polite delay between requests
MAX_RETRIES = 3

# ORCID enrichment settings
ORCID_SEARCH_URL = "https://pub.orcid.org/v3.0/expanded-search"


def build_session() -> requests.Session:
    sess = requests.Session()
    sess.headers.update(get_headers("h1"))
    sess.verify = False

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


# Utilities
def norm_ws(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("\u00a0", " ")
    s = re.sub(r"[ \t\r\f\v]+", " ", s).strip()
    return s or None


def get_soup(url: str) -> BeautifulSoup:
    resp = SESSION.get(
        url,
        timeout=REQ_TIMEOUT,
        verify=(False),
    )
    resp.raise_for_status()
    time.sleep(PAUSE)
    return BeautifulSoup(resp.text, "html.parser")


def extract_text_or_none(el) -> Optional[str]:
    if not el:
        return None
    return norm_ws(el.get_text(" "))


def pick_first(haystack: Iterable[Optional[str]]) -> Optional[str]:
    for x in haystack:
        x = norm_ws(x)
        if x:
            return x
    return None


# Name Parsing Logic
_PREFIX_RE = re.compile(
    r"^(dr|prof|professor)\.?\s+",
    flags=re.I,
)

_CREDENTIAL_RE = re.compile(
    r",?\s*(Ph\.?D\.?|Ed\.?D\.?|D\.?Ed\.?|M\.?D\.?|D\.?O\.?|MFA|M\.?F\.?A\.?|MBA|M\.?B\.?A\.?|"
    r"MS|M\.?S\.?|MA|M\.?A\.?|MEd|M\.?Ed\.?|JD|J\.?D\.?|Esq\.?|RN|FNP|PNP|DNP|CFA|CFP|CPA)\b\.?",
    flags=re.I,
)

_SUFFIX_RE = re.compile(
    r",?\s*(Jr\.?|Sr\.?|II|III|IV|V)$",
    flags=re.I,
)


def split_name(full: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Robust-ish name splitter:
    - Strips prefixes like Dr., Prof.
    - Strips common degree credentials.
    - Keeps Jr./Sr./II/etc as part of last name.
    """
    full = norm_ws(full) or ""
    if not full:
        return None, None

    full = _PREFIX_RE.sub("", full)
    full = _CREDENTIAL_RE.sub("", full)
    suffix = None
    m = _SUFFIX_RE.search(full)
    if m:
        suffix = m.group(1)
        full = full[: m.start()].strip()

    parts = full.split()
    if not parts:
        return None, None
    if len(parts) == 1:
        return parts[0], suffix

    first = " ".join(parts[:-1])
    last = parts[-1]
    if suffix:
        last = f"{last} {suffix}"
    return first or None, last or None


# Email Utilities
_EMAIL_FIXES = [
    (r"\s*\[at\]\s*", "@"),
    (r"\s*\(at\)\s*", "@"),
    (r"\s+at\s+", "@"),
    (r"\s*\[dot\]\s*", "."),
    (r"\s*\(dot\)\s*", "."),
]


def clean_email(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    s = norm_ws(s)
    for pat, repl in _EMAIL_FIXES:
        s = re.sub(pat, repl, s, flags=re.I)
    m = re.search(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", s or "", flags=re.I)
    return m.group(0).lower() if m else None


def is_boilerplate_text(text: str) -> bool:
    """
    Check if text appears to be website boilerplate rather than actual biography content.
    Returns True if the text looks like cookie notices, footer text, etc.
    """
    if not text:
        return True
    
    text_lower = text.lower()
    
    # Strong indicators of boilerplate - if any of these are present, it's likely not a bio
    boilerplate_phrases = [
        "cookie",
        "we use cookies",
        "cookie information is stored",
        "best user experience",
        "privacy policy",
        "terms of service",
        "gdpr",
        "consent",
        "third party",
        "analytics",
        "strictly necessary",
        "browser and performs functions",
        "recognising you when you return",
        "help us understand",
        "improve your experience",
        "accept our use",
        "cookie settings",
    ]
    
    for phrase in boilerplate_phrases:
        if phrase in text_lower:
            return True
    
    return False


def clean_biography(bio: Optional[str]) -> Optional[str]:
    """
    Clean biography text by filtering out unwanted content like cookie notices,
    website boilerplate, and other non-biography content.
    """
    if not bio:
        return None
    
    bio = norm_ws(bio)
    if not bio:
        return None
    
    # Check for boilerplate text first
    if is_boilerplate_text(bio):
        return None
    
    # Additional checks: if bio is too short, return None
    bio_words = bio.split()
    if len(bio_words) < 10:  # Too short to be a real biography
        return None
    
    # Final normalization
    bio = norm_ws(bio)
    return bio if bio and len(bio.strip()) > 20 else None


def make_faculty_id(url: str, email: Optional[str], full_name: Optional[str]) -> str:
    if url:
        slug = url.rstrip("/").split("/")[-1]
        if slug and len(slug) < 128:
            return slug
    if email:
        return email.split("@")[0]
    if full_name:
        base = re.sub(r"[^a-z0-9]+", "-", full_name.lower())
        base = re.sub(r"-+", "-", base).strip("-")
        if base:
            return base
    # last resort pseudo-random
    return re.sub(r"[^a-z0-9]+", "-", str(time.time()))


# Directory Index Scraper
def scrape_directory_index(start_url: str = UMF_DIR_URL) -> List[str]:
    """
    Collect profile links from the UMF faculty directory (handles pagination if present).
    Only keeps URLs that look like individual profile pages.
    """
    links: set[str] = set()
    to_visit = [start_url]
    seen_pages: set[str] = set()

    while to_visit:
        url = to_visit.pop(0)
        if url in seen_pages:
            continue
        seen_pages.add(url)

        soup = get_soup(url)

        # Person links: /about/directory/<slug>/
        for a in soup.select('a[href*="/about/directory/"]'):
            href = (a.get("href") or "").strip()
            if not href:
                continue
            if href.startswith("/"):
                href = UMF_DIR_BASE + href
            if not href.startswith(UMF_DIR_BASE):
                continue

            path = href.replace(UMF_DIR_BASE, "")
            if "/about/directory/" in path:
                path_no_q = path.split("?", 1)[0]
                # Must have a slug after /about/directory/
                if re.search(r"/about/directory/[^/?#]+/?$", path_no_q):
                    links.add(href)

        # Pagination: look for rel=next or typical next links
        next_link = soup.select_one('a[rel="next"], a.next, a.pagination__next')
        if next_link:
            nhref = (next_link.get("href") or "").strip()
            if nhref:
                if nhref.startswith("/"):
                    nhref = UMF_DIR_BASE + nhref
                if nhref.startswith(UMF_DIR_BASE) and nhref not in seen_pages:
                    to_visit.append(nhref)

    return sorted(links)


# Title & Department Parsing Enhancements
TITLE_KEYWORDS = [
    "Professor",
    "Associate Professor",
    "Assistant Professor",
    "Adjunct Professor",
    "Lecturer",
    "Senior Lecturer",
    "Instructor",
    "Emeritus",
    "Co-Director",
    "Director",
    "Coordinator",
    "Chair",
    "Co-Chair",
    "Dean",
]

TITLE_KEYWORDS_RE = re.compile(
    r"(?i)\b("
    + "|".join(
        sorted(
            {k.replace(" ", r"\s+") for k in TITLE_KEYWORDS},
            key=len,
            reverse=True,
        )
    )
    + r")\b"
)


def refine_title_and_department(
    raw_title: Optional[str],
    hero_dept: Optional[str],
) -> Tuple[Optional[str], Optional[str]]:
    """
    Attempt to:
    - Extract a clean academic/administrative title.
    - Infer department if baked into the title string
      (e.g., "Associate Professor of Mathematics").
    """
    title = norm_ws(raw_title)
    department = norm_ws(hero_dept)

    if not title and not department:
        return None, None
    if not title and department:
        return None, department

    clean_title = title

    # If multiple roles separated by |, /, or -
    for sep in [" | ", " / ", " - "]:
        if sep in clean_title:
            parts = [p.strip() for p in clean_title.split(sep) if p.strip()]
            prof_like = [
                p
                for p in parts
                if re.search(
                    r"(?i)professor|lecturer|instructor|director|dean|chair|coordinator",
                    p,
                )
            ]
            clean_title = prof_like[0] if prof_like else parts[0]
            break

    # Trim anything before the first title keyword
    m = TITLE_KEYWORDS_RE.search(clean_title or "")
    if m:
        clean_title = clean_title[m.start() :].strip()

    # If title like "Associate Professor of Biology" or
    # "Associate Professor, Biology"
    derived_dept = None
    if clean_title:
        m_of = re.search(r"(?i)\b(of|for|in)\b\s+(.+)$", clean_title)
        if m_of:
            derived_dept = norm_ws(m_of.group(2))
            clean_title = norm_ws(clean_title[: m_of.start()].rstrip(","))
        else:
            # If trailing text not containing rank words, treat as dept
            rank_match = TITLE_KEYWORDS_RE.search(clean_title)
            if rank_match:
                trailing = norm_ws(clean_title[rank_match.end() :])
                if trailing and not re.search(
                    r"(?i)professor|lecturer|instructor|director|dean|chair|coordinator",
                    trailing,
                ):
                    derived_dept = trailing.strip(" ,-/")
                    clean_title = norm_ws(clean_title[: rank_match.end()])

    if not department and derived_dept:
        department = derived_dept

    return clean_title or None, department or None


# ==========================
# Scholarly Links Extraction
# ==========================
def extract_scholarly_links(
    soup: BeautifulSoup,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Look for ORCID, Google Scholar, and ResearchGate URLs in links/text.
    Only uses explicit links on the page (no remote search).
    """
    orcid_url = None
    gscholar_url = None
    rgate_url = None

    # Scan anchors
    for a in soup.select("a[href]"):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        lower = href.lower()
        if "orcid.org" in lower:
            orcid_url = href
        elif "scholar.google." in lower or "scholar.google.com" in lower:
            gscholar_url = href
        elif "researchgate.net" in lower:
            rgate_url = href

    # ORCID IDs can also appear as bare text (0000-0002-1825-0097)
    if not orcid_url:
        text = soup.get_text(" ")
        m = re.search(
            r"\b(https?://orcid\.org/)?(\d{4}-\d{4}-\d{4}-\d{3}[\dX])\b",
            text,
            flags=re.I,
        )
        if m:
            if m.group(1):
                orcid_url = m.group(0)
            else:
                orcid_url = "https://orcid.org/" + m.group(2)

    return orcid_url, gscholar_url, rgate_url


# ORCID Lookup by Name
def lookup_orcid_by_name(
    first: str,
    last: str,
    affiliation: Optional[str] = None,
) -> Optional[str]:
    """
    Best-effort ORCID lookup using the public ORCID expanded-search API.
    Uses first + last name + affiliation to reduce collisions.
    Returns a full ORCID URL or None if no confident match.
    """
    first = norm_ws(first) or ""
    last = norm_ws(last) or ""
    if not first or not last:
        return None

    if not affiliation:
        affiliation = UMF_NAME

    # Build search query with fielded search terms
    first_q = first.replace('"', "")
    last_q = last.replace('"', "")
    aff_q = (affiliation or "").replace('"', "")

    query_parts = [
        f'given-names:"{first_q}"',
        f'family-name:"{last_q}"',
    ]
    if aff_q:
        query_parts.append(f'affiliation-org-name:"{aff_q}"')
    q = " AND ".join(query_parts)

    try:
        resp = SESSION.get(
            ORCID_SEARCH_URL,
            params={"q": q, "rows": 5},
            headers={"Accept": "application/json"},
            timeout=REQ_TIMEOUT,
        )

        if resp.status_code != 200:
            return None
        data = resp.json()
    except Exception:
        return None

    # Support both expanded-search and older search shapes
    results = data.get("expanded-result") or data.get("result") or []
    if not isinstance(results, list):
        return None

    first_l = first.lower()
    last_l = last.lower()

    for item in results:
        # Try to extract ORCID iD
        orcid = (
            item.get("orcid-id")
            or item.get("orcid")
            or (
                (item.get("orcid-identifier") or {}).get("path")
                or ((item.get("orcid-identifier") or {}).get("uri") or "").split("/")[-1]
            )
        )
        if not orcid:
            continue

        # Candidate names
        gn = (
            item.get("given-names")
            or item.get("given-name")
            or (
                (item.get("person") or {})
                .get("name", {})
                .get("given-names", {})
                .get("value")
            )
            or ""
        )
        fn = (
            item.get("family-names")
            or item.get("family-name")
            or (
                (item.get("person") or {})
                .get("name", {})
                .get("family-name", {})
                .get("value")
            )
            or ""
        )

        gn = str(gn).strip().lower()
        fn = str(fn).strip().lower()

        # Require exact last name
        if fn != last_l:
            continue

        # Accept if given name is close:
        # - exact match, or
        # - same initial
        if gn and (gn == first_l or gn[0:1] == first_l[0:1]):
            return f"https://orcid.org/{orcid.strip()}"

    return None


# Individual Profile Page
def scrape_profile_page(url: str) -> Faculty:
    soup = get_soup(url)

    # Name
    full_name = pick_first(
        [
            extract_text_or_none(soup.select_one("h1._farUsersHero__text__name")),
            extract_text_or_none(soup.select_one("section._farUsersHero h1")),
            extract_text_or_none(soup.select_one("h1")),
            extract_text_or_none(soup.select_one(".entry-title")),
        ]
    )
    first, last = split_name(full_name or "")

    # Department & Title from hero
    hero_dept = extract_text_or_none(
        soup.select_one("._farUsersHero__text__officeDepartment span")
    )
    raw_title = extract_text_or_none(
        soup.select_one("._farUsersHero__text__title")
    )
    title, department = refine_title_and_department(raw_title, hero_dept)

    # Contact info blocks
    hero_contact_lines = [
        extract_text_or_none(el)
        for el in soup.select("._farUsersHero__text__contactInfo")
    ]
    hero_contact_lines = [l for l in hero_contact_lines if l]

    email = None
    phone = None
    for line in hero_contact_lines:
        if not email:
            maybe_email = clean_email(line)
            if maybe_email:
                email = maybe_email
                continue
        if not phone:
            m = re.search(r"(\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4})", line)
            if m:
                phone = m.group(1)

    # email fallback in page text
    if not email:
        text_all = soup.get_text(" ")
        email = clean_email(text_all)

    # Biography block - only use specific biography section, don't fall back to page content
    bio = None
    bio_block = soup.select_one("section._farUsersBiography ._farUsersBiography__text")
    
    if bio_block:
        # Only extract paragraphs from the actual biography section
        paras = [extract_text_or_none(p) for p in bio_block.select("p")]
        paras = [p for p in paras if p and len(p.split()) > 6 and not is_boilerplate_text(p)]
        if paras:
            bio = "\n\n".join(paras[:6]).strip()
            bio = clean_biography(bio)
    
    # If no dedicated biography section, check for a bio in a content area but be strict
    if not bio:
        # Try entry-content but be very careful to filter out boilerplate
        content_block = soup.select_one(".entry-content")
        if content_block:
            paras = [extract_text_or_none(p) for p in content_block.select("p")]
            # Filter more aggressively for fallback content
            paras = [p for p in paras if p and len(p.split()) > 10 and not is_boilerplate_text(p)]
            if paras:
                bio = "\n\n".join(paras[:6]).strip()
                bio = clean_biography(bio)

    # Scholarly links from page content
    orcid_url, gscholar_url, rgate_url = extract_scholarly_links(soup)

    # ORCID enrichment via public search (name + affiliation)
    if not orcid_url and first and last:
        orcid_url = lookup_orcid_by_name(first, last, UMF_NAME)

    # Phone fallback (whole page)
    if not phone:
        text_all = soup.get_text(" ")
        m = re.search(r"(\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4})", text_all)
        if m:
            phone = m.group(1)

    email = clean_email(email)

    fac = Faculty(
        faculty_id=make_faculty_id(url, email, full_name),
        first_name=first,
        last_name=last,
        title=title,
        department=department,
        email=email,
        phone_num=phone,
        biography=bio,
        research_interest=None,
        orcid=orcid_url,
        google_scholar_url=gscholar_url,
        research_gate_url=rgate_url,
        scraped_from=url,
    )
    return fac

def scrape_umf() -> List[Dict]:
    """
    Scrape UMF faculty data and return faculty records.
    
    Returns:
        List of faculty dictionaries with all attributes including MV attributes as arrays.
        Each record includes institution_name which references data/institutions.json.
    """

    print("[INFO] Fetching faculty directory index…")
    profile_links = scrape_directory_index(UMF_DIR_URL)
    print(f"[INFO] Found {len(profile_links)} profile links")

    # List of faculty records with MV attributes as arrays
    faculty_records = []

    for i, url in enumerate(profile_links, start=1):
        try:
            f = scrape_profile_page(url)
            
            # Collect emails as array
            emails = []
            if f.email:
                if isinstance(f.email, list):
                    emails = [e for e in f.email if e]
                else:
                    if f.email:
                        emails = [f.email]
            
            # Collect phones as array
            phones = []
            if f.phone_num:
                if isinstance(f.phone_num, list):
                    phones = [p for p in f.phone_num if p]
                else:
                    if f.phone_num:
                        phones = [f.phone_num]
            
            # Collect departments as array
            departments = []
            if f.department:
                if isinstance(f.department, list):
                    departments = [d for d in f.department if d]
                else:
                    if f.department:
                        departments = [f.department]
            
            # Collect titles as array
            titles = []
            if f.title:
                if isinstance(f.title, list):
                    titles = [t for t in f.title if t]
                else:
                    if f.title:
                        titles = [f.title]
            
            # Create faculty record with MV attributes as arrays
            faculty_record = {
                'first_name': f.first_name,
                'last_name': f.last_name,
                'biography': f.biography,
                'orcid': f.orcid,
                'google_scholar_url': f.google_scholar_url,
                'research_gate_url': f.research_gate_url,
                'scraped_from': f.scraped_from,
                'emails': emails,
                'phones': phones,
                'departments': departments,
                'titles': titles,
                'institution_name': INSTITUTION_NAME,
                'start_date': date.today().isoformat(),
                'end_date': None,
            }
            
            faculty_records.append(faculty_record)
            
            print(
                f"[OK] {f.first_name or '?'} {f.last_name or '?'} "
                f"| {f.title or ''} | {url}"
            )
        except Exception as e:
            print(f"[WARN] Failed profile {url}: {e}")

    try:
        print("[INFO] Backfilling names/roles from catalog…")
        before = len(faculty_records)
        after = len(faculty_records)
        print(f"[INFO] Catalog backfill added {after - before} records")
    except Exception as e:
        print(f"[WARN] Catalog backfill failed: {e}")
    
    return faculty_records


def main(output_dir: str = "scraping/out"):
    """
    Main function to scrape UMF data and output JSON files.
    
    Args:
        output_dir: Directory to write output files (default: scraping/out)
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    faculty_records = scrape_umf()
    print(f"[INFO] Scraped {len(faculty_records)} faculty records")
    
    # Write faculty JSONL file
    faculty_output = os.path.join(output_dir, "umf_faculty.jsonl")
    write_faculty_jsonl(faculty_records, faculty_output)
    print(f"[INFO] Wrote: {faculty_output}")
    
    return faculty_output


if __name__ == "__main__":
    main()