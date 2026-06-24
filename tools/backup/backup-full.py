#!/usr/bin/python3
version = 'Tillerz Full Article Backup'

# --- requirements ----------------------------------------------------
# see https://github.com/Tillerz/worldanvil-templates/blob/master/tools/backup/

from bs4 import BeautifulSoup
from collections import deque
import json
from pathlib import Path
import requests
from requests.utils import dict_from_cookiejar
from requests.utils import cookiejar_from_dict
from sys import platform
import time
from wa_common import (
    build_api_url,
    build_request_headers,
    chdir_to_script_dir,
    ensure_dir,
    fetch_article,
    fetch_article_list_page,
    load_cfg_or_exit,
    read_text,
    world_paths,
    write_json,
)

# main
chdir_to_script_dir(__file__)

file_cookies = "cookies.json"
cfg = load_cfg_or_exit("settings.cfg")
world_name = cfg['world_name']
world_id = cfg['world_id']
request_headers = build_request_headers(cfg, version)
api_url = build_api_url(cfg)
paths = world_paths(world_name)

# this is the root folder for the backup:
root_folder = paths["root"]
root_folder_json = paths["json"]
file_all_articles_new = root_folder / "all_articles_new.json"
file_all_articles_old = root_folder / "all_articles_old.json"
file_all_articles = root_folder / "all_articles.json"

# create a backup folder if it doesn't exist
try:
    ensure_dir(root_folder)
except OSError as error:
    print(f"Cannot create folder {world_name}: {error}")
    raise SystemExit(1)

# --- action starts here ---------------------------------------------------

# create a session
with requests.Session() as session:
    if Path(file_cookies).is_file():
        # load the saved cookies
        cookies = json.loads(read_text(file_cookies))
        # turn the object into a a cookie jar
        cookies = cookiejar_from_dict(cookies)
        # attach cookies to session
        session.cookies.update(cookies)

    # global timer
    loop_start = time.monotonic()

    # read article list
    pagesize = 50
    all_articles_new = []
    try:
        offset = 0
        request_times = deque(maxlen=5)
        # fetch <pagesize> article, add them to the list and then increase offset for next <pagesize> articles
        counter = 0
        while True:
            if len(request_times) == request_times.maxlen:
                elapsed = time.monotonic() - request_times[0]
                if elapsed < 5:
                    time.sleep(5 - elapsed)
            request_times.append(time.monotonic())
            jdata = fetch_article_list_page(
                session,
                api_url,
                world_id,
                request_headers,
                limit=pagesize,
                offset=offset,
            )
            if jdata.get("success") is True:
                if jdata.get("entities") == []:
                    break
                else:
                    all_articles_new.extend(jdata.get("entities", []))
                    offset += pagesize
                    print(f"article list offset {counter} read ({counter * pagesize}+)")
                    counter += 1
            else:
                break
    except requests.RequestException as e:
        print(f"Error fetching article list: {e}")
        raise SystemExit(1)

    if not all_articles_new:
        print("Error: No articles returned from API.")
        raise SystemExit(1)

    print("Comparing list of existing articles with downloaded list.")
    # load old article list, if existing
    if file_all_articles.exists():
        all_articles_old = json.loads(read_text(file_all_articles))
    else:
        all_articles_old = []

    write_json(file_all_articles_new, all_articles_new, compact=True)

    old_dates_by_id = {
        a.get("id"): a.get("updateDate", {}).get("date")
        for a in all_articles_old
        if "id" in a
    }
    updated_count = 0
    unchanged_count = 0
    new_articles = []
    for a in all_articles_new:
        article_id = a.get("id")
        if article_id is None:
            continue
        old_date = old_dates_by_id.get(article_id)
        new_date = a.get("updateDate", {}).get("date")
        if old_date is None or (new_date is not None and new_date > old_date):
            new_articles.append(article_id)
        else:
            unchanged_count += 1
    # debug: Path("new_articles.json").write_text(json.dumps(new_articles, separators=(",", ":")))

    request_times = deque(maxlen=5)
    # loop over all new or changed articles
    remaining = len(new_articles)
    for article_id in new_articles:
        if len(request_times) == request_times.maxlen:
            elapsed = time.monotonic() - request_times[0]
            if elapsed < 5:
                time.sleep(5 - elapsed)
        request_times.append(time.monotonic())
        # fetch article via API with granularity 3, means full article with all fields
        try:
            jdata = fetch_article(
                session, api_url, article_id, request_headers, granularity=3
            )
        except requests.RequestException as e:
            print(f"Error fetching article data: {e}")
            continue

        # parse the json file and extract some values
        length = len(json.dumps(jdata))
        length_old = 0

        slug = jdata["slug"]
        wordcount = jdata["wordcount"]
        last_modif = jdata["updateDate"]["date"]

        # build path + filename to save the json:
        file_json_article_base = root_folder_json / (
            slug + '_' + last_modif.replace(".000000","").replace(' ','_').replace(':','')
        )
        last_modif_old = ""
        old_wordcount = 0
        diff = 0
        perc = 100
        wdiff = ""

        # if the file already exists, load it and extract some values for comparison with the new downloaded version
        article_json_path = file_json_article_base.with_suffix('.json')
        if article_json_path.is_file():
            oldfile = read_text(article_json_path)

            length_old = len(oldfile)
            olddata = json.loads(oldfile)
            old_wordcount = olddata["wordcount"]
            last_modif_old = olddata["updateDate"]["date"]

            if (old_wordcount > 0):
                perc = wordcount * 100 / old_wordcount

            if (old_wordcount > 0):
                diff = wordcount - old_wordcount
                if (diff >= 0):
                    wdiff = "+" + str(diff)
                wdiff = "("+str(wdiff)+", "+str(round(perc))+"% of previous size)"
        # do not save new article if it is unchanged
        if ((last_modif_old == last_modif) and (diff == 0) and (length == length_old)):
            print(f'SLUG: {slug} --> file did not change, not saving.')
            unchanged_count += 1
        else:
            # print some output for the user
            print(f'SLUG: {slug} ({article_id})')
            print(f'Last Modified: {last_modif.replace(".000000","")}')
            print(f'Wordcount: {wordcount} {wdiff}')

            # write the json file to disk
            print(f'Writing file to {article_json_path}')
            write_json(article_json_path, jdata)
            updated_count += 1

            # for debug: print(json.dumps(response.json(), indent=2))
        remaining -= 1
        print(f'------------------------ {remaining}')

    if updated_count == 0:
        print(f"{unchanged_count} articles were already up-to-date.")
        if file_all_articles_new.is_file():
            file_all_articles_new.unlink()
    else:
        print(f"Updated {updated_count} articles, {unchanged_count} articles were already up-to-date.")
        if file_all_articles_old.is_file():
            file_all_articles_old.unlink()
        if file_all_articles.is_file():
            file_all_articles.replace(file_all_articles_old)
        if file_all_articles_new.is_file():
            file_all_articles_new.replace(file_all_articles)

    elapsed = int(time.monotonic() - loop_start)
    minutes, seconds = divmod(elapsed, 60)
    print(f"Elapsed time: {minutes}m {seconds:02d}s")

    # turn cookiejar into dict and save it
    cookies = dict_from_cookiejar(session.cookies)
    if Path(file_cookies).is_file():
        if session.cookies:
            cookies = dict_from_cookiejar(session.cookies)
        else:
            cookies = {}
    write_json(file_cookies, cookies)
