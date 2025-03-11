#!/usr/bin/python3

version = 'Tillerz Article Backup v0.04'

from sys import platform
from bs4 import BeautifulSoup
from pathlib import Path
import requests
from requests.utils import dict_from_cookiejar
from requests.utils import cookiejar_from_dict
import json
import yaml
import datetime
import os

# --- requirements ----------------------------------------------------
# see https://github.com/Tillerz/worldanvil-templates/blob/master/tools/backup/

# VS Code (Windows) does not switch to the folder the script is in, so we need to do it ourselves
if platform in ('win32', 'cygwin'):
    os.chdir(os.path.dirname(__file__))

# read the config file
cfg = {}
try:
    with open("settings.cfg", "r") as myfile:
        for line in myfile:
            line = line.strip()
            if not line.startswith("#"):
                name, var = line.partition("=")[::2]
                cfg[name.strip()] = str(var.strip())
except FileNotFoundError:
    print("Error: The settings.cfg file was not found.")
    exit(1)
except IOError:
    print("Error: The settings.cfg file could not be read.")
    exit(1)
world_name = cfg['world_name']
world_id = cfg['world_id']

# if the new file is down to this percentage of the previous version, then do NOT overwrite but print an error.
# example: 75 = if the file is only 75% or smaller of its previous size, do not overwrite
overwrite_threshold = int(cfg['overwrite_threshold'])

# Default: False. If set to True, saved files will be named <slug>_<last_modif>.json, eg. martine-character_2024-06-05_143000.json
# That way you have a fresh copy with each edit.
append_last_modif = cfg['append_last_modif'].lower() in ('true', '1', 't')

# headers for the rss request
headers =  {
    "Content-Type" : "application/json",
    "x-auth-token" : cfg['x_auth_token'],
    "x-application-key" : cfg['x_application_key'],
    "User-Agent" : version,
    "Referer" : 'https://www.worldanvil.com/w/'+world_name
}

# headers for the api requests
api_headers =  {
    "Content-Type" : "application/json",
    "x-auth-token" : cfg['x_auth_token'],
    "x-application-key" : cfg['x_application_key'],
    "User-Agent" : version,
    "Referer" : 'https://www.worldanvil.com/w/'+world_name
}

# api and rss urls:
api_url = "https://www.worldanvil.com/api/external/boromir/"

# this is the root folder for the backup:
root_folder = world_name

# create a backup folder if it doesn't exist
try:
    os.makedirs(world_name, exist_ok=True)
except OSError as error:
    print(f"Cannot create folder {world_name}: "+error)

# --- action starts here ---------------------------------------------------

# create a session
with requests.Session() as session:
    if os.path.isfile("cookies.json"):
        # load the saved cookies
        cookies = json.loads(Path("cookies.json").read_text())
        # turn the object into a a cookie jar
        cookies = cookiejar_from_dict(cookies)
        # attach cookies to session
        session.cookies.update(cookies)

    try:
        # load the rss data
        rss_response = session.get('https://www.worldanvil.com/w/'+world_name+'/opendata/rss', headers=api_headers)
        rss_response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching RSS data: {e}")
        exit(1)

    # grab rss content
    soup = BeautifulSoup(rss_response.content, 'xml')

    # save rss data for debug purposes
    Path("dump.rss").write_text(soup.prettify())

    # find all entries in the xml data
    entries = soup.find_all('item')

    for i in entries:
        # get data from RSS list
        title = i.title.text
        link = i.link.text
        article_id = i.guid.text
        print(f'Title: {title}\nLink: {link}\nArticle ID: {article_id}')

        # fetch article via API
        get_article = api_url + "article?id=" + article_id + "&granularity=3"
        try:
            response = session.get(get_article, headers=api_headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching article data: {e}")
            continue

        # parse the json file
        jdata = response.json()
        length = len(json.dumps(jdata))
        length_old = 0

        slug = jdata["slug"]
        wordcount = jdata["wordcount"]
        last_modif = jdata["updateDate"]["date"]

        # path and filename to save the json:
        filepath = root_folder+"/"+slug
        if (append_last_modif):
            filepath = filepath + "_" + last_modif.replace(".000000","").replace(' ','_').replace(':','')

        last_modif_old = ""
        old_wordcount = 0
        perc = 100
        wdiff = ""

        if os.path.isfile(filepath+".json"):
            oldfile = Path(filepath+".json").read_text()

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

            print(f'SLUG: {slug}')
            print(f'Last Modified: {last_modif.replace(".000000","")}')
            print(f'Wordcount: {wordcount} {wdiff}')

        if ((last_modif_old == last_modif) and (diff == 0) and length <= length_old):
            print("INFO: file didn't change, not saving.")
        else:
            if (perc <= overwrite_threshold):
                print("\n    #### ERROR: not overwriting file, the file did shrink too much! Saving with postfix .NEW\n")
                filepath = filepath + ".NEW"

            # write the json file to disk
            print(f'Writing file to {filepath}.json')
            Path(filepath+".json").write_text(json.dumps(jdata))

            # print(json.dumps(response.json(), indent=2))
        print('------------------------')

    # turn cookiejar into dict and save them
    cookies = dict_from_cookiejar(session.cookies)
    if os.path.isfile("cookies.json"):
        if session.cookies:
            cookies = dict_from_cookiejar(session.cookies)
        else:
            cookies = {}
    Path("cookies.json").write_text(json.dumps(cookies))
