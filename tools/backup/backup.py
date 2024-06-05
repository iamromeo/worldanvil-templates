#!/usr/bin/python3

from bs4 import BeautifulSoup
import requests
import json
import yaml
import os
import datetime

# --- requirements ----------------------------------------------------
# install python 3.x
# install git client
# git clone --depth=2 https://gitlab.com/SoulLink/world-anvil-api-client.git
# pip install bs4
# pip install lxml

# --- adjust here ----------------------------------------------------
# world name, example: alana
world_name = 'YOUR_WORLD_NAME_HERE'
# world id, example: b4c38990-f121-44b9-a966-2c80514ff3d6
world_id = 'YOUR_WORLD_ID_HERE'
api_headers =  {
  "Content-Type" : "application/json",
  "x-auth-token" : "AUTH_TOKEN_HERE_THE_REALLY_REALLY_LONG_ONE",
  "x-application-key" : "APPLICATION_KEY_HERE",
  "User-Agent" : 'Tillerz Article Backup v0.01'
}

# if the new file is down to this percentage of the previous version, then do NOT overwrite but print an error.
# example: 75 = if the file is only 75% of its previous size (or smaller), do not overwrite
overwrite_threshold = 75

# Default: False. If set to True, saved files will be named <slug>-<last_modif>.json, eg. martine-character-2024-06-05_143000.json
# That way you have a fresh copy with each edit.
append_last_modif = False

# --- do not edit below ----------------------------------------------------

# this is the root folder for the backup:
root_folder = world_name

# api and rss urls:
api_url = "https://www.worldanvil.com/api/external/boromir/"
rss_url = requests.get('https://www.worldanvil.com/w/'+world_name+'/opendata/rss')

# create a backup folder if it doesn't exist
try:
    os.mkdir(world_name)
except OSError as error:
    print(f"All good, folder {world_name} already exists.")

soup = BeautifulSoup(rss_url.content, 'xml')
entries = soup.find_all('item')

for i in entries:
  # get data from RSS list
  title = i.title.text
  link = i.link.text
  article_id = i.guid.text
  print(f'Title: {title}\nLink: {link}\nArticle ID: {article_id}')

  # fetch article via API
  get_article = api_url + "article?id=" + article_id
  response = requests.get(get_article, headers=api_headers)
  rc = response.status_code
  if (rc != 200):
    print(f'HTTP Error: {rc}, should be 200.')
  else:
    # parse the json file
    jdata = response.json()
    try:
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
        f = open(filepath+".json", 'r')
        oldfile = f.read()
        f.close()         

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

      if ((last_modif_old == last_modif) and (diff == 0)):
        print("INFO: file didn't change, not saving.")
      else:
        if (perc <= overwrite_threshold):
          print("\n    #### ERROR: not overwriting file, the file did shrink too much! Saving with postfix .NEW\n")
          filepath = filepath + ".NEW"

        # write the json file to disk
        f = open(filepath+".json", "w")
        f.write(json.dumps(response.json()))
        f.close()

        # print(json.dumps(response.json(), indent=2))

    except yaml.YAMLError as exc:
      print(exc)

  print('------------------------')
