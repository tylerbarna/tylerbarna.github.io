#!/usr/bin/env python3
"""Fail if any page in the built site links to a file that doesn't exist.

Checks href/src attributes that point inside the site (relative paths, root-
relative paths, and absolute URLs on the site's own domain). External links are
checked separately and less often by .github/workflows/link-check.yml.

  python bin/check_links.py _site [--site-url https://tylerbarna.com]
"""

import argparse
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "data:", "#")


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.found = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if value and name in ("href", "src") and not (tag == "link" and ("rel", "preconnect") in attrs):
                self.found.append(value.strip())


def resolve(root: Path, page: Path, link: str, site_host: str):
    if link.startswith(SKIP_SCHEMES) or "{{" in link:
        return None
    parsed = urlparse(link)
    if parsed.scheme in ("http", "https") or link.startswith("//"):
        if parsed.netloc != site_host:
            return None
        path = parsed.path
    else:
        page_url = "/" + page.relative_to(root).as_posix()
        path = urlparse(urljoin(page_url, link)).path
    target = root / unquote(path).lstrip("/")
    if path.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("site", type=Path)
    ap.add_argument("--site-url", default="https://tylerbarna.com")
    args = ap.parse_args()
    host = urlparse(args.site_url).netloc
    broken = {}
    pages = sorted(args.site.rglob("*.html"))
    for page in pages:
        parser = Links()
        parser.feed(page.read_text(encoding="utf-8", errors="replace"))
        for link in parser.found:
            target = resolve(args.site, page, link, host)
            if target is not None and not target.exists():
                broken.setdefault(link, set()).add(page.relative_to(args.site).as_posix())
    for link, where in sorted(broken.items()):
        print(f"x {link}  (on {', '.join(sorted(where))})")
    print(f"checked {len(pages)} pages, {len(broken)} broken internal link(s)")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
