
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

```python
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
```

You can also configure to not overwrite an existing backup if the World Anvil copy is smaller. It then will append .NEW to the new version and save it besides the already existing article. A previous .NEW file will be overwritten.

```python
# if the new file is down to this percentage of the previous version, then do NOT overwrite but print an error.
# example: 75 = if the file is only 75% of its previous size (or smaller), do not overwrite
overwrite_threshold = 75
```
