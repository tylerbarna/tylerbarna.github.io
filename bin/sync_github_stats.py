#!/usr/bin/env python3
"""Refresh stars, forks and last-push date in _data/repositories.yml.

Only the numbers GitHub owns are touched. Names, roles and descriptions are
hand-written and left alone. If GitHub is unreachable the file is not modified.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

PATH = Path(__file__).resolve().parent.parent / "_data" / "repositories.yml"
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def fetch(repo: str):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "tylerbarna.com stats sync"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"  {repo}: {exc}", file=sys.stderr)
        return None


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    header = "".join(line for line in text.splitlines(keepends=True) if line.startswith("#"))
    data = yaml.safe_load(text)
    for project in data.get("projects", []):
        info = fetch(project["repo"])
        if not info:
            continue
        project["stars"] = info["stargazers_count"]
        project["forks"] = info["forks_count"]
        # GitHub's language detection can be misleading (NMMA is reported as
        # "Jupyter Notebook"), so only fill the language in when it's missing.
        project.setdefault("language", info.get("language"))
        project["updated"] = info["pushed_at"][:10]
        print(f"  {project['repo']}: {project['stars']} stars, {project['forks']} forks")
    new = header + yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    if new != text:
        PATH.write_text(new, encoding="utf-8")
        print(f"Updated {PATH.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
