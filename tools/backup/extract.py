#!/usr/bin/python3
version = 'Tillerz Article Extract'

# --- requirements ----------------------------------------------------
# see https://github.com/Tillerz/worldanvil-templates/blob/master/tools/backup/

from argparse import ArgumentParser
from pathlib import Path
import re
from shutil import copy2
from sys import platform
from wa_common import (
    chdir_to_script_dir,
    ensure_dir,
    load_all_json_articles,
    load_cfg_or_exit,
    load_latest_json_by_slug,
    matches_slug,
    matches_state,
    matches_tags,
    matches_text,
    matches_title,
    matches_type,
    parse_tags,
    sanitize_filename_component,
    unique_preserve_order,
    world_paths,
    writing_fields,
    read_json,
    write_text,
)

types_str = { "excerpt", "publicationDate", "notificationDate", "updateDate", "snippet", "scrapbook", "url", "name", "title", "slug", "state", "icon", "tags", "credits", "editURL", "metaTitle", "metaDescription", "metaKeywords", "canonicalURL", "robots", "ogTitle", "ogDescription", "ogImage", "twitterTitle", "twitterDescription", "twitterImage", "customCss", "customJs", "content", "sidepanelcontenttop", "sidepanelcontent", "sidebarcontent", "sidebarcontentbottom", "footnotes", "fullfooter", "subheading", "authornotes", "pronunciation" }
types_uuid = { "id", "worldID", "parentID", "categoryID", "authorID", "folderId" }
types_int = { "likes", "views", "wordcount", "viewCount", "likeCount", "commentCount", "positionX", "positionY", "zoomLevel", "mapWidth", "mapHeight", "mapMarkerWidth", "mapMarkerHeight" }
types_bool = { "isWip", "isDraft", "isAdultContent", "isLocked", "allowComments", "showAuthor", "showLastModified", "showWordCount", "showInSidebar", "showInMap", "isPinned", "isFeatured", "isFeaturedArticle", "isPublished", "showInToc", "isEmphasized", "displayAuthor", "displayChildrenUnder", "displayTitle", "displaySheet", "isEditable", "coverIsMap" }
default_fields = { "title", "subheading", "snippet", "excerpt", "pronunciation", "content", "fullfooter", "sidepanelcontenttop", "sidepanelcontent", "sidebarcontentbottom", "sidebarcontent", "footnotes", "authornotes", "scrapbook", "credits", "displayCss" }
SPECIAL_LINK_RE = re.compile(r'@\[([^\]]*)\]\([^)]*\)')
BBCODE_NEWLINE_RE = re.compile(r'\[(?:br|/p|p)\s*/?\]', re.IGNORECASE)
BBCODE_HR_RE = re.compile(r'\[hr\s*/?\]', re.IGNORECASE)
BBCODE_HEADLINE_RE = re.compile(r'\[h([1-4])\](.*?)\[/h\1\]', re.IGNORECASE | re.DOTALL)
BBCODE_TABLE_CELL_RE = re.compile(r'\[t[dh]\](.*?)\[/t[dh]\]', re.IGNORECASE | re.DOTALL)
BBCODE_TABLE_TRAILING_SEP_RE = re.compile(r',\s*(?=\[/(?:tr|row)\]|\[/table\])', re.IGNORECASE)
BBCODE_TABLE_ROW_RE = re.compile(r'\[/(?:tr|row)\]', re.IGNORECASE)
BBCODE_TAG_RE = re.compile(r'\[/?(?!roll:)[a-z*][^\]\n]*\]', re.IGNORECASE)
WHITESPACE_BEFORE_NEWLINE_RE = re.compile(r'[ \t]+\n')
EXCESS_BLANK_LINES_RE = re.compile(r'(?:\r?\n[ \t]*){3,}')


