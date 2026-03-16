# World Anvil Backup/Edit/Deploy Scripts

Scripts in this folder support a full flow:

1. download article JSON backups
2. extract editable text fields into plain text files
3. prepare minimal update payloads from edited text files
4. manage the article tags
5. deploy payloads to WA REST API


# Requirements

- Python 3
- Python packages:
  - `requests`
  - `beautifulsoup4`
  - `lxml`

Install example:

```bash
pip install requests beautifulsoup4 lxml
```


# Configuration

Copy `settings-template.cfg` to `settings.cfg` and fill values:

- `world_name`
- `world_id`
- `x_auth_token`
- `x_application_key`
- `proxy` (optional; leave empty to use `https://www.worldanvil.com`)

The scripts read `settings.cfg` from this folder (`tools/backup`).


# Scripts

## 1) Full Backup

Script:

- Linux/macOS: `python3 backup-full.py`
- Windows: `backup-full.cmd`

Purpose:

- fetches all articles via WA API
- stores full article JSON in `<world_name>/json/`

Parameters:

- none


## 2) Extract Editable Fields

Script:

- Linux/macOS: `python3 extract.py <filename> [options]`
- Windows: `extract.cmd <filename> [options]`

Input:

- `<filename>` is a JSON file name from `<world_name>/json/`

Output:

- creates/updates `<world_name>/edit/<article-slug>/`
- writes one `<field>.txt` per extracted field
- writes `.jsonfile` with original JSON file name
- writes `.uuid` with article id (if present)
- with `--writing`, also writes combined plain-text exports to `<world_name>/writing/<entityClass>/<slug>.txt`

Usage:

```bash
usage: extract.py [-h] [-f FIELDS] [-l] [-a] [-t] [-e] [-w] filename
```

Parameters:

- `filename` article json file name, looked up in `<world_name>/json/`
- `-f, --fields` comma-separated field list to extract
- `-l, --list` list fields in JSON (default list mode: string fields)
- `-a, --all` with `-l`, include all fields (not only strings)
- `-t, --types` with `-l`, show field types
- `-e, --empty` create files for empty fields too
- `-w, --writing` extract writing fields into `<world_name>/writing/<entityClass>/<slug>.txt`

Examples:

- `python3 extract.py <article-json-file> --writing`
- `python3 extract.py --writing --all`
  exports writing files for all published articles in `<world_name>/json/`


## 3) Prepare Deploy Payload for One Article

Script:

- Linux/macOS: `python3 prepare.py <article-slug>`
- Windows: `prepare.cmd <article-slug>`

Purpose:

- reads edited files from `<world_name>/edit/<article-slug>/`
- loads original JSON (`.jsonfile` marker, with fallback by slug)
- compares each edited field with original value
- creates minimal payload containing:
  - `id`
  - only changed fields
- writes payload to `<world_name>/deploy/<article-slug>.json`

Notes:

- `None` vs empty string for text fields is treated as unchanged
- prints byte/word diffs for changed fields listed in `word_count_fields`

Usage:

```bash
usage: prepare.py [-h] article_slug
```

Parameters:

- `article_slug` slug folder name under `<world_name>/edit/`


## 4) Tag Manager

Script:

- Linux/macOS: `python3 tagmgr.py <command>`

Purpose:

Tool to manage the article tags.

- reads article json files from `<world_name>/json/`
- inspects and updates article tags
- writes tag updates to `<world_name>/deploy/<article-slug>.json`
- if deploy payloads already exist, updates those files in place so multiple tag operations can be chained safely
- update files can then deployed to WA using `python3 deploy.py`

Format:

- a `<tag list>` can be a single tag or several tags separated by comma
- a single tag may not contain a comma
- `<article-slug>` is the slug of the article as seen in its WA URL (`../a/<article-slug>`)

Usage examples:

List all tags of all articles with usage count and some stats:
- `python3 tagmgr.py --stats`
List all tags of type Document with usage count and some stats:
- `python3 tagmgr.py --stats --type Document`

```
[..]
we2021: 1
we2022: 6
we2023: 1
we2024: 1
we2025: 1
zaxor: 1
---
articles with tags: 36
articles with no tags: 25
average tags per tagged article: 3.06
```

List all tags of the given article:

- `python3 tagmgr.py --tags <article-slug>`

List all articles using the given tags:

- `python3 tagmgr.py --articles "<tag list>"`

List all articles of type Document using the given tags:

- `python3 tagmgr.py --articles "<tag list>" --type Document`

Replace a tag in all articles or the given article:

- `python3 tagmgr.py --replace <old tag> <new tag> [--all | <article-slug>]`

Replace a tag in all articles of type Document:

- `python3 tagmgr.py --replace <old tag> <new tag> --all --type Document`

Dry-run replace:

- `python3 tagmgr.py --replace <old tag> <new tag> [--all | <article-slug>] --dry-run`

Add a list of tags to all articles or a given article:

- `python3 tagmgr.py --add "<tag list>" [--all | <article-slug>]`

Add a list of tags to all articles of type Document:

- `python3 tagmgr.py --add "<tag list>" --all --type Document`

Dry-run add:

- `python3 tagmgr.py --add "<tag list>" [--all | <article-slug>] --dry-run`

Remove a list of tags from all articles or a given article:

- `python3 tagmgr.py --remove "<tag list>" [--all | <article-slug>]`

Remove a list of tags from all articles of type Document:

- `python3 tagmgr.py --remove "<tag list>" --all --type Document`

Dry-run remove:

- `python3 tagmgr.py --remove "<tag list>" [--all | <article-slug>] --dry-run`

A dry-run lets you run the command to see the output without writing any update files to deploy/.

Optional filter `--type <entityClass>`:

- all commands that do not target a single article support `--type <type>`
- `<type>` matches the article root-level `entityClass` value in json files
- `--dry-run` is supported by `--add`, `--replace`, and `--remove`
- available values (alphabetical):
- `Article`
- `Condition`
- `Document`
- `Ethnicity`
- `Formation`
- `Item`
- `Landmark`
- `Language`
- `Law`
- `Location`
- `Material`
- `MilitaryConflict`
- `Myth`
- `Organization`
- `Person`
- `Plot`
- `Profession`
- `Prose`
- `Rank`
- `Ritual`
- `Settlement`
- `Species`
- `Vehicle`


## 5) Deploy Payloads

Script:

- Linux/macOS: `python3 deploy.py [--dry-run] [--validate]`
- Windows: `deploy.cmd [--dry-run] [--validate]`

Purpose:

- scans `<world_name>/deploy/*.json`
- validates payload format (`id` + at least one changed field)
- sends updates to WA API:
  - method: `PATCH`
  - URL: `.../api/external/boromir/article?id=<article_id>`
  - body: payload without `id`

Usage:

```bash
usage: deploy.py [-h] [--dry-run] [--validate]
```

Parameters:

- `--dry-run` validate and print planned PATCH calls without sending requests
- `--validate` after successful PATCH, fetch article again and verify uploaded fields


# Typical Workflow

1. `python3 backup-full.py`
2. `python3 extract.py <article-json-file>`
3. update/add files in `<world_name>/edit/<article-slug>/`
4. `python3 tagmgr --add <tag list> <article-slug>`
5. `python3 prepare.py <article-slug>`
6. review `<world_name>/deploy/<article-slug>.json`
7. `python3 deploy.py --dry-run`
8. `python3 deploy.py --validate`
