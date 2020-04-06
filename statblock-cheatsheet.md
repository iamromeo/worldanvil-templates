# RPG Statblocks Cheatsheet
Date | Revision | author | comment 
------------ | ------------- | ------------- | -------------
2019 | 2.0 | [GorkamWorka](https://github.com/GorkamWorka) | update to reflect block-system-2.0
2018 | 1.0 | [GorkamWorka](https://github.com/GorkamWorka) | initial commit

## Template Structure

Each block **MUST** include : 
- a display template => a twig file defining how the data stored in the block is displayed.
  - a default for this can be found on the right sidebar in block builder "display" tab under "Boilerplate Template"

Each block **MAY**  include :
- a YAML file defining variables stored in the block. (this is an automation of the "parts" tab of the block builder) 
- a CSS file => css file containing styling for the block
- a badge template => a twig file defining the "badge" (a compact small summary of the block) for the block.
- a trackable template => a twig form template defining an editable or partially editable 

## References
Templates are made using :
- [Twig Documentation](https://twig.symfony.com/doc/2.x/)
- [bootstrap 4 Documentation](http://getbootstrap.com/docs/4.0/)
- [html Documentation](https://www.w3schools.com/Html/)

YAML data model : 
- [YAML Documentation](http://yaml.org/)

CSS files :
- [CSS Documentation](https://www.w3schools.com/css/)

## The YAML File
If you have any questions join us on our discord https://www.worldanvil.com/discord and use the channel #custom-articles-and-statblocks-help.  

If you are planning to create your own form and you will not rely on automatic form generation the only thing you need for each of the fields is an entry with the label and input: string
```yaml
vehicle_class
 input: string
 label: "Vehicle Class"
 ```
 _**Notes**_
 1) To properly name the field always use the "label" property
 2) Do not use a field name called "name". This is always automatically addded. 

### Reference
#### Input types
- string
- integer
- select
- text
- checkbox

#### Renderers
use property "render"
- image (input: integer _note: accepts ID of an image_)
- table (input: text _note: this is a | separated CSV_)
- random (input: text _note: this is a | separated CSV_)
- list (input: text _note: this is a key value list (on each line: key|value)_ )
 
#### Example 
```yaml
fields:
  level: 
    input: integer
    label: "Level"
    placeholder: "2"
    min: 1
    max: 9
  type:
    input: select
    label: "Item Type"
    required: true
    options: 
      Adventuring Gear: Adventuring Gear
      Ammunition: Ammunition
      Armor: Armor
      Artisan Tool: Artisan Tool
      Explosive: Explosive
      Firearm: Firearm
      Futuristic: Futuristic
      Gaming Set: Gaming Set
      Generic Variant: Generic Variant
      Instrument: Instrument
      Modern: Modern
      Mount: Mount
      Poison: Poison
      Potion: Potion
      Renaissance: Renaissance
      Ring: Ring
      Rod: Rod
      Scroll: Scroll
      Spellcasting Focus: Spellcasting Focus
      Staff: Staff
      Tack and Harness: Tack and Harness
      Tool: Tool
      Trade Good: Trade Good
      Vehicle: Vehicle
      Wand: Wand
      Weapon: Weapon
      Wondrous Item: Wondrous Item
  attunement:
    input: text
    rows: 3
    description: "Item's magical attunement"
    label: "Attunement"
    placeholder: "Abjuration"
  needsattunement:
    input: checkbox
    label: "Items needs Attunement"
  attunement:
    input: text
    rows: 3
    description: "Item's magical attunement"
    label: "Attunement Requirements"
    placeholder: "Abjuration"
  properties:
    input: text
    rows: 6
    description: "Item properties"
    label: "Properties"
    placeholder: "Magical, Heavy, Cursed, Light, Versatile"
  armortype:
    input: select
    description: "Armor subtype if the item is an armor"
    label: "Armor Type"
    options:
      None: None
      Light: Light
      Medium: Medium
      Heavy: Heavy
      Shield: Shield
  ac:
    input: string
    description: "Armor Class if the item is an armor"
    label: "Armor Class (AC)"
    placeholder: 14
  strengthrequirement:
    input: string
    description: "Strength Required if the item is an armor"
    label: "Strength Requirement"
    placeholder: 12+
  stealthdisadvantage:
    input: checkbox
    description: "Check if the armor confers a stealth check disadvantage"
    label: "Stealth Disadvantage?"
  weapontype:
    input: select
    description: "Weapon subtype if the item is a weapon"
    label: "Weapon Subtype"
    options:
      None: None
      Simple Melee: Simple Melee
      Martial Melee: Martial Melee
      Simple Ranged: Simple Ranged
      Martial Ranged: Martial Ranged
  damage:
    input: string
    description: "Damage dealt by item, if the item is a weapon"
    label: "Weapon Damage"
    placeholder: "1d8+4"
  secondarydamage:
    input: string
    description: "Secondary or Versatile property Damage dealt by item, if the item is a weapon"
    label: "Weapon Secondary Damage"
    placeholder: "1d8+4"
  damagetype:
    input: select
    description: "Weapon damage type if the item is a weapon"
    label: "Weapon Damage Type"
    options:
      None: None
      Bludgeoning: Bludgeoning
      Slashing: Slashing
      Piercing: Piercing
      Acid: Acid
      Cold: Cold
      Fire: Fire
      Force: Force
      Lightning: Lightning
      Necrotic: Necrotic
      Poison: Poison
      Psychic: Psychic
      Radiant: Radiant
      Thunder: Thunder
      Non-magical: Non-magical
      Silver: Silver
      Adamantine: Adamantine
  range:
    input: string
    description: "How far does it shoot, if the item is a weapon"
    label: "Weapon Range"
    placeholder: "30/60 ft"
  description:
    input: text
    rows: 10
    description: "Item physical description and abilities"
    label: "Description"
  rarity:
    input: select
    description: "How rare is the item"
    label: "Rarity"
    options: 
      Varies: Varies
      Common: Common
      Uncommon: Uncommon
      Rare: Rare
      Very Rare: Very Rare
      Legendary: Legendary
  cost:
    input: string
    label: "Price"
    placeholder: "3gp 5sp"
  weight:
    input: string
    label: "Weight"
    placeholder: "5lb"
  level: 
    input: integer
    label: "Level"
    placeholder: "2"
    min: 1
    max: 9
  source:
    input: string
    label: "Source"
    placeholder: "DnD 5e SRD or World of X, X marks your world!"
    description: "Where can this be found, in anywhere else"
  image:
    input: integer
    render: image
    description: "paste here the ID of the image you want to be used as the image of the item"
    label: "Image Gallery ID"
    placeholder: "123"
```
 
## The HTML Template
- [Bootstrap4 Grid-System](https://getbootstrap.com/docs/4.0/layout/grid/): **READ THIS !** you'll need it trust me.


_//-- Contribution needed --//_
## The CSS File

_//-- Contribution needed --//_