def unroll(data, indent=0, types=False, all=False, fields={}):
    spacing = "  " * (indent)
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                if all or (fields != {} and key in fields):
                    print(f"{spacing}{key}:")
                unroll(value, indent + 1, types, all)
            else:
                if all or (fields != {} and key in fields):
                    o = "?" if type(value).__name__ == "NoneType" else type(value).__name__
                    if key in types_str:
                        o = "str"
                    if key in types_uuid:
                        o = "uuid"
                    if key in types_int:
                        o = "int"
                    if key in types_bool:
                        o = "bool"
                    if all or o == "str":
                        if types:
                            print(f"{spacing}{key}: {o}")
                        else:
                            print(f"{spacing}{key}: {value}")
    elif isinstance(data, list):
        for index, item in enumerate(data):
            if isinstance(item, (dict, list)):
                if all or (fields != {} and item in fields):
                    print(f"{spacing}[{index}]")
                unroll(item, indent + 1, types, all)
            else:
                if all or (fields != {} and item in fields):
                    print(f"{spacing}- {item}")
    else:
        print(f"{spacing}{data}")


def build_writing_text(jdata, keep_bbcode=False):
    parts = []
    for field in writing_fields:
        value = jdata.get(field)
        if isinstance(value, str) and value != "":
            value = value.replace("\r\n", "\n")
            if not keep_bbcode:
                # WA article links
                value = SPECIAL_LINK_RE.sub(r'\1', value)
                # BBCODE
                value = BBCODE_HEADLINE_RE.sub(lambda match: f"{'!' * int(match.group(1))} {match.group(2).strip()}\n\n", value)
                value = BBCODE_HR_RE.sub("\n---\n", value)
                value = BBCODE_NEWLINE_RE.sub("\n", value)
                value = BBCODE_TABLE_CELL_RE.sub(lambda m: m.group(1).strip() + ", ", value)
                value = BBCODE_TABLE_TRAILING_SEP_RE.sub("", value)
                value = BBCODE_TABLE_ROW_RE.sub("\n", value)
                value = BBCODE_TAG_RE.sub("", value)
            value = WHITESPACE_BEFORE_NEWLINE_RE.sub("\n", value)
            value = EXCESS_BLANK_LINES_RE.sub("\n\n", value).strip()
            if value != "":
                parts.append(value)
    return "\n\n".join(parts)


def write_writing_file(base_folder, jdata, keep_bbcode=False):
    entity_class = sanitize_filename_component(jdata.get("entityClass", ""))
    slug = sanitize_filename_component(jdata.get("slug", ""))
    if entity_class in {"", ".", ".."} or slug in {"", ".", ".."}:
        return False
    content = build_writing_text(jdata, keep_bbcode)
    if len(content.encode()) < 100:
        return False

    target_folder = Path(base_folder) / "text-export" / entity_class
    ensure_dir(target_folder)
    target_file = target_folder / f"{slug}.txt"
    write_text(target_file, content)
    print(f"Text export: {target_file.as_posix()}")
    return True


def load_latest_articles(json_folder):
    return [item[0] for item in load_latest_json_by_slug(json_folder).values()]


def extract_blocks_from_articles(articles, start_str, end_str, output_file):
    pattern = re.compile(re.escape(start_str) + r'(.*?)' + re.escape(end_str), re.DOTALL)

    sections = []
    for data, _path, _update_date, _source_mtime in articles:
        slug = data.get("slug") or ""
        uuid = data.get("id") or ""
        title = data.get("title") or slug

        blocks = []
        for field in writing_fields:
            value = data.get(field)
            if not isinstance(value, str) or value == "":
                continue
            for match in pattern.finditer(value):
                block = match.group(1).strip()
                if block:
                    blocks.append(block)

        if not blocks:
            continue

        section_lines = [f"{title} ({slug}, {uuid})"]
        section_lines.extend(blocks)
        sections.append("\n".join(section_lines))

    content = "\n---\n".join(sections)
    if sections:
        content += "\n---"
    Path(output_file).expanduser().write_text(content, encoding="utf-8")
    print(f"Extracted blocks from {len(sections)} article(s) to {output_file}")


