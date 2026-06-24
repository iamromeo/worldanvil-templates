#!/usr/bin/python3
version = "Tillerz Tag Manager"

from argparse import ArgumentParser
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Optional

from wa_common import (
    chdir_to_script_dir,
    ensure_dir,
    format_tags,
    load_cfg_or_exit,
    load_latest_json_by_slug,
    parse_tags,
    sanitize_filename_component,
    unique_preserve_order,
    validate_single_comma_free_tag,
    world_paths,
    read_json,
    write_json,
)


@dataclass
class ArticleRecord:
    slug: str
    title: str
    article_id: str
    entity_class: str
    source_path: Path
    update_date: Optional[datetime]
    source_tags: list[str]


def is_type_match(record, entity_type):
    if entity_type is None:
        return True
    return (record.entity_class or "").casefold() == entity_type.casefold()


def load_articles(json_folder):
    latest_by_slug = {}
    for slug, (data, path, update_date, _source_mtime) in load_latest_json_by_slug(
        json_folder, require_article_id=True
    ).items():
        article_id = data["id"]
        entity_class = data.get("entityClass")
        if not isinstance(entity_class, str):
            entity_class = ""

        source_tags = unique_preserve_order(parse_tags(data.get("tags")))

        latest_by_slug[slug] = ArticleRecord(
            slug=slug,
            title=data.get("title") if isinstance(data.get("title"), str) else "",
            article_id=article_id,
            entity_class=entity_class,
            source_path=path,
            update_date=update_date,
            source_tags=source_tags,
        )

    return dict(sorted(latest_by_slug.items(), key=lambda item: item[0]))


def load_existing_payload(deploy_path):
    if not deploy_path.is_file():
        return {}
    data = read_json(deploy_path)
    if not isinstance(data, dict):
        raise ValueError(f"Deploy file is not a JSON object: {deploy_path.as_posix()}")
    return data


def effective_tags_for_article(record, deploy_folder):
    deploy_path = deploy_folder / f"{record.slug}.json"
    payload = load_existing_payload(deploy_path)
    if "tags" in payload:
        return unique_preserve_order(parse_tags(payload.get("tags")))
    return list(record.source_tags)


def write_article_deploy(record, deploy_folder, tags):
    ensure_dir(deploy_folder)
    deploy_path = deploy_folder / f"{record.slug}.json"
    payload = load_existing_payload(deploy_path)

    existing_id = payload.get("id")
    if existing_id is not None and existing_id != record.article_id:
        raise ValueError(
            f"Deploy file id mismatch for slug '{record.slug}': {existing_id} != {record.article_id}"
        )

    payload["id"] = record.article_id
    payload["tags"] = format_tags(tags)

    write_json(deploy_path, payload, indent=2)
    return deploy_path


def find_article(articles_by_slug, slug):
    sanitized = sanitize_filename_component(slug)
    return articles_by_slug.get(sanitized) or articles_by_slug.get(slug)


def command_stats(records):
    tags_per_article = [record.source_tags for record in records]
    with_tags = [tags for tags in tags_per_article if tags]
    without_tags = len(tags_per_article) - len(with_tags)

    counts = Counter()
    for tags in with_tags:
        counts.update(tags)

    for tag in sorted(counts.keys(), key=lambda value: value.casefold()):
        print(f"{tag}: {counts[tag]}")

    print("---")
    print(f"articles with tags: {len(with_tags)}")
    print(f"articles with no tags: {without_tags}")

    average = 0.0
    if with_tags:
        average = sum(len(tags) for tags in with_tags) / len(with_tags)
    print(f"average tags per tagged article: {average:.2f}")


def command_tags(record):
    if not record.source_tags:
        print("(no tags)")
        return
    for tag in record.source_tags:
        print(tag)


def command_articles(records, required_tags):
    hits = []
    required = set(required_tags)
    for record in records:
        article_tag_set = set(record.source_tags)
        if required.issubset(article_tag_set):
            hits.append(record)

    for record in hits:
        print(f"{record.slug} | {record.title}")

    print(f"matches: {len(hits)}")


def apply_replace(tags, old_tag, new_tag):
    changed = False
    output = []
    for tag in tags:
        if tag == old_tag:
            output.append(new_tag)
            changed = True
        else:
            output.append(tag)
    output = unique_preserve_order(output)
    return output, changed


def apply_add(tags, add_tags):
    result = list(tags)
    changed = False
    for tag in add_tags:
        if tag not in result:
            result.append(tag)
            changed = True
    return result, changed


def apply_remove(tags, remove_tags):
    remove_set = set(remove_tags)
    result = [tag for tag in tags if tag not in remove_set]
    return result, result != tags


def command_bulk_update(records, deploy_folder, update_fn, dry_run=False):
    changed = 0
    unchanged = 0
    for record in records:
        current_tags = effective_tags_for_article(record, deploy_folder)
        new_tags, did_change = update_fn(current_tags)
        if not did_change:
            unchanged += 1
            continue
        if dry_run:
            print(f"would update: {record.slug}")
        else:
            write_article_deploy(record, deploy_folder, new_tags)
            print(f"updated: {record.slug}")
        changed += 1
    if dry_run:
        print(f"would change: {changed}")
    else:
        print(f"changed: {changed}")
    print(f"unchanged: {unchanged}")


