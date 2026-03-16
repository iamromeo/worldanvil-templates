#!/usr/bin/python3
version = 'Tillerz Article Extract'

# --- requirements ----------------------------------------------------
# see https://github.com/Tillerz/worldanvil-templates/blob/master/tools/backup/

from argparse import ArgumentParser
from pathlib import Path
import re
from sys import platform
from wa_common import (
    chdir_to_script_dir,
    ensure_dir,
    load_cfg_or_exit,
    load_latest_json_by_slug,
    sanitize_filename_component,
    world_paths,
    read_json,
    write_text,
)

types_str = { "excerpt", "publicationDate", "notificationDate", "updateDate", "snippet", "scrapbook", "url", "name", "title", "slug", "state", "icon", "tags", "credits", "editURL", "metaTitle", "metaDescription", "metaKeywords", "canonicalURL", "robots", "ogTitle", "ogDescription", "ogImage", "twitterTitle", "twitterDescription", "twitterImage", "customCss", "customJs", "content", "sidepanelcontenttop", "sidepanelcontent", "sidebarcontent", "sidebarcontentbottom", "footnotes", "fullfooter", "subheading", "authornotes", "pronunciation" }
types_uuid = { "id", "worldID", "parentID", "categoryID", "authorID", "folderId" }
types_int = { "likes", "views", "wordcount", "viewCount", "likeCount", "commentCount", "positionX", "positionY", "zoomLevel", "mapWidth", "mapHeight", "mapMarkerWidth", "mapMarkerHeight" }
types_bool = { "isWip", "isDraft", "isAdultContent", "isLocked", "allowComments", "showAuthor", "showLastModified", "showWordCount", "showInSidebar", "showInMap", "isPinned", "isFeatured", "isFeaturedArticle", "isPublished", "showInToc", "isEmphasized", "displayAuthor", "displayChildrenUnder", "displayTitle", "displaySheet", "isEditable", "coverIsMap" }
default_fields = { "title", "subheading", "snippet", "excerpt", "pronunciation", "content", "fullfooter", "sidepanelcontenttop", "sidepanelcontent", "sidebarcontentbottom", "sidebarcontent", "footnotes", "authornotes", "scrapbook", "credits", "displayCss" }
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

SPECIAL_LINK_RE = re.compile(r'@\[([^\]]*)\]\([^)]*\)')
BBCODE_NEWLINE_RE = re.compile(r'\[(?:br|hr|/p|p)\s*/?\]', re.IGNORECASE)
BBCODE_HEADLINE_RE = re.compile(r'\[h([1-4])\](.*?)\[/h\1\]', re.IGNORECASE | re.DOTALL)
BBCODE_TAG_RE = re.compile(r'\[/?[a-z*][^\]\n]*\]', re.IGNORECASE)
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


def build_writing_text(jdata):
    parts = []
    for field in writing_fields:
        value = jdata.get(field)
        if isinstance(value, str) and value != "":
            value = value.replace("\r\n", "\n")
            value = SPECIAL_LINK_RE.sub(r'\1', value)
            value = BBCODE_HEADLINE_RE.sub(lambda match: f"{'!' * int(match.group(1))} {match.group(2).strip()}\n\n", value)
            value = BBCODE_NEWLINE_RE.sub("\n", value)
            value = BBCODE_TAG_RE.sub("", value)
            value = WHITESPACE_BEFORE_NEWLINE_RE.sub("\n", value)
            value = EXCESS_BLANK_LINES_RE.sub("\n\n", value).strip()
            if value != "":
                parts.append(value)
    return "\n\n".join(parts)


def write_writing_file(base_folder, jdata):
    entity_class = sanitize_filename_component(jdata.get("entityClass", ""))
    slug = sanitize_filename_component(jdata.get("slug", ""))
    if entity_class in {"", ".", ".."} or slug in {"", ".", ".."}:
        return False
    content = build_writing_text(jdata)
    if len(content.encode()) < 100:
        return False

    target_folder = Path(base_folder) / "writing" / entity_class
    ensure_dir(target_folder)
    target_file = target_folder / f"{slug}.txt"
    write_text(target_file, content)
    print(f"Writing export: {target_file.as_posix()}")
    return True


def load_latest_articles(json_folder):
    return [item[0] for item in load_latest_json_by_slug(json_folder).values()]


def is_published_writing_article(jdata):
    return jdata.get("state") == "public"


# main
chdir_to_script_dir(__file__)

parser = ArgumentParser()
parser.add_argument('filename', nargs='?', help="article json file name, it will be looked for in the world/json folder")
parser.add_argument("-f", "--fields", required=False, help="fields to extract, separated by commas, default: " + ",".join(str(x) for x in default_fields))
parser.add_argument("-l", "--list", required=False, action='store_true', help="list fields found in the json file, default: only strings")
parser.add_argument("-a", "--all", required=False, action='store_true', help="-l will list ALL fields found in the json file, not just strings")
parser.add_argument("-t", "--types", required=False, action='store_true', help="-l will display the type of each field found")
parser.add_argument("-e", "--empty", required=False, action='store_true', help="create files for empty fields, too")
parser.add_argument("-w", "--writing", required=False, action='store_true', help="extract writing fields into writing/<entityClass>/<slug>.txt")
args = parser.parse_args()
cfg = load_cfg_or_exit("settings.cfg")
world_name = cfg['world_name']
world_id = cfg['world_id']
paths = world_paths(world_name)
json_folder = paths["json"]
output_folder = paths["edit"]

# create the writing folder if it doesn't exist
if args.writing:
    try:
        ensure_dir(paths["writing"])
    except OSError as error:
        print(f"Cannot create folder {world_name + '/writing'}: {error}")
        raise SystemExit(1)

# create the extract folder if it doesn't exist
try:
    ensure_dir(output_folder)
except OSError as error:
    print(f"Cannot create folder {output_folder}: {error}")
    raise SystemExit(1)

if args.writing and args.all:
    for jdata in load_latest_articles(json_folder):
        if is_published_writing_article(jdata):
            write_writing_file(world_name, jdata)
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

    if args.writing:
        if not is_published_writing_article(jdata):
            raise SystemExit(0)
        if not write_writing_file(world_name, jdata):
            print("Could not write writing export: missing or invalid entityClass/slug.")
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