def is_published_writing_article(jdata):
    return jdata.get("state") == "public"


def apply_filters(articles, args, required_tags):
    result = []
    for item in articles:
        data = item[0]
        if args.title is not None and not matches_title(data, args.title, args.case):
            continue
        if args.slug is not None and not matches_slug(data, args.slug, args.case):
            continue
        if args.text is not None and not matches_text(data, args.text, args.case):
            continue
        if required_tags and not matches_tags(data, required_tags):
            continue
        if args.entity_type is not None and not matches_type(data, args.entity_type, args.case):
            continue
        if args.state is not None and not matches_state(data, args.state, args.case):
            continue
        result.append(item)
    return result


def parse_required_tags(args, parser):
    if args.tags is None:
        return []
    tags = unique_preserve_order(parse_tags(args.tags))
    if not tags:
        parser.error("--tags: tag list is empty")
    return tags


# main
chdir_to_script_dir(__file__)

parser = ArgumentParser()
parser.add_argument('filename', nargs='?', help="article json file name, it will be looked for in the world/json folder")
parser.add_argument("-f", "--fields", required=False, help="fields to extract, separated by commas, default: " + ",".join(str(x) for x in default_fields))
parser.add_argument("-l", "--list", required=False, action='store_true', help="list fields found in the json file, default: only strings")
parser.add_argument("-a", "--all", required=False, action='store_true', help="-l will list ALL fields found in the json file, not just strings")
parser.add_argument("-t", "--types", required=False, action='store_true', help="-l will display the type of each field found")
parser.add_argument("-e", "--empty", required=False, action='store_true', help="create files for empty fields, too")
parser.add_argument("-x", "--export", required=False, action='store_true', help="extract main article text fields into text-export/<entityClass>/<slug>.txt")
parser.add_argument("-b", "--bbcode", required=False, action='store_true', help="with --export, keep BBcode tags in output instead of stripping them")
parser.add_argument("--copy", metavar="DEST_FOLDER", help="copy matching JSON files to DEST_FOLDER")
parser.add_argument("--extract-blocks", metavar="OUTPUT_FILE", help="extract all text blocks between --start and --end from every article")
parser.add_argument("--start", help="start delimiter for --extract-blocks")
parser.add_argument("--end", help="end delimiter for --extract-blocks")
parser.add_argument("--title", help="filter: articles with this string in the title")
parser.add_argument("--slug", help="filter: articles with this string in the slug")
parser.add_argument("--text", help="filter: articles with this string in any writing field")
parser.add_argument("--tags", help="filter: articles that have all of these comma-separated tags")
parser.add_argument("--type", dest="entity_type", help="filter: entity class (e.g. Person, Location)")
parser.add_argument("--state", help="filter: article state (e.g. public, draft, wip)")
parser.add_argument("--case", action="store_true", help="filter: case-sensitive matching (default: case-insensitive)")
args = parser.parse_args()
cfg = load_cfg_or_exit("settings.cfg")
world_name = cfg['world_name']
world_id = cfg['world_id']
paths = world_paths(world_name, cfg.get('root_folder'))
json_folder = paths["json"]
output_folder = paths["edit"]

if args.copy:
    if args.title is None and args.slug is None and args.text is None and args.tags is None and args.entity_type is None and args.state is None:
        parser.error("--copy requires at least one filter: --title, --slug, --text, --tags, --type, or --state")
    if not json_folder.is_dir():
        print(f"JSON folder not found: {json_folder.as_posix()}")
        raise SystemExit(1)
    required_tags = parse_required_tags(args, parser)
    dest_folder = Path(args.copy).expanduser()
    ensure_dir(dest_folder)
    articles = apply_filters(list(load_latest_json_by_slug(json_folder).values()), args, required_tags)
    copied = 0
    for _data, path, _update_date, _source_mtime in articles:
        copy2(path, dest_folder / path.name)
        print(f"Copied: {path.name}")
        copied += 1
    print(f"Copied {copied} file(s) to {dest_folder.as_posix()}")
    raise SystemExit(0)

