# tylerbarna.com

Source for [tylerbarna.com](https://tylerbarna.com), built with Jekyll and the
[al-folio](https://github.com/alshedivat/al-folio) theme (v1, gem-based). The
theme's own documentation is in [`docs/`](docs/).

## What updates itself

| What                                     | Source             | When                                   | Code                                                                            |
| ---------------------------------------- | ------------------ | -------------------------------------- | ------------------------------------------------------------------------------- |
| Publications (`_bibliography/papers.bib`) | NASA ADS           | Mondays                                | [`bin/sync_publications.py`](bin/sync_publications.py)                          |
| Citation metrics (`_data/metrics.yml`)   | NASA ADS           | Mondays                                | same script                                                                     |
| Software stars (`_data/repositories.yml`) | GitHub API         | Mondays                                | [`bin/sync_github_stats.py`](bin/sync_github_stats.py)                          |
| Deploy                                   | this repo          | every push to `main`, and after a sync | [`deploy.yml`](.github/workflows/deploy.yml)                                    |
| Outbound link check                      | the deployed site  | 1st of each month; opens an issue      | [`link-check.yml`](.github/workflows/link-check.yml)                            |

The sync is in [`sync-data.yml`](.github/workflows/sync-data.yml). It needs one
repository secret, `ADS_API_TOKEN`, from
[ADS settings](https://ui.adsabs.harvard.edu/user/settings/token) (the older
`SCIX_API_TOKEN` or `ADS_DEV_KEY` names also work).

### How the publication sync works

ADS is the only source of record. ADS already merges a preprint with its
published version, so every work appears once with its real author list and
abstract. Each run matches works by DOI, arXiv ID, bibcode or title and updates
them in place, so duplicates can't build up. ORCID is only checked to _report_
works ADS hasn't indexed yet (see the run summary); nothing is added from it
automatically.

## Editing by hand

All of these survive the weekly sync.

- **Feature a paper on the home page:** add `selected = {true}` to its entry.
- **Add links:** `code`, `slides`, `poster`, `video`, `website`, `pdf`, `supp`.
- **Something ADS will never index:** add the entry with `source = {manual}` and
  a `pubtype`. The sync leaves it alone.
- **Wrong section:** set `pubtype_override` to one of `refereed`, `preprint`,
  `abstract`, `report`, `software`, `data`, `other`.
- **News:** add a file to `_news/` (see existing ones for the format).
- **Software list:** edit names, roles and descriptions in
  `_data/repositories.yml`; the numbers are filled in automatically.
- **CV:** `_data/cv.yml` drives the web CV; the PDF is
  `assets/pdf/barna_tyler_cv.pdf`.

## Checks

Every push and pull request runs:

```bash
python bin/sync_publications.py --check   # duplicates, placeholder authors, unexpanded macros
python bin/check_links.py _site           # links to pages or files that don't exist
```

After editing `papers.bib` by hand, `python bin/sync_publications.py --offline`
tidies it into the canonical format.

## Local preview

```bash
bundle install
LC_ALL=en_US.UTF-8 bundle exec jekyll serve
```

ImageMagick is needed for the responsive WebP images; without it the build
still works and falls back to the original files.
