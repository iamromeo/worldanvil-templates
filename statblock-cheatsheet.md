# RPG Statblocks Cheatsheet

## Template Structure
Each template requires 
- A YAML file which defines the structure of the form that will be generated and the way that data is stored
- An HTML/TWIG template which defines how the stored data will be displayed on the page
- (optionally) A CSS file which adds styling to the HTML/TWIG template

__If a template doesn't have an HTML file it will automatically show a simple list of its contents as key values. __

## References
Templates are made using :
- [twig](https://twig.symfony.com/doc/2.x/)
- [bootstrap 3](http://getbootstrap.com/docs/3.3/)
- [html](https://www.w3schools.com/Html/)

Yaml data model are made using yml
- [yaml](http://yaml.org/)

Css are made in, well, css :
- [Css](https://www.w3schools.com/css/)

## The YAML File
### Minimum Required enties

```yaml
version: 0.1
system: dnd5e
author: 
  username: WorldAnvil
  email: hello@worldanvil.com
unique_reference: character-dnd5e
name: Character Sheet
display_template: character.html.twig
description: Character sheet for Dungeons and Dragons 5e
instructions: "The character sheet is meant to be used for the NOT trackable resources. Things like Curent HP, XP, Temporary HP, Ammunition, Class Resource, Spells remaining etc. will be tracked and used via the Campaign manager and the Digital Storyteller Screen (DSTS)"
fields:
  name:
    input: string
    label: "Hero name"
    placeholder: "Sir George Honeybadger the 2nd"
    required: true
```

### Allowed Field types

-  String

-  Integer

-  Selection

-  Checkbox

-  Text

-  Image  
  render: image

-  Table (Text variant)  
  render: table

-  List (Text variant)  
  render: list


## The HTML Template
- [Bootstrap3 Grid-System](https://getbootstrap.com/docs/3.3/css/#grid) : **READ THIS !**  
you'll need it trust me.

_//-- Contribution needed --//_
## The CSS File

_//-- Contribution needed --//_