if args.extract_blocks:
    if not args.start or not args.end:
        parser.error("--extract-blocks requires both --start and --end")
    if not json_folder.is_dir():
        print(f"JSON folder not found: {json_folder.as_posix()}")
        raise SystemExit(1)
    required_tags = parse_required_tags(args, parser)
    articles = apply_filters(list(load_latest_json_by_slug(json_folder).values()), args, required_tags)
    extract_blocks_from_articles(articles, args.start, args.end, args.extract_blocks)
    raise SystemExit(0)

# create the export folder if it doesn't exist
if args.export:
    try:
        ensure_dir(paths["text-export"])
    except OSError as error:
        print(f"Cannot create folder {world_name + '/text-export'}: {error}")
        raise SystemExit(1)

# create the extract folder if it doesn't exist
try:
    ensure_dir(output_folder)
except OSError as error:
    print(f"Cannot create folder {output_folder}: {error}")
    raise SystemExit(1)

if args.export and args.all:
    for jdata in load_latest_articles(json_folder):
        if is_published_writing_article(jdata):
            write_writing_file(paths["root"], jdata, args.bbcode)
    raise SystemExit(0)

if args.filename is None:
    print("Invalid filename.")
    raise SystemExit(1)

filename = sanitize_filename_component(args.filename)
if filename in {"", ".", ".."}:
    print("Invalid filename.")
    raise SystemExit(1)

file_input = json_folder / filename
if file_input.is_file():
    jdata = read_json(file_input)

    if args.export:
        if not is_published_writing_article(jdata):
            raise SystemExit(0)
        if not write_writing_file(paths["root"], jdata, args.bbcode):
            print("Could not write text export: missing or invalid entityClass/slug.")
            raise SystemExit(1)
        raise SystemExit(0)

    title = jdata["title"]
    slug = jdata["slug"]
    wordcount = jdata["wordcount"]
    last_modif = jdata["updateDate"]["date"]
    fields = default_fields
    if (args.fields != None and args.fields != ""):
        fields = args.fields.split(',')

    print(f'Title: {title}')
    print(f'Slug: {slug}')
    print(f'Last Modified: {last_modif.replace(".000000","")}')
    print(f'Wordcount: {wordcount} words')
    
    if (args.list):
        print('------------------------')
        print('Fields found in article json file:')
        print('------------------------')
        for field in jdata:
            unroll({field: jdata[field]}, 0, args.types, args.all, fields)
        print('------------------------')
    else:
        print(f'Field list: ' + ",".join(str(x) for x in default_fields))
        print('------------------------')

        extract_folder = output_folder / slug

        # create the extract folder if it doesn't exist
        try:
            ensure_dir(extract_folder)
        except OSError as error:
            print(f"Cannot create folder {extract_folder}: {error}")
            raise SystemExit(1)

        # remember where the content came from (filename, article-id)
        write_text(extract_folder / '.jsonfile', filename)
        if (jdata['id'] != "" and jdata['id'] != None):
            write_text(extract_folder / '.uuid', jdata['id'])

        # extract all the fields into single text files
        # if -e was given, create empty files for empty fields, too
        for field in fields:
            if field in jdata:
                file_for_field = extract_folder / (field + ".txt")
                if (jdata[field] != "" and jdata[field] != None):
                    print(f'Extracting field {field} to {file_for_field}')
                    write_text(file_for_field, jdata[field])
                else:
                    if args.empty:
                        print(f'Field {field} is empty, creating empty file {file_for_field}')
                        write_text(file_for_field, "")
                    else:
                        print(f'Field {field} is empty/unset, not saving.')
            else:
                print(f'Field {field} not found in json data.')
        print('------------------------')

else:
    print(f"Could not find file {file_input}")
