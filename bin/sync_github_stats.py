#!/usr/bin/env python3
"""
Sync GitHub repository stats, organization contributions, and aggregate metrics.
Updates `_data/repositories.yml` automatically during the weekly GitHub Actions workflow.
"""

import os
import json
import urllib.request
import urllib.error
import yaml

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

def github_request(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; TylerBarnaBot/1.0)",
        "Accept": "application/vnd.github.v3+json",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code} for {url}: {e.reason}")
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    repo_yaml_path = os.path.join(os.path.dirname(__file__), "..", "_data", "repositories.yml")
    repo_yaml_path = os.path.abspath(repo_yaml_path)

    if not os.path.exists(repo_yaml_path):
        print(f"File not found: {repo_yaml_path}")
        return

    with open(repo_yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # 1. Update individual project stars and forks
    projects = data.get("projects", [])
    for proj in projects:
        repo_name = proj.get("repo")
        if not repo_name:
            continue
        print(f"Fetching repo info for {repo_name}...")
        repo_data = github_request(f"https://api.github.com/repos/{repo_name}")
        if repo_data and "stargazers_count" in repo_data:
            proj["stars"] = repo_data["stargazers_count"]
            proj["forks"] = repo_data["forks_count"]
            print(f"  -> {repo_name}: {proj['stars']} stars, {proj['forks']} forks")

    # 2. Update aggregate stars across all associated repos
    associated = data.get("associated_repos", [
        "nasa-gcn/gcn.nasa.gov",
        "nasa-gcn/gcn-schema",
        "nuclear-multimessenger-astronomy/nmma",
        "nuclear-multimessenger-astronomy/survey-sim",
        "nuclear-multimessenger-astronomy/sim_based_inference",
        "skyportal/skyportal",
        "tylerbarna/IIb-or-not-IIIb",
    ])

    total_combined_stars = 0
    for assoc_repo in associated:
        # Check if already fetched in projects
        matched = next((p for p in projects if p.get("repo") == assoc_repo), None)
        if matched and "stars" in matched:
            total_combined_stars += matched["stars"]
        else:
            print(f"Fetching associated repo {assoc_repo}...")
            r_data = github_request(f"https://api.github.com/repos/{assoc_repo}")
            if r_data and "stargazers_count" in r_data:
                total_combined_stars += r_data["stargazers_count"]

    print(f"Total combined stars calculated: {total_combined_stars}")
    if total_combined_stars >= 400:
        combined_str = f"{(total_combined_stars // 10) * 10}+"
    else:
        combined_str = f"{total_combined_stars}"

    if "profile" not in data:
        data["profile"] = {}
    data["profile"]["combined_stars"] = combined_str

    # 3. Fetch total merged/authored pull requests
    username = data["profile"].get("username", "tylerbarna")
    pr_data = github_request(f"https://api.github.com/search/issues?q=author:{username}+type:pr")
    if pr_data and "total_count" in pr_data:
        pr_count = pr_data["total_count"]
        pr_str = f"{(pr_count // 10) * 10}+"
        data["profile"]["merged_prs"] = pr_str
        print(f"Total PRs found: {pr_count} ({pr_str})")

    # Write back YAML preserving readable format
    with open(repo_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, default_flow_style=False, allow_unicode=True)

    print("Successfully updated _data/repositories.yml!")

if __name__ == "__main__":
    main()
