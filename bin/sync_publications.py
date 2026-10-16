#!/usr/bin/env python3
"""
Multi-source automated publication synchronizer for Tyler Barna.
Integrates:
  1. NASA ADS / SciX API (if ADS_DEV_KEY is present in env or secrets)
  2. Public ORCID API (0000-0002-4843-345X, no token needed)
  3. Public arXiv API (author: Barna, Tyler, no token needed)
  4. CrossRef Content Negotiation for clean BibTeX generation

Automatically enriches each entry with modern al-folio attributes:
  - abbr={VENUE}
  - bibtex_show={true}
  - altmetric={true}
  - dimensions={true}
  - arxiv={ARXIV_ID}
  - html={URL}
"""

import os
import sys
import re
import json
import urllib.request
import urllib.error
import ssl
import xml.etree.ElementTree as ET

ORCID_ID = os.environ.get("ORCID_ID", "0000-0002-4843-345X")
ADS_DEV_KEY = os.environ.get("SCIX_API_TOKEN") or os.environ.get("ADS_DEV_KEY", "")
OUTPUT_BIB = os.environ.get("OUTPUT_BIB", "_bibliography/papers.bib")

VENUE_MAP = {
    r"Monthly Notices": "MNRAS",
    r"mnras": "MNRAS",
    r"Publications of the Astronomical Society of the Pacific": "PASP",
    r"pasp": "PASP",
    r"Astrophysical Journal Supplement": "ApJS",
    r"apjs": "ApJS",
    r"Astrophysical Journal Letters": "ApJL",
    r"apjl": "ApJL",
    r"Astrophysical Journal": "ApJ",
    r"apj": "ApJ",
    r"Nature Communications": "Nat. Commun.",
    r"Astronomer's Telegram": "ATel",
    r"VizieR": "VizieR",
    r"arXiv": "arXiv"
}

def create_ssl_context():
    """Create a permissive SSL context for environments with custom or skewed clocks."""
    try:
        return ssl.create_default_context()
    except Exception:
        return ssl._create_unverified_context()

def fetch_orcid_dois(orcid):
    """Fetch all work DOIs from the public ORCID API."""
    url = f"https://pub.orcid.org/v3.0/{orcid}/works"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "TylerBarna-Portfolio-Sync/1.0 (mailto:barna314@umn.edu)"
        }
    )
    dois = []
    try:
        ctx = create_ssl_context()
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for group in data.get("group", []):
                for summary in group.get("work-summary", []):
                    ext_ids = summary.get("external-ids", {}).get("external-id", [])
                    for ext in ext_ids:
                        if ext.get("external-id-type", "").lower() == "doi":
                            val = ext.get("external-id-value")
                            if val and val not in dois:
                                dois.append(val.strip())
    except Exception as e:
        print(f"Notice: ORCID API query returned {e}", file=sys.stderr)
    return dois

def fetch_arxiv_entries(author="Barna_Tyler"):
    """Fetch recent papers by author from arXiv API."""
    url = f"https://export.arxiv.org/api/query?search_query=au:{author}&max_results=30"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "TylerBarna-Portfolio-Sync/1.0"}
    )
    entries = []
    try:
        ctx = create_ssl_context()
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            xml_text = resp.read().decode("utf-8")
            root = ET.fromstring(xml_text)
            ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
            for entry in root.findall("atom:entry", ns):
                title_el = entry.find("atom:title", ns)
                id_el = entry.find("atom:id", ns)
                published_el = entry.find("atom:published", ns)
                doi_el = entry.find("arxiv:doi", ns)

                title = title_el.text.strip().replace("\n", " ") if title_el is not None else ""
                raw_id = id_el.text.strip() if id_el is not None else ""
                arxiv_id = raw_id.split("/abs/")[-1].split("v")[0] if "/abs/" in raw_id else ""
                pub_year = published_el.text[:4] if published_el is not None else "2025"
                doi = doi_el.text.strip() if doi_el is not None else None

                if arxiv_id:
                    entries.append({
                        "arxiv_id": arxiv_id,
                        "title": title,
                        "year": pub_year,
                        "doi": doi
                    })
    except Exception as e:
        print(f"Notice: arXiv API query returned {e}", file=sys.stderr)
    return entries

def fetch_ads_bibtex(ads_token, orcid):
    """Query NASA ADS / SciX API for clean, curated astronomy BibTeX."""
    url = "https://api.adsabs.harvard.edu/v1/search/query"
    query_params = {
        "q": f'orcid:{orcid} OR author:"Barna, Tyler"',
        "fl": "bibcode,title,year,author,doi,identifier",
        "rows": 50
    }
    encoded = urllib.parse.urlencode(query_params)
    req = urllib.request.Request(
        f"{url}?{encoded}",
        headers={"Authorization": f"Bearer {ads_token}"}
    )
    try:
        ctx = create_ssl_context()
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            docs = data.get("response", {}).get("docs", [])
            bibcodes = [d["bibcode"] for d in docs if "bibcode" in d]
            if not bibcodes:
                return []

            # Export BibTeX for these bibcodes
            export_url = "https://api.adsabs.harvard.edu/v1/export/bibtex"
            post_data = json.dumps({"bibcode": bibcodes}).encode("utf-8")
            export_req = urllib.request.Request(
                export_url,
                data=post_data,
                headers={
                    "Authorization": f"Bearer {ads_token}",
                    "Content-Type": "application/json"
                }
            )
            with urllib.request.urlopen(export_req, timeout=20, context=ctx) as exp_resp:
                exp_data = json.loads(exp_resp.read().decode("utf-8"))
                return exp_data.get("export", "").split("\n\n")
    except Exception as e:
        print(f"Notice: NASA ADS / SciX API query returned {e}", file=sys.stderr)
        return []

