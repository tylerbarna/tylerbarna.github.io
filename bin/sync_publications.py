#!/usr/bin/env python3
"""Keep _bibliography/papers.bib and _data/metrics.yml in sync with NASA ADS.

Design
------
* NASA ADS (SciX) is the single source of record. ADS already merges an arXiv
  preprint with its published version, so every work appears exactly once and
  with its full author list and abstract.
* Existing entries are *upserted*, never blindly prepended: a work is matched by
  DOI, arXiv ID, ADS bibcode or normalised title, and the duplicates that the old
  multi-source sync produced are folded together.
* Hand-curated fields (``selected``, ``code``, ``slides``, ``preview`` ...) are
  carried over from the existing entry, so curation survives every sync.
* Entries tagged ``source = {manual}`` (e.g. work ADS will never index) are left
  exactly as written.
* ORCID and arXiv are only consulted to *report* works ADS has not indexed yet.
  The script never invents an entry or an author list.

Usage
-----
  python bin/sync_publications.py             # fetch from ADS, merge, write
  python bin/sync_publications.py --offline   # normalise / de-duplicate only
  python bin/sync_publications.py --check     # exit 1 if the file needs fixing

Environment: ``ADS_API_TOKEN`` (or the legacy ``SCIX_API_TOKEN`` /
``ADS_DEV_KEY``), ``ORCID_ID``.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BIB_PATH = ROOT / "_bibliography" / "papers.bib"
METRICS_PATH = ROOT / "_data" / "metrics.yml"

ORCID_ID = os.environ.get("ORCID_ID", "0000-0002-4843-345X")
ADS_TOKEN = (
    os.environ.get("ADS_API_TOKEN")
    or os.environ.get("SCIX_API_TOKEN")
    or os.environ.get("ADS_DEV_KEY")
    or ""
)
OWNER_LAST_NAME = "Barna"
ADS_QUERY = f'orcid:{ORCID_ID} OR (author:"Barna, Tyler" AND year:2016-2035)'
ADS_HOSTS = ("https://api.adsabs.harvard.edu/v1", "https://scixplorer.org/v1")
USER_AGENT = "tylerbarna.com publication sync (+https://github.com/tylerbarna/tylerbarna.github.io)"

# Fields a human adds by hand. They are never supplied by ADS and are carried
# over from the existing entry on every sync.
CURATED_FIELDS = (
    "selected", "preview", "code", "slides", "poster", "video", "website", "blog",
    "pdf", "supp", "award", "award_name", "additional_info", "annotation",
    "google_scholar_id", "inspirehep_id", "hidden", "pubtype_override", "html",
)
# Fields this script derives; recomputed on every run.
DERIVED_FIELDS = ("abbr", "pubtype", "bibtex_show", "altmetric", "dimensions", "arxiv")
# Order used when writing entries, so diffs stay small and readable.
FIELD_ORDER = (
    "author", "title", "journal", "booktitle", "series", "year", "month", "volume",
    "number", "pages", "eid", "doi", "archiveprefix", "eprint", "primaryclass",
    "keywords", "abstract", "adsurl", "adsnote", "abbr", "pubtype", "bibtex_show",
    "selected", "altmetric", "dimensions", "arxiv", "html",
)
DISPLAY_NAMES = {"archiveprefix": "archivePrefix", "primaryclass": "primaryClass"}

# ADS journal macros -> full names (longest first so \apjs wins over \apj).
JOURNAL_MACROS = {
    "apjs": "The Astrophysical Journal Supplement Series",
    "apjl": "The Astrophysical Journal Letters",
    "apj": "The Astrophysical Journal",
    "aj": "The Astronomical Journal",
    "mnras": "Monthly Notices of the Royal Astronomical Society",
    "pasp": "Publications of the Astronomical Society of the Pacific",
    "aap": "Astronomy and Astrophysics",
    "natas": "Nature Astronomy",
    "nat": "Nature",
    "prd": "Physical Review D",
    "araa": "Annual Review of Astronomy and Astrophysics",
    "jcap": "Journal of Cosmology and Astroparticle Physics",
}
# Venue abbreviations, checked in order against the journal / booktitle.
VENUES = (
    (r"astrophysical journal letters", "ApJL"),
    (r"astrophysical journal supplement", "ApJS"),
    (r"astrophysical journal", "ApJ"),
    (r"astronomical journal", "AJ"),
    (r"monthly notices", "MNRAS"),
    (r"publications of the astronomical society of the pacific", "PASP"),
    (r"nature communications", "Nat. Commun."),
    (r"nature astronomy", "Nat. Astron."),
    (r"astronomy and astrophysics|astronomy & astrophysics", "A&A"),
    (r"physical review d", "PRD"),
    (r"high energy astrophysics division", "HEAD"),
    (r"american astronomical society", "AAS"),
    (r"transient name server", "TNS"),
    (r"astronomer'?s telegram", "ATel"),
    (r"gcn circular", "GCN"),
    (r"source code library", "ASCL"),
    (r"vizier", "VizieR"),
    (r"arxiv", "arXiv"),
)
BIBCODE_RE = re.compile(r"^\d{4}[A-Za-z&.]{5}[\w.]{4}[A-Za-z.][\d.]{4}[A-Z]$")
ARXIV_RE = re.compile(r"(\d{4}\.\d{4,5})(?:v\d+)?")


# --------------------------------------------------------------------------- #
# Minimal BibTeX reader / writer (no third-party dependency).
# --------------------------------------------------------------------------- #


@dataclass
class Entry:
    type: str
    key: str
    fields: dict = field(default_factory=dict)  # lower-case name -> raw value (no outer delimiters)
    bare: set = field(default_factory=set)      # names whose value was an unquoted token

    def get(self, name: str, default: str = "") -> str:
        return self.fields.get(name, default)

    def set(self, name: str, value: str, bare: bool = False) -> None:
        self.fields[name] = value
        (self.bare.add if bare else self.bare.discard)(name)

    def drop(self, name: str) -> None:
        self.fields.pop(name, None)
        self.bare.discard(name)


def _read_delimited(text: str, i: int) -> tuple[str, int, bool]:
    """Read a field value starting at text[i]; return (value, next index, is_bare)."""
    if text[i] == "{":
        depth, j = 0, i
        while j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    return text[i + 1 : j], j + 1, False
            j += 1
        raise ValueError("unbalanced braces")
    if text[i] == '"':
        depth, j = 0, i + 1
        while j < len(text):
            c = text[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            elif c == '"' and depth == 0 and text[j - 1] != "\\":
                value = text[i + 1 : j]
                # ADS writes title = "{Title}"; keep the protective braces as-is.
                return value, j + 1, False
            j += 1
        raise ValueError("unterminated quoted value")
    m = re.match(r"[^,}\s]+", text[i:])
    return m.group(0), i + m.end(), True


def parse_bibtex(text: str) -> list[Entry]:
    entries, i = [], 0
    while True:
        at = text.find("@", i)
        if at == -1:
            return entries
        m = re.match(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text[at:])
        if not m:
            i = at + 1
            continue
        entry = Entry(type=m.group(1).lower(), key=m.group(2))
        j = at + m.end()
        while j < len(text):
            while j < len(text) and text[j] in " \t\r\n,":
                j += 1
            if j < len(text) and text[j] == "}":
                j += 1
                break
            fm = re.match(r"([\w\-:.]+)\s*=\s*", text[j:])
            if not fm:  # malformed tail; skip to the closing brace
                j = text.find("}", j) + 1
                break
            name = fm.group(1).lower()
            j += fm.end()
            value, j, bare = _read_delimited(text, j)
            entry.set(name, value.replace("\x07", "\\a"), bare=bare)
        entries.append(entry)
        i = j


def format_entry(e: Entry) -> str:
    names = sorted(
        e.fields,
        key=lambda n: (FIELD_ORDER.index(n) if n in FIELD_ORDER else len(FIELD_ORDER), n),
    )
    width = max(len(DISPLAY_NAMES.get(n, n)) for n in names)
    lines = []
    for n in names:
        v = re.sub(r"\s+", " ", e.fields[n]).strip()
        shown = v if n in e.bare else "{" + v + "}"
        lines.append(f"  {DISPLAY_NAMES.get(n, n).rjust(width)} = {shown}")
    return f"@{e.type.upper() if e.type in ('article', 'inproceedings', 'software') else e.type}{{{e.key},\n" + ",\n".join(lines) + "\n}\n"


# --------------------------------------------------------------------------- #
# Normalisation helpers.
# --------------------------------------------------------------------------- #


def plain(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"\\[a-zA-Z]+\s*", " ", text)
    return re.sub(r"[{}\\~]", "", text)


def norm_title(e: Entry) -> str:
    t = plain(e.get("title")).lower()
    t = re.sub(r"^vizier online data catalog:\s*", "", t)
    t = re.sub(r"\([^()]*\+,\s*\d{4}\)\s*$", "", t)
    return re.sub(r"[^a-z0-9]", "", t)


def doi_of(e: Entry) -> str:
    d = e.get("doi") or ""
    if not d:
        m = re.search(r"doi\.org/(10\.[^\s}]+)", e.get("url") + " " + e.get("html"))
        d = m.group(1) if m else ""
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d.strip()).lower()
    return "" if d.startswith("10.48550/arxiv.") else d


def arxiv_of(e: Entry) -> str:
    # ASCL records also use `eprint` (ascl:YYMM.NNN), so honour archivePrefix.
    eprint = e.get("eprint") if e.get("archiveprefix", "arxiv").lower() == "arxiv" else ""
    for source in (eprint, e.get("arxiv"), e.get("doi"), e.get("eid"), e.get("url"), e.get("html")):
        if not source or ("arxiv" not in source.lower() and source not in (eprint, e.get("arxiv"))):
            continue
        m = ARXIV_RE.search(source)
        if m:
            return m.group(1)
    return ""


def bibcode_of(e: Entry) -> str:
    if BIBCODE_RE.match(e.key):
        return e.key
    m = re.search(r"/abs/([^/\s}]+)", e.get("adsurl"))
    return urllib.parse.unquote(m.group(1)) if m else ""


def identities(e: Entry) -> set[str]:
    ids = set()
    if doi_of(e):
        ids.add("doi:" + doi_of(e))
    if arxiv_of(e):
        ids.add("arxiv:" + arxiv_of(e))
    if bibcode_of(e):
        ids.add("bibcode:" + bibcode_of(e))
    is_abstract = "abstract" in (e.get("booktitle") + e.get("journal")).lower()
    if norm_title(e) and not is_abstract:
        ids.add("title:" + norm_title(e))
    return ids


def expand_journal(e: Entry) -> None:
    for name in ("journal", "booktitle"):
        v = e.get(name)
        if not v:
            continue
        # "\apjs" is an ADS macro; a bare "pjs" is what is left after a Python
        # string turned "\a" into a bell character in an earlier sync.
        m = re.fullmatch(r"\\([a-z]+)|(pjs|pjl|pj)", v.strip())
        if m:
            macro = m.group(1) or "a" + m.group(2)
            if macro in JOURNAL_MACROS:
                e.set(name, JOURNAL_MACROS[macro])
        v = e.get(name).strip()
        if v.startswith("{") and v.endswith("}") and v.count("{") == 1:
            e.set(name, v[1:-1])


def where_of(e: Entry) -> str:
    """Everything that says where a work appeared, as plain lower-case text."""
    return plain(" ".join(e.get(n) for n in ("journal", "booktitle", "howpublished", "publisher"))).lower()


def venue_abbr(e: Entry) -> str:
    where = where_of(e)
    for pattern, abbr in VENUES:
        if re.search(pattern, where):
            return abbr
    return e.get("abbr")


def classify(e: Entry, ads_meta: dict | None = None) -> str:
    if e.get("pubtype_override"):
        return e.get("pubtype_override")
    where = where_of(e)
    if ads_meta:
        doctype = ads_meta.get("doctype", "")
        props = set(ads_meta.get("property", []))
        if "REFEREED" in props and doctype in ("article", "inproceedings", "inbook"):
            return "refereed"
        if doctype == "eprint":
            return "preprint"
        if doctype == "software":
            return "software"
        if doctype == "catalog":
            return "data"
        if doctype in ("circular", "newsletter") or re.search(r"telegram|name server|gcn", where):
            return "report"
        if doctype in ("abstract", "inproceedings"):
            return "abstract"
    if e.type == "software" or "source code library" in where:
        return "software"
    if re.search(r"vizier|\bcds\b", where):
        return "data"
    if re.search(r"meeting abstracts|abstracts|conference|proceedings", where) or e.type == "inproceedings":
        return "abstract"
    if re.search(r"telegram|transient name server|gcn circular", where):
        return "report"
    if "arxiv" in where or (not where.strip() and arxiv_of(e)):
        return "preprint"
    if e.get("journal"):
        return "refereed"
    return "other"


def author_list(e: Entry) -> list[str]:
    return [a.strip() for a in re.split(r"\s+and\s+", e.get("author")) if a.strip()]


def is_fabricated(e: Entry) -> bool:
    """Entries the old arXiv fallback produced: 'Barna, Tyler and others'."""
    authors = author_list(e)
    return len(authors) <= 2 and authors[-1:] == ["others"] and OWNER_LAST_NAME in authors[0]


def quality(e: Entry) -> float:
    score = 0.0
    authors = author_list(e)
    if e.get("adsurl"):
        score += 40
    if "others" not in authors:
        score += 60
    if doi_of(e):
        score += 25
    if classify(e) == "refereed":
        score += 30
    if BIBCODE_RE.match(e.key):
        score += 10
    if is_fabricated(e) or e.key.startswith(("arXiv_", "http")):
        score -= 200
    return score + len(authors) / 1000


def first_author_is_owner(e: Entry) -> bool:
    authors = author_list(e)
    return bool(authors) and OWNER_LAST_NAME.lower() in plain(authors[0]).lower().split(",")[0]


def year_of(e: Entry) -> int:
    m = re.search(r"\d{4}", e.get("year"))
    return int(m.group(0)) if m else 0


MONTHS = {m: i for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split(), 1)}


def sort_key(e: Entry) -> tuple:
    month = MONTHS.get(e.get("month", "")[:3].lower(), 0)
    return (-year_of(e), -month, e.key.lower())


# --------------------------------------------------------------------------- #
# Merge / normalise.
# --------------------------------------------------------------------------- #


def group_duplicates(entries: list[Entry]) -> list[list[Entry]]:
    parent = list(range(len(entries)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    seen: dict[str, int] = {}
    for i, e in enumerate(entries):
        if e.get("source") == "manual":
            continue
        for ident in identities(e):
            if ident in seen:
                parent[find(i)] = find(seen[ident])
            else:
                seen[ident] = i
    groups: dict[int, list[Entry]] = {}
    for i, e in enumerate(entries):
        groups.setdefault(find(i), []).append(e)
    return list(groups.values())


def carry_curated(target: Entry, sources: list[Entry]) -> None:
    for name in CURATED_FIELDS:
        if target.get(name):
            continue
        for s in sources:
            if s.get(name):
                target.set(name, s.get(name), bare=name in s.bare)
                break


def finalise(e: Entry, ads_meta: dict | None = None) -> Entry:
    """Recompute every derived field on a single entry."""
    if e.get("source") == "manual":
        e.set("pubtype", e.get("pubtype") or "other")
        return e
    expand_journal(e)
    for name in ("url", "publisher", "copyright", "issn", "isbn"):
        e.drop(name)
    # ADS's doctype/refereed flags beat the journal-name heuristic, so once an
    # entry has been classified from ADS, offline runs keep that answer.
    prior = e.get("pubtype")
    for name in DERIVED_FIELDS:
        e.drop(name)
    if ads_meta or e.get("pubtype_override") or not prior:
        pubtype = classify(e, ads_meta)
    else:
        pubtype = prior
    abbr = venue_abbr(e)
    if abbr:
        e.set("abbr", abbr)
    e.set("pubtype", pubtype)
    e.set("bibtex_show", "true")
    arxiv = arxiv_of(e)
    if arxiv:
        e.set("arxiv", arxiv)
        if not e.get("eprint"):
            e.set("eprint", arxiv)
    if pubtype in ("refereed", "preprint") and (doi_of(e) or arxiv):
        e.set("altmetric", "true")
    if pubtype == "refereed" and doi_of(e):
        e.set("dimensions", "true")
    if doi_of(e) or arxiv:
        e.drop("html")  # the DOI / arXiv buttons already link to the paper
    elif not e.get("html") and e.get("adsurl"):
        e.set("html", e.get("adsurl"))  # nothing else to link to
    if e.get("doi").lower().startswith("10.48550/arxiv."):
        e.drop("doi")
    return e


def normalise(entries: list[Entry]) -> tuple[list[Entry], list[str]]:
    """De-duplicate and clean a list of entries. Returns (entries, log)."""
    log, out = [], []
    for group in group_duplicates(entries):
        best = max(group, key=quality)
        if len(group) > 1:
            others = sorted((e for e in group if e is not best), key=quality, reverse=True)
            log.append(
                f"merged {len(group)} records of '{plain(best.get('title'))[:60]}' -> {best.key} "
                f"(dropped {', '.join(e.key for e in others)})"
            )
            carry_curated(best, others)
            # Keep identifiers the winning record lacks (e.g. the arXiv ID of a
            # CrossRef record), so its DOI / arXiv buttons stay complete.
            for other in others:
                if not doi_of(best) and doi_of(other):
                    best.set("doi", doi_of(other))
                if not arxiv_of(best) and arxiv_of(other):
                    best.set("eprint", arxiv_of(other))
                    best.set("archiveprefix", "arXiv")
                if not best.get("adsurl") and other.get("adsurl"):
                    best.set("adsurl", other.get("adsurl"))
        out.append(finalise(best))
    out.sort(key=sort_key)
    return out, log


def problems(entries: list[Entry]) -> list[str]:
    issues = []
    for group in group_duplicates(entries):
        if len(group) > 1:
            issues.append("duplicate: " + ", ".join(e.key for e in group))
    for e in entries:
        if is_fabricated(e):
            issues.append(f"{e.key}: placeholder author list ('{e.get('author')}')")
        j = e.get("journal").strip()
        if j and (re.fullmatch(r"\\?[a-z]{2,5}", j)):
            issues.append(f"{e.key}: unexpanded journal macro '{j}'")
        if not year_of(e):
            issues.append(f"{e.key}: missing year")
    return issues


def render(entries: list[Entry]) -> str:
    header = (
        "% Generated by bin/sync_publications.py from NASA ADS.\n"
        "% Safe to hand-edit: curated fields (selected, code, slides, preview, ...)\n"
        "% are kept on every sync, and entries with `source = {manual}` are never touched.\n\n"
    )
    return header + "\n".join(format_entry(e) for e in entries)


# --------------------------------------------------------------------------- #
# Remote sources.
# --------------------------------------------------------------------------- #


def http_json(url: str, token: str | None = None, payload: dict | None = None, timeout: int = 30):
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    data = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def fetch_ads(token: str) -> tuple[list[Entry], dict, str]:
    """Return (entries, {bibcode: meta}, host) for every ADS record of the owner."""
    params = urllib.parse.urlencode(
        {"q": ADS_QUERY, "fl": "bibcode,doctype,property,doi,identifier", "rows": 200, "sort": "date desc"}
    )
    last_error = None
    for host in ADS_HOSTS:
        try:
            docs = http_json(f"{host}/search/query?{params}", token)["response"]["docs"]
            meta = {d["bibcode"]: d for d in docs}
            if not meta:
                return [], {}, host
            export = http_json(f"{host}/export/bibtexabs", token, {"bibcode": list(meta), "sort": ["date desc"]})
            return parse_bibtex(export["export"]), meta, host
        except (urllib.error.URLError, KeyError, ValueError) as exc:
            last_error = exc
            print(f"  {host}: {exc}", file=sys.stderr)
    raise RuntimeError(f"ADS unavailable: {last_error}")


def fetch_ads_metrics(token: str, host: str, bibcodes: list[str]) -> dict:
    res = http_json(f"{host}/metrics", token, {"bibcodes": bibcodes})
    this_year = dt.date.today().year
    hist = res.get("histograms", {}).get("citations", {})
    by_year: dict[int, int] = {}
    for series in ("refereed to refereed", "nonrefereed to refereed", "refereed to nonrefereed", "nonrefereed to nonrefereed"):
        for y, n in hist.get(series, {}).items():
            if y.isdigit() and 2016 <= int(y) <= this_year:
                by_year[int(y)] = by_year.get(int(y), 0) + int(n)
    stats = res.get("citation stats", {})
    ind = res.get("indicators", {})
    basic = res.get("basic stats", {})
    return {
        "total_citations": stats.get("total number of citations", 0),
        "refereed_citations": stats.get("total number of refereed citations", 0),
        "h_index": ind.get("h", 0),
        "g_index": ind.get("g", 0),
        "i10_index": ind.get("i10", 0),
        "total_reads": basic.get("total number of reads", 0),
        "citations_by_year": dict(sorted(by_year.items())),
    }


def report_missing(entries: list[Entry]) -> list[str]:
    """Works on ORCID / arXiv that are not in the bibliography (reported, not added)."""
    have = set().union(*(identities(e) for e in entries)) if entries else set()
    missing = []
    try:
        works = http_json(f"https://pub.orcid.org/v3.0/{ORCID_ID}/works")
        for group in works.get("group", []):
            for ext in group.get("external-ids", {}).get("external-id", []):
                kind, value = ext.get("external-id-type", "").lower(), ext.get("external-id-value", "")
                if kind == "doi" and value and "doi:" + value.lower() not in have and not value.lower().startswith("10.48550"):
                    missing.append(f"ORCID DOI {value}")
                if kind == "arxiv" and value and "arxiv:" + ARXIV_RE.search(value).group(1) not in have:
                    missing.append(f"ORCID arXiv {value}")
    except Exception as exc:  # report-only; never fatal
        print(f"  ORCID check skipped: {exc}", file=sys.stderr)
    return sorted(set(missing))


# --------------------------------------------------------------------------- #
# Entry point.
# --------------------------------------------------------------------------- #


def write_metrics(entries: list[Entry], ads_metrics: dict | None) -> bool:
    current = yaml.safe_load(METRICS_PATH.read_text()) if METRICS_PATH.exists() else {}
    current = current or {}
    if ads_metrics:
        current.update(ads_metrics)
        current["updated"] = dt.date.today().isoformat()
    refereed = [e for e in entries if e.get("pubtype") == "refereed"]
    current["papers_refereed"] = len(refereed)
    current["papers_refereed_first_author"] = sum(first_author_is_owner(e) for e in refereed)
    current["papers_preprints"] = sum(e.get("pubtype") == "preprint" for e in entries)
    for stale in ("publications_by_year", "citing_papers", "total_downloads"):
        current.pop(stale, None)
    if "citations_by_year" in current:
        this_year = dt.date.today().year
        current["citations_by_year"] = {int(y): n for y, n in current["citations_by_year"].items() if int(y) <= this_year}
    new_text = yaml.safe_dump(current, sort_keys=False)
    if METRICS_PATH.exists() and METRICS_PATH.read_text() == new_text:
        return False
    METRICS_PATH.write_text(new_text)
    return True


def summary(lines: list[str]) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path and lines:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--offline", action="store_true", help="only normalise the existing file")
    mode.add_argument("--check", action="store_true", help="report problems and exit 1 if the file is not normalised")
    args = ap.parse_args()

    original = BIB_PATH.read_text(encoding="utf-8")
    existing = parse_bibtex(original)

    if args.check:
        issues = problems(existing)
        normalised, _ = normalise(parse_bibtex(original))
        if render(normalised) != original:
            issues.append("papers.bib is not normalised: run `python bin/sync_publications.py --offline`")
        for line in issues:
            print("x", line)
        print(f"{len(existing)} entries, {len(issues)} problem(s)")
        return 1 if issues else 0

    entries, log = normalise(existing)
    ads_metrics = None

    if not args.offline:
        if not ADS_TOKEN:
            print("No ADS_API_TOKEN set; normalising the existing file only.", file=sys.stderr)
        else:
            print(f"Querying ADS: {ADS_QUERY}")
            ads_entries, meta, host = fetch_ads(ADS_TOKEN)
            print(f"  {len(ads_entries)} records from {host}")
            index = {}
            for i, e in enumerate(entries):
                for ident in identities(e):
                    index.setdefault(ident, i)
            for ads in ads_entries:
                bib = bibcode_of(ads)
                ads = finalise(ads, meta.get(bib, {}))
                hit = next((index[i] for i in identities(ads) if i in index), None)
                if hit is None:
                    log.append(f"added {ads.key}: {plain(ads.get('title'))[:70]}")
                    entries.append(ads)
                    continue
                old = entries[hit]
                if old.get("source") == "manual":
                    continue
                carry_curated(ads, [old])
                entries[hit] = ads
            entries, more = normalise(entries)  # fold anything the upsert joined
            log += more
            ads_metrics = fetch_ads_metrics(ADS_TOKEN, host, list(meta))
            missing = report_missing(entries)
            if missing:
                summary(["### Works not yet in ADS", *[f"- {m}" for m in missing]])
                print("Not in the bibliography (add by hand with source = {manual} if ADS never indexes them):")
                print("\n".join("  - " + m for m in missing))

    text = render(entries)
    if text != original:
        BIB_PATH.write_text(text, encoding="utf-8")
        print(f"Wrote {len(entries)} entries to {BIB_PATH.name}")
    if write_metrics(entries, ads_metrics):
        print(f"Updated {METRICS_PATH.name}")
    for line in log:
        print("  " + line)
    summary([f"- {line}" for line in log])
    return 0


if __name__ == "__main__":
    sys.exit(main())