def parse_tag_list(raw):
    values = parse_tags(raw)
    values = unique_preserve_order(values)
    return values


def parse_operation(args):
    ops = []
    if args.stats:
        ops.append("stats")
    if args.tags is not None:
        ops.append("tags")
    if args.articles is not None:
        ops.append("articles")
    if args.replace is not None:
        ops.append("replace")
    if args.add is not None:
        ops.append("add")
    if args.remove is not None:
        ops.append("remove")

    if len(ops) != 1:
        raise ValueError("Exactly one operation must be provided.")
    return ops[0]


# main
chdir_to_script_dir(__file__)

parser = ArgumentParser()
parser.add_argument("--stats", action="store_true", help="list tag statistics")
parser.add_argument("--tags", metavar="article_slug", help="list tags of one article")
parser.add_argument("--articles", metavar="tag_list", help="list articles matching all tags")
parser.add_argument("--replace", nargs="+", help="replace tag: with --all use '<old> <new>', without --all use '<old> <new> <article-slug>'")
parser.add_argument("--add", nargs="+", metavar=("tag_list", "article_slug"), help="add tags: with --all use '<tag_list>', without --all use '<tag_list> <article-slug>'")
parser.add_argument("--remove", nargs="+", metavar=("tag_list", "target"), help="remove tags: with --all use '<tag_list>', without --all use '<tag_list> <article-slug>'")
parser.add_argument("--all", action="store_true", help="apply add/replace/remove to all matching articles")
parser.add_argument("--dry-run", action="store_true", help="show planned changes for add/replace/remove without writing deploy files")
parser.add_argument("--type", dest="entity_type", help="optional entity class filter for non-single-article operations")
argv = sys.argv[1:]

# Support user-friendly forms:
#   --replace --all <old> <new>
#   --add --all <tag list>
#   --remove --all <tag list>
for option_name in ("--replace", "--add", "--remove"):
    if option_name in argv:
        index = argv.index(option_name)
        if index + 1 < len(argv) and argv[index + 1] == "--all":
            del argv[index + 1]
            if "--all" not in argv:
                argv.insert(0, "--all")

args = parser.parse_args(argv)

cfg = load_cfg_or_exit("settings.cfg")
world_name = cfg["world_name"]
paths = world_paths(world_name, cfg.get('root_folder'))
json_folder = paths["json"]
deploy_folder = paths["deploy"]

if not json_folder.is_dir():
    print(f"JSON folder not found: {json_folder.as_posix()}")
    raise SystemExit(1)

try:
    operation = parse_operation(args)
except ValueError as error:
    print(f"Error: {error}")
    raise SystemExit(1)
if args.all and operation not in {"add", "replace", "remove"}:
    print("Error: --all can only be used together with --add, --replace, or --remove.")
    raise SystemExit(1)
if args.dry_run and operation not in {"add", "replace", "remove"}:
    print("Error: --dry-run can only be used together with --add, --replace, or --remove.")
    raise SystemExit(1)

articles_by_slug = load_articles(json_folder)
if not articles_by_slug:
    print(f"No article json files found in {json_folder.as_posix()}")
    raise SystemExit(1)

if operation == "stats":
    records = [record for record in articles_by_slug.values() if is_type_match(record, args.entity_type)]
    command_stats(records)
    raise SystemExit(0)

if operation == "tags":
    if args.entity_type is not None:
        print("Error: --type can only be used for operations that do not target a single article.")
        raise SystemExit(1)
    record = find_article(articles_by_slug, args.tags)
    if record is None:
        print(f"Article not found for slug: {args.tags}")
        raise SystemExit(1)
    command_tags(record)
    raise SystemExit(0)

if operation == "articles":
    required_tags = parse_tag_list(args.articles)
    if not required_tags:
        print("Error: tag list is empty.")
        raise SystemExit(1)
    records = [record for record in articles_by_slug.values() if is_type_match(record, args.entity_type)]
    command_articles(records, required_tags)
    raise SystemExit(0)

