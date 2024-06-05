
# Backup Script for Articles

Loads the Recent Articles RSS from World Anvil and downloads + saves the JSON file for each, if needed.

The script will create a folder <worldname> and put all the articles in there, naming them <slug>.json, where <slug> is the article SLUG used by WA.

## Requirements

- install python 3.x
- install git client
- git clone --depth=2 https://gitlab.com/SoulLink/world-anvil-api-client.git
- pip install bs4
- pip install lxml

## Configuration

You need to replace the string written in all caps:

world_name = 'YOUR_WORLD_NAME_HERE'
world_id = 'YOUR_WORLD_ID_HERE'
api_headers =  {
  "Content-Type" : "application/json",
  "x-auth-token" : "AUTH_TOKEN_HERE_THE_REALLY_REALLY_LONG_ONE",
  "x-application-key" : "APPLICATION_KEY_HERE",

