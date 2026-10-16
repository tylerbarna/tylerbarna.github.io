#!/usr/bin/env python3
"""
Sync publications from ORCID to _bibliography/papers.bib.
Queries public ORCID API for works, retrieves DOIs, fetches BibTeX,
and updates _bibliography/papers.bib while preserving existing manual annotations.
"""

import sys
import os
import re
import urllib.request
import json

DEFAULT_ORCID = "0000-0002-4843-345X"
DEFAULT_OUTPUT = "_bibliography/papers.bib"

def fetch_orcid_works(orcid_id):
    url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "al-folio-orcid-sync/1.0"
        }
    )
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data.get("group", [])

def fetch_bibtex_by_doi(doi):
    url = f"https://doi.org/{doi}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/x-bibtex; charset=utf-8",
            "User-Agent": "al-folio-orcid-sync/1.0"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8").strip()
    except Exception as e:
        print(f"Warning: could not fetch BibTeX for DOI {doi}: {e}", file=sys.stderr)
        return None

def main():
    orcid_id = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ORCID
    output_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUTPUT

    print(f"Fetching publications for ORCID: {orcid_id}...")
    try:
        groups = fetch_orcid_works(orcid_id)
    except Exception as e:
        print(f"Error connecting to ORCID: {e}", file=sys.stderr)
        sys.exit(0)  # Don't fail the build if ORCID is temporarily unreachable

    dois = []
    for g in groups:
        summaries = g.get("work-summary", [])
        for s in summaries:
            ext_ids = s.get("external-ids", {}).get("external-id", [])
            for ext in ext_ids:
                if ext.get("external-id-type", "").lower() == "doi":
                    val = ext.get("external-id-value")
                    if val and val not in dois:
                        dois.append(val)

    print(f"Found {len(dois)} works with DOIs on ORCID.")

    existing_content = ""
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            existing_content = f.read()

    new_entries = []
    for doi in dois:
        # Check if DOI already in existing_content
        doi_clean = doi.strip().lower()
        if doi_clean in existing_content.lower():
            print(f"DOI already present: {doi}")
            continue

        print(f"Fetching BibTeX for new DOI: {doi}...")
        bib = fetch_bibtex_by_doi(doi)
        if bib:
            new_entries.append(bib)

    if new_entries:
        print(f"Adding {len(new_entries)} new entries to {output_path}")
        with open(output_path, "a", encoding="utf-8") as f:
            f.write("\n\n" + "\n\n".join(new_entries) + "\n")
    else:
        print("No new publications to add. File is up to date.")

if __name__ == "__main__":
    main()