def fetch_bibtex_by_doi(doi):
    """Fetch standard BibTeX using CrossRef Content Negotiation."""
    url = f"https://api.crossref.org/works/{doi}/transform/application/x-bibtex"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "TylerBarna-Portfolio-Sync/1.0 (mailto:barna314@umn.edu)"}
    )
    try:
        ctx = create_ssl_context()
        with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
            return resp.read().decode("utf-8").strip()
    except Exception:
        # Fallback to doi.org
        doi_url = f"https://doi.org/{doi}"
        doi_req = urllib.request.Request(
            doi_url,
            headers={"Accept": "application/x-bibtex; charset=utf-8", "User-Agent": "Mozilla/5.0"}
        )
        try:
            with urllib.request.urlopen(doi_req, timeout=12, context=ctx) as resp:
                return resp.read().decode("utf-8").strip()
        except Exception:
            return None

def enrich_bibtex_entry(raw_bib, doi=None, arxiv=None):
    """Inject al-folio properties into raw BibTeX string."""
    if not raw_bib or not raw_bib.strip().startswith("@"):
        return raw_bib

    # Determine venue abbreviation
    abbr = "arXiv"
    for pattern, venue in VENUE_MAP.items():
        if re.search(pattern, raw_bib, re.IGNORECASE):
            abbr = venue
            break

    # Extract or infer arXiv
    if not arxiv:
        arxiv_match = re.search(r"10\.48550/arXiv\.([0-9]+\.[0-9]+)", raw_bib)
        if arxiv_match:
            arxiv = arxiv_match.group(1)
        else:
            eprint_match = re.search(r"eprint\s*=\s*\{([0-9]+\.[0-9]+)\}", raw_bib)
            if eprint_match:
                arxiv = eprint_match.group(1)

    # Prepare injected fields
    injections = [
        f"  abbr = {{{abbr}}}",
        "  bibtex_show = {true}",
        "  altmetric = {true}",
        "  dimensions = {true}"
    ]
    if arxiv:
        injections.append(f"  arxiv = {{{arxiv}}}")

    # Insert right before final closing brace
    last_brace_idx = raw_bib.rfind("}")
    if last_brace_idx != -1:
        injected_block = ",\n" + ",\n".join(injections) + "\n}"
        return raw_bib[:last_brace_idx] + injected_block
    return raw_bib

def main():
    print("=== Tyler Barna Publication Synchronizer (NASA ADS/SciX + ORCID + arXiv) ===")
    print(f"Output target: {OUTPUT_BIB}")

    existing_content = ""
    if os.path.exists(OUTPUT_BIB):
        with open(OUTPUT_BIB, "r", encoding="utf-8") as f:
            existing_content = f.read()

    new_entries = []

    # 1. Try NASA ADS / SciX if API key provided
    if ADS_DEV_KEY:
        print("Querying NASA ADS / SciX API with configured ADS_DEV_KEY...")
        ads_entries = fetch_ads_bibtex(ADS_DEV_KEY, ORCID_ID)
        for entry in ads_entries:
            if not entry.strip():
                continue
            # Extract bibkey
            key_m = re.match(r"@\w+\{([^,]+),", entry.strip())
            if key_m and key_m.group(1).lower() in existing_content.lower():
                continue
            new_entries.append(enrich_bibtex_entry(entry))

    # 2. Query ORCID API
    print(f"Querying public ORCID API for {ORCID_ID}...")
    orcid_dois = fetch_orcid_dois(ORCID_ID)
    print(f"Found {len(orcid_dois)} DOIs on ORCID.")

    for doi in orcid_dois:
        doi_clean = doi.strip().lower()
        if doi_clean in existing_content.lower():
            continue

        print(f"Fetching BibTeX for new DOI: {doi}...")
        raw_bib = fetch_bibtex_by_doi(doi)
        if raw_bib:
            enriched = enrich_bibtex_entry(raw_bib, doi=doi)
            new_entries.append(enriched)

    # 3. Query arXiv API
    print("Querying arXiv API for author preprints...")
    arxiv_papers = fetch_arxiv_entries("Barna_Tyler")
    print(f"Found {len(arxiv_papers)} papers on arXiv.")

    for p in arxiv_papers:
        arx = p["arxiv_id"]
        if arx in existing_content:
            continue
        if p.get("doi") and p["doi"].lower() in existing_content.lower():
            continue

        print(f"Creating BibTeX entry for new arXiv preprint: {arx} ({p['title']})...")
        key = f"arXiv_{arx.replace('.', '_')}"
        raw_bib = f"""@ARTICLE{{{key},
  author = {{Barna, Tyler and others}},
  title = {{{{{p['title']}}}}},
  journal = {{arXiv e-prints}},
  year = {{{p['year']}}},
  archivePrefix = {{arXiv}},
  eprint = {{{arx}}},
  arxiv = {{{arx}}},
  abbr = {{arXiv}},
  bibtex_show = {{true}},
  altmetric = {{true}},
  dimensions = {{true}},
  html = {{https://arxiv.org/abs/{arx}}}
}}"""
        new_entries.append(raw_bib)

    if new_entries:
        print(f"Adding {len(new_entries)} new publications to {OUTPUT_BIB}...")
        with open(OUTPUT_BIB, "w", encoding="utf-8") as f:
            f.write("\n\n".join(new_entries) + "\n\n" + existing_content)
        print("Success! Publications updated.")
    else:
        print("All publications are already up to date!")

if __name__ == "__main__":
    main()
