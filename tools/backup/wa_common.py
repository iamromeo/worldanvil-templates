#!/usr/bin/python3

from datetime import datetime
import json
import os
from pathlib import Path
import requests

TEXT_ENCODING = "utf-8"


def read_text(path):
    return Path(path).read_text(encoding=TEXT_ENCODING)


def write_text(path, content):
    Path(path).write_text(content, encoding=TEXT_ENCODING)


def read_json(path):
    return json.loads(read_text(path))


def write_json(path, data, compact=False, indent=None):
    kwargs: dict = {"ensure_ascii": False}
    if compact:
        kwargs["separators"] = (",", ":")
    elif indent is not None:
        kwargs["indent"] = indent
    Path(path).write_text(json.dumps(data, **kwargs), encoding=TEXT_ENCODING)


def load_cfg(path):
    cfg = {}
    with open(path, "r", encoding=TEXT_ENCODING) as myfile:
        for line in myfile:
            line = line.strip()
            if not line.startswith("#"):
                name, var = line.partition("=")[::2]
                cfg[name.strip()] = str(var.strip())
    return cfg


def load_cfg_or_exit(path="settings.cfg"):
    try:
        return load_cfg(path)
    except FileNotFoundError:
        print(f"Error: The file {path} was not found.")
        raise SystemExit(1)
    except IOError:
        print(f"Error: The file {path} could not be read.")
        raise SystemExit(1)


def sanitize_filename_component(value):
    invalid_filename_chars = '/\\<>:"|?*'
    invalid_filename_chars += "".join(chr(i) for i in range(32))
    table = str.maketrans("", "", invalid_filename_chars)
    sanitized = os.path.basename(value.replace("\\", "/")).translate(table).strip()
    return sanitized


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def chdir_to_script_dir(file_path):
    os.chdir(Path(file_path).resolve().parent)


def world_paths(world_name, root_folder=None):
    if root_folder:
        root = Path(root_folder).expanduser() / world_name
    else:
        root = Path(world_name)
    return {
        "root": root,
        "json": root / "json",
        "edit": root / "edit",
        "deploy": root / "deploy",
        "text-export": root / "text-export",
    }


def parse_wa_datetime(raw):
    if not isinstance(raw, str) or raw == "":
        return None
    cleaned = raw.replace(".000000", "")
    try:
        return datetime.strptime(cleaned, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def parse_tags(value):
    if value is None:
        return []
    if isinstance(value, str):
        if value == "":
            return []
        return [part for part in value.split(",") if part != ""]
    return []


def format_tags(tags):
    return ",".join(tags)


def unique_preserve_order(values):
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def validate_single_comma_free_tag(value, label):
    if "," in value:
        raise ValueError(f"{label} may not contain commas.")


def build_request_headers(cfg, version):
    world_name = cfg["world_name"]
    return {
        "Content-Type": "application/json",
        "x-auth-token": cfg["x_auth_token"],
        "x-application-key": cfg["x_application_key"],
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " + version,
        "Referer": "https://www.worldanvil.com/w/" + world_name,
    }


def build_api_url(cfg):
    proxy_url = cfg.get("proxy", "")
    base_url = proxy_url if proxy_url != "" else "https://www.worldanvil.com"
    return base_url + "/api/external/boromir/"


def fetch_article_list_page(session, api_url, world_id, request_headers, limit=50, offset=0):
    endpoint = api_url + "world/articles?id=" + world_id + "&granularity=1"
    payload = {"limit": limit, "offset": offset}
    response = session.post(endpoint, json=payload, headers=request_headers)
    response.raise_for_status()
    return response.json()


def fetch_article(session, api_url, article_id, request_headers, granularity=3):
    endpoint = api_url + "article?id=" + article_id + "&granularity=" + str(granularity)
    response = session.get(endpoint, headers=request_headers)
    response.raise_for_status()
    return response.json()


def patch_article(session, api_url, article_id, payload, request_headers, timeout=60):
    endpoint = api_url + "article?id=" + article_id
    response = session.patch(
        endpoint, json=payload, headers=request_headers, timeout=timeout
    )
    response.raise_for_status()
    return response


writing_fields = (
    "title",
    "subheading",
    "snippet",
    "excerpt",
    "pronunciation",
    "content",
    "fullfooter",
    "sidepanelcontenttop",
    "sidepanelcontent",
    "sidebarcontentbottom",
    "sidebarcontent",
)


def load_all_json_articles(json_folder):
    results = []
    for path in sorted(Path(json_folder).glob("*.json")):
        try:
            data = read_json(path)
        except Exception as error:
            print(f"Warning: skipped invalid json {path.as_posix()}: {error}")
            continue
        slug = data.get("slug")
        if not isinstance(slug, str) or slug == "":
            continue
        update_obj = data.get("updateDate")
        update_raw = update_obj.get("date") if isinstance(update_obj, dict) else None
        update_date = parse_wa_datetime(update_raw)
        source_mtime = path.stat().st_mtime
        results.append((data, path, update_date, source_mtime))
    return results


def matches_title(jdata, query, case_sensitive):
    title = jdata.get("title") or ""
    if not case_sensitive:
        return query.lower() in title.lower()
    return query in title


def matches_slug(jdata, query, case_sensitive):
    slug = jdata.get("slug") or ""
    if not case_sensitive:
        return query.lower() in slug.lower()
    return query in slug


def matches_text(jdata, query, case_sensitive):
    for field in writing_fields:
        value = jdata.get(field)
        if not isinstance(value, str) or value == "":
            continue
        if not case_sensitive:
            if query.lower() in value.lower():
                return True
        else:
            if query in value:
                return True
    return False


def matches_tags(jdata, required_tags):
    article_tags = set(parse_tags(jdata.get("tags")))
    return set(required_tags).issubset(article_tags)


def matches_type(jdata, entity_type, case_sensitive):
    entity_class = jdata.get("entityClass") or ""
    if not case_sensitive:
        return entity_type.lower() == entity_class.lower()
    return entity_type == entity_class


def matches_state(jdata, state, case_sensitive):
    article_state = jdata.get("state") or ""
    if not case_sensitive:
        return state.lower() == article_state.lower()
    return state == article_state


def load_latest_json_by_slug(json_folder, require_article_id=False):
    latest_by_slug = {}
    for path in sorted(Path(json_folder).glob("*.json")):
        try:
            data = read_json(path)
        except Exception as error:
            print(f"Warning: skipped invalid json {path.as_posix()}: {error}")
            continue

        slug = data.get("slug")
        if not isinstance(slug, str) or slug == "":
            continue

        if require_article_id:
            article_id = data.get("id")
            if not isinstance(article_id, str) or article_id == "":
                continue

        update_obj = data.get("updateDate")
        update_raw = update_obj.get("date") if isinstance(update_obj, dict) else None
        update_date = parse_wa_datetime(update_raw)
        source_mtime = path.stat().st_mtime

        current = latest_by_slug.get(slug)
        if current is None:
            latest_by_slug[slug] = (data, path, update_date, source_mtime)
            continue

        current_key = (
            current[2] if current[2] is not None else datetime.min,
            current[3],
        )
        new_key = (
            update_date if update_date is not None else datetime.min,
            source_mtime,
        )
        if new_key >= current_key:
            latest_by_slug[slug] = (data, path, update_date, source_mtime)

    return latest_by_slug