if operation == "replace":
    values = args.replace
    if args.all:
        if len(values) != 2:
            print("Error: with --replace --all, provide exactly '<old> <new>'.")
            raise SystemExit(1)
        if args.entity_type is None:
            filtered = list(articles_by_slug.values())
        else:
            filtered = [record for record in articles_by_slug.values() if is_type_match(record, args.entity_type)]

        old_tag = values[0]
        new_tag = values[1]
        validate_single_comma_free_tag(old_tag, "old tag")
        validate_single_comma_free_tag(new_tag, "new tag")

        command_bulk_update(
            filtered,
            deploy_folder,
            lambda tags: apply_replace(tags, old_tag, new_tag),
            dry_run=args.dry_run,
        )
        raise SystemExit(0)

    if len(values) == 3:
        if args.entity_type is not None:
            print("Error: --type can only be used for operations that do not target a single article.")
            raise SystemExit(1)
        old_tag, new_tag, article_slug = values
        validate_single_comma_free_tag(old_tag, "old tag")
        validate_single_comma_free_tag(new_tag, "new tag")

        record = find_article(articles_by_slug, article_slug)
        if record is None:
            print(f"Article not found for slug: {article_slug}")
            raise SystemExit(1)

        current_tags = effective_tags_for_article(record, deploy_folder)
        new_tags, changed = apply_replace(current_tags, old_tag, new_tag)
        if not changed:
            print("No changes needed.")
            raise SystemExit(0)

        output = deploy_folder / f"{record.slug}.json"
        if args.dry_run:
            print(f"would update: {record.slug}")
            print(f"deploy file: {output.as_posix()}")
        else:
            output = write_article_deploy(record, deploy_folder, new_tags)
            print(f"updated: {record.slug}")
            print(f"deploy file: {output.as_posix()}")
        raise SystemExit(0)

    print("Error: --replace expects either '--replace --all <old> <new>' or '--replace <old> <new> <article-slug>'.")
    raise SystemExit(1)

if operation == "add":
    values = args.add
    if args.all:
        if len(values) != 1:
            print("Error: with --add --all, provide exactly '<tag list>'.")
            raise SystemExit(1)
        add_tags = parse_tag_list(values[0])
        if not add_tags:
            print("Error: tag list is empty.")
            raise SystemExit(1)
        if args.entity_type is None:
            filtered = list(articles_by_slug.values())
        else:
            filtered = [record for record in articles_by_slug.values() if is_type_match(record, args.entity_type)]
        command_bulk_update(
            filtered,
            deploy_folder,
            lambda tags: apply_add(tags, add_tags),
            dry_run=args.dry_run,
        )
        raise SystemExit(0)

    if len(values) != 2:
        print("Error: --add expects either '--add --all <tag list>' or '--add <tag list> <article-slug>'.")
        raise SystemExit(1)
    if args.entity_type is not None:
        print("Error: --type can only be used for operations that do not target a single article.")
        raise SystemExit(1)

    raw_tags, article_slug = values
    add_tags = parse_tag_list(raw_tags)
    if not add_tags:
        print("Error: tag list is empty.")
        raise SystemExit(1)

    record = find_article(articles_by_slug, article_slug)
    if record is None:
        print(f"Article not found for slug: {article_slug}")
        raise SystemExit(1)

    current_tags = effective_tags_for_article(record, deploy_folder)
    new_tags, changed = apply_add(current_tags, add_tags)
    if not changed:
        print("No changes needed.")
        raise SystemExit(0)

    output = deploy_folder / f"{record.slug}.json"
    if args.dry_run:
        print(f"would update: {record.slug}")
        print(f"deploy file: {output.as_posix()}")
    else:
        output = write_article_deploy(record, deploy_folder, new_tags)
        print(f"updated: {record.slug}")
        print(f"deploy file: {output.as_posix()}")
    raise SystemExit(0)

if operation == "remove":
    values = args.remove
    if args.all:
        if len(values) != 1:
            print("Error: with --remove --all, provide exactly '<tag list>'.")
            raise SystemExit(1)
        remove_tags = parse_tag_list(values[0])
        if not remove_tags:
            print("Error: tag list is empty.")
            raise SystemExit(1)
        if args.entity_type is None:
            filtered = list(articles_by_slug.values())
        else:
            filtered = [record for record in articles_by_slug.values() if is_type_match(record, args.entity_type)]

        command_bulk_update(
            filtered,
            deploy_folder,
            lambda tags: apply_remove(tags, remove_tags),
            dry_run=args.dry_run,
        )
        raise SystemExit(0)

    if len(values) != 2:
        print("Error: --remove expects either '--remove --all <tag list>' or '--remove <tag list> <article-slug>'.")
        raise SystemExit(1)
    raw_tags, target = values
    remove_tags = parse_tag_list(raw_tags)
    if not remove_tags:
        print("Error: tag list is empty.")
        raise SystemExit(1)

    if args.entity_type is not None:
        print("Error: --type can only be used for operations that do not target a single article.")
        raise SystemExit(1)

    record = find_article(articles_by_slug, target)
    if record is None:
        print(f"Article not found for slug: {target}")
        raise SystemExit(1)

    current_tags = effective_tags_for_article(record, deploy_folder)
    new_tags, changed = apply_remove(current_tags, remove_tags)
    if not changed:
        print("No changes needed.")
        raise SystemExit(0)

    output = deploy_folder / f"{record.slug}.json"
    if args.dry_run:
        print(f"would update: {record.slug}")
        print(f"deploy file: {output.as_posix()}")
    else:
        output = write_article_deploy(record, deploy_folder, new_tags)
        print(f"updated: {record.slug}")
        print(f"deploy file: {output.as_posix()}")
    raise SystemExit(0)

print("Error: unsupported operation.")
raise SystemExit(1)
