#!/usr/bin/python3
version = "Tillerz Article Prepare"

from argparse import ArgumentParser
from pathlib import Path
from wa_common import (
    TEXT_ENCODING,
    chdir_to_script_dir,
    ensure_dir,
    load_cfg_or_exit,
    read_json,
    read_text,
    sanitize_filename_component,
    world_paths,
    write_json,
)

word_count_fields = { "content", "sidebarcontent", "sidepanelcontenttop", "sidepanelcontent", "sidebarcontentbottom", "footnotes", "fullfooter" }


def sanitize_slug(slug):
    return sanitize_filename_component(slug)


def resolve_source_json(world_name, slug, edit_folder):
    marker = edit_folder / ".jsonfile"
    json_folder = world_paths(world_name)["json"]

    if marker.is_file():
        marker_value = read_text(marker).strip()
        source_path = json_folder / marker_value
        if source_path.is_file():
            return source_path
        raise FileNotFoundError(
            f"Source marker found, but file missing: {source_path.as_posix()}"
        )

    # Backward-compatible fallback for old extracts that only contain .uuid.
    candidates = sorted(
        json_folder.glob(f"{slug}_*.json"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    if not candidates:
        plain = json_folder / f"{slug}.json"
        if plain.is_file():
            return plain
        raise FileNotFoundError(
            f"No .jsonfile marker found and no fallback source json matched slug '{slug}'."
        )
    return candidates[0]


def load_edited_fields(edit_folder):
    edited = {}
    for path in sorted(edit_folder.glob("*.txt")):
        field = path.stem
        edited[field] = read_text(path)
    return edited


def is_field_changed(original_value, edited_value):
    if original_value is None and edited_value == "":
        return False
    return original_value != edited_value


def as_text(value):
    if value is None:
        return ""
    return value if isinstance(value, str) else str(value)


def word_count(value):
    return len(as_text(value).split())


def resolve_article_id(world_name, slug, edit_folder):
    id_marker = edit_folder / ".uuid"
    if id_marker.is_file():
        article_id = read_text(id_marker).strip()
        if article_id:
            return article_id, id_marker.as_posix()

    source_json_path = resolve_source_json(world_name, slug, edit_folder)
    jdata = read_json(source_json_path)
    article_id = jdata.get("id")
    if not article_id:
        raise ValueError(f"Could not resolve article id from {source_json_path.as_posix()}")
    return article_id, source_json_path.as_posix()


# main
chdir_to_script_dir(__file__)

parser = ArgumentParser()
parser.add_argument("article_slug", help="article slug to prepare from <world>/edit/<slug>")
args = parser.parse_args()
cfg = load_cfg_or_exit("settings.cfg")
world_name = cfg["world_name"]
paths = world_paths(world_name)
slug = sanitize_slug(args.article_slug)
if slug in {"", ".", ".."}:
    print("Invalid article slug.")
    raise SystemExit(1)

edit_folder = paths["edit"] / slug
if not edit_folder.is_dir():
    print(f"Edit folder not found: {edit_folder.as_posix()}")
    raise SystemExit(1)

try:
    source_json_path = resolve_source_json(world_name, slug, edit_folder)
    source_json = read_json(source_json_path)
except (FileNotFoundError, ValueError) as error:
    print(f"Error: {error}")
    raise SystemExit(1)

try:
    article_id, id_source = resolve_article_id(world_name, slug, edit_folder)
except (FileNotFoundError, ValueError) as error:
    print(f"Error: {error}")
    raise SystemExit(1)

edited_fields = load_edited_fields(edit_folder)

if not edited_fields:
    print(f"No .txt fields found in {edit_folder.as_posix()}")
    raise SystemExit(1)

payload = {"id": article_id}
changed_fields = []
counted_word_fields = []
byte_diff_total = 0
word_diff_total = 0
for field, value in edited_fields.items():
    old_value = source_json.get(field)
    if is_field_changed(old_value, value):
        payload[field] = value
        changed_fields.append(field)
        if field in word_count_fields:
            counted_word_fields.append(field)
            old_text = as_text(old_value)
            new_text = as_text(value)
            byte_diff_total += len(new_text.encode(TEXT_ENCODING)) - len(old_text.encode(TEXT_ENCODING))
            word_diff_total += word_count(new_text) - word_count(old_text)

if len(changed_fields)>0:
    deploy_folder = paths["deploy"]
    ensure_dir(deploy_folder)
    output_path = deploy_folder / f"{slug}.json"
    write_json(output_path, payload, indent=2)

    print(f"Slug: {slug}")
    print(f"Article-ID: {article_id}")
    print(f"Source: {source_json_path.as_posix()}")
    if changed_fields:
        print(f"Changed fields ({len(changed_fields)}): " + ", ".join(changed_fields))
    if counted_word_fields:
        print("Word-counted fields: " + ", ".join(counted_word_fields))
    else:
        print("Word-counted fields: none")
    sign_bytes = "+" if byte_diff_total >= 0 else ""
    sign_words = "+" if word_diff_total >= 0 else ""
    print(f"Word count fields byte diff: {sign_bytes}{byte_diff_total} bytes")
    print(f"Word count fields word diff: {sign_words}{word_diff_total} words")
    print(f"Deploy file written: {output_path.as_posix()}")
else:
    print(f"No changes detected for article {slug}.")
