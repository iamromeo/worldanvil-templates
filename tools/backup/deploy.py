#!/usr/bin/python3
version = "Tillerz Article Deploy"

from argparse import ArgumentParser
import json
from pathlib import Path
import requests
from wa_common import (
    build_api_url,
    build_request_headers,
    chdir_to_script_dir,
    fetch_article,
    load_cfg_or_exit,
    patch_article,
    read_json,
    world_paths,
)

# main
chdir_to_script_dir(__file__)

parser = ArgumentParser()
parser.add_argument(
    "--dry-run",
    action="store_true",
    help="validate deploy payloads and print what would be sent, but do not PATCH",
)
parser.add_argument(
    "--validate",
    action="store_true",
    help="after PATCH, fetch article and verify uploaded fields match server data",
)
args = parser.parse_args()

cfg = load_cfg_or_exit("settings.cfg")
world_name = cfg["world_name"]
deploy_folder = world_paths(world_name, cfg.get('root_folder'))["deploy"]
if not deploy_folder.is_dir():
    print(f"Deploy folder not found: {deploy_folder.as_posix()}")
    raise SystemExit(1)

payload_files = sorted(deploy_folder.glob("*.json"))
if not payload_files:
    print(f"No deploy files found in {deploy_folder.as_posix()}")
    raise SystemExit(0)

api_url = build_api_url(cfg)
request_headers = build_request_headers(cfg, version)

print(f"Deploy folder: {deploy_folder.as_posix()}")
print(f"Deploy files found: {len(payload_files)}")
print(f"Mode: {'dry-run' if args.dry_run else 'live'}")
print(f"Validate: {'on' if args.validate else 'off'}")

deployable_count = 0
deployed_count = 0
validated_count = 0
validation_failed_count = 0
with requests.Session() as session:
    for file_path in payload_files:
        try:
            payload = read_json(file_path)
        except json.JSONDecodeError as error:
            print(f"Skipping {file_path.name}: invalid JSON ({error})")
            continue

        article_id = payload.get("id")
        if not article_id:
            print(f"Skipping {file_path.name}: missing required field 'id'")
            continue
        if len(payload.keys()) <= 1:
            print(f"Skipping {file_path.name}: no changed fields in payload")
            continue

        deployable_count += 1
        changed_fields = [key for key in payload.keys() if key != "id"]
        print(f"Prepared: {file_path.name} -> article {article_id}")
        print(f"Fields: {', '.join(changed_fields)}")

        update_article = api_url + "article?id=" + article_id
        update_payload = {key: value for key, value in payload.items() if key != "id"}
        if args.dry_run:
            print(f"Dry-run: PATCH {update_article}")
            continue

        try:
            patch_article(
                session,
                api_url,
                article_id,
                update_payload,
                request_headers,
                timeout=60,
            )
            deployed_count += 1
            print(f"Deployed: {file_path.name}")

            if args.validate:
                server_article = fetch_article(
                    session, api_url, article_id, request_headers, granularity=3
                )
                mismatches = []
                for field, expected_value in update_payload.items():
                    server_value = server_article.get(field)
                    # WA may normalize empty text to null.
                    if expected_value == "" and server_value is None:
                        continue
                    if server_value != expected_value:
                        mismatches.append(field)

                if mismatches:
                    validation_failed_count += 1
                    print(
                        f"Validation failed for {file_path.name}: mismatched fields: "
                        + ", ".join(mismatches)
                    )
                else:
                    validated_count += 1
                    print(f"Validated: {file_path.name}")
        except requests.RequestException as error:
            print(f"Deploy failed for {file_path.name}: {error}")

print(f"Deployable payloads: {deployable_count}")
print(f"Deployed payloads: {deployed_count}")
if args.validate and not args.dry_run:
    print(f"Validated payloads: {validated_count}")
    print(f"Validation failures: {validation_failed_count}")
