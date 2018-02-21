# World Anvil RPG Block Templates 
Welcome weary and mighty traveller

This repository is a list of all templates created for World Anvil Role Playing Games blocks. 

## Requirements
- Are you one of those amazing individuals happy to create a template or two, or five for your favorite RPG systems? 
- Do you have some very basic coding knowledge? 
- Do you enjoy the warm fuzzy feeling of having hundreds of people be thankful to you? 
If you have answered yes to at least 2 of the above with YES then you are in the right place! 

----
## Getting started
In order to start working you will need to 
- Know the unique identifier for the system you want to create templates for (for example dnd5e). If you don't know the Identifier of the system you can ask Dimitris (see Getting Help bellow) 
- Read the documentation 
- Have some knowledge of YAML (basic)
- Have some knoeledge of HTML 
- Have some knowledge of CSS (optional)
- Have done some very basic programming (we are talking if else and variables here)

You will need some sort of text editor (I highly recommend SublimeText2 or 3 www.sublimetext.com )

That's all. - _Get started!_

## Getting help
If you are not already there join us at the World Anvil Discord Server and the #coders-anonymous channel
Alternatively you can always ask questions here or mail me directly at dimitris@worldanvil.com 

## DOCUMENTATION 

### Template Structure
Each template requires 
- A YAML file which defines the structure of the form that will be generated and the way that data is stored
- An HTML/TWIG template which defines how the stored data will be displayed on the page
- (optionally) A CSS file which adds styling to the HTML/TWIG template

__If a template doesn't have an HTML file it will automatically show a simple list of its contents as key values. __

### The YAML File
#### Minimum Required enties

```yaml
version: 0.1
system: dnd5e
author: 
  username: WorldAnvil
  email: hello@worldanvil.com
unique_reference: character-dnd5e
name: Character Sheet
description: Character sheet for Dungeons and Dragons 5e
instructions: "The character sheet is meant to be used for the NOT trackable resources. Things like Curent HP, XP, Temporary HP, Ammunition, Class Resource, Spells remaining etc. will be tracked and used via the Campaign manager and the Digital Storyteller Screen (DSTS)"
fields:
  name:
    input: string
    label: "Hero name"
    placeholder: "Sir George Honeybadger the 2nd"
    required: true
```

#### Field types

##### String

##### Integer

##### Selection

##### Checkbox

##### Text

##### Image

##### Table

### The HTML Template

### The CSS File


## Submitting your template


