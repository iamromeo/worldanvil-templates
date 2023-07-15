# Creating a sheet or block for World Anvil

## Preparations

- If you have no python environment on your computer, you can do this online too, using Google Colab:
     - Go here: https://colab.research.google.com/
     - Create a new notebook.
     - A window opens with a triangle arrow in a circle. The input field is a cell, the button is the "Run Cell" button.
     - Copy the content of [gen.py](./gen.py) into the cell at the right side of the Run Cell button.
     - Click the folder icon on the left sidebar to open the data folder.
     - Now follow the steps starting at "Prepare your world for sheets", then go back here and do the missing steps.
     - Drag and drop the schema.yml you created into that data folder on the left.
     - Click the Run Cell button, it should do some stuff and finish with a green checkmark. If it doesn't, something went wrong.
     - Above the data folder on the left is a refresh button. Click it to see the output files.
     - Download the files or directly open them and then use their content on WA as described further down.

## Prepare your world for sheets

- Go to your world, click "Edit World" and then the "Configuration" button and add the system of your choice to your world. Save.
- If the system is not existing yet, contact the DEV team and request a new system. Provide a name and optionally a logo.
- Go to https://www.worldanvil.com/studio/sheets and create a new sheet for your system (right sidebar).
- Give a name and a short description to the sheet. Can be the same, shouldn't be too long. Avoid special characters. Click "Create Template".

## Create the files required

- Create a file schema.yml. That file defines which fields will show up on your sheet. How the yaml file needs to like like you can find [here](../../statblock-cheatsheet.md).
- Enrich your schema.yml with comment lines that define the layout of your sheet, description for that see further below.
- Execute the python script: `python gen.py`, or on Windows click gen.cmd.
- The script creates three files:

### import-to-wa.yml

You can import this file on the 'Parts Configuration Page'. You actually only need to do this if you want to use the tracker sheet.
After importing the YAML file, click "Share with Players" in the sidebar, so that the sheet will be visible to the players in your world.
Then click "Switch to Display Mode".

Note: if you have change the fields in the yaml file later and want to update the PARTS in WA:

- Go to the parts page, scroll all the way down and click "Delete ALL parts on this sheet".
- Then just paste in the content of the updated `import-to-wa.yml`.

### basic-sheet.html.twig

This is the sheet for everyone to view later. Copy the content of the generated `basic-sheet.html.twig` into the input field of the "Basic Sheet" tab.

### edit-form.html.twig

This is the form to fill data into the sheet. Copy the content of the generated `edit-form.html.twig` into the input field of the "Edit Form" tab.

Now add add any CSS you want to use into the input field on the "CSS" tab and click "Save Changes".
That's it, you can already create a first sheet by clicking the big "+" at the top right.

## Tracker

WA actually does not need the PARTS information, you could just use the generated sheet and form and that's it. WA just saves all the fields that are part of the form. Only if you want to use the TRACKER in WA, then you need the Parts in WA.

If you want to create a tracker where the player can save fields that are often changing (hit points, conditions, notes), then just take the form and remove everything except the fields you want to see in the tracker and copy the result into the input field in the "Tracker Sheet" tab and save.

## Badge

The badge is just a really short summary of the character sheet/block, like a name, a class and a level and/or the most vital stats. To make it just take the basic sheet and remove everything you don't want to see in the badge. Copy the result into the input field in the "Badge Sheet" tab and save.

# Script Usage

See a full example in the example/ folder. Possible commands:

## Control commands

```yaml
# include: <filename>
```
Loads the specified file and includes it in the output files.

## Layout
### sheet

```yaml
# sheet: <name of the sheet>
# /sheet
```

This will create the sheet wrapper around the whole sheet with "sheet-name-of-the-sheet" as css class. The yaml file needs to start with # sheet: ... and end with # /sheet.

```html
<div class="container-fluid sheet-name-of-the-sheer">
```

### row

```yaml
# row
# /row
```

Adds a bootstrap row to the sheet.

```html
<div class="row">
</div>
```

### col

```yaml
# col: <col params>
# /col
```

Adds a bootstrap col(umn) to the sheet, col <params> can be "col-12 col-md-6 col-lg 4" for example. A col /col block should always be directly inside a row /row block.

```html
<div class="col params">
</div>
```

### card

```yaml
# card: <class name> [: <card title>]
# /card
```

Adds a bootstab card to the sheet, with "class-name" as css class and a card-header with the given card title. <card title> is optional, if left out, there will be no card header with the title in it.

```html
<div class="card class-name" id="class-name">
    <div class="card-header class-name">card title</div>
</div>
```

### card-body

```yaml
# card-body
# /card-body
```

Adds the card body to the sheet.

```html
<div class="card-body">
</div>
```

For single large text area inside a card body (eg for "Notes"), an additional parameter can enable the 'mention' class to show the formatting buttons for this textarea:

```yaml
# card-body: mention
```

### dots

```yaml
# dots: <number>
```

A string or number field will be interpreted as an integer and displayed as a row of squares. <number> squares will be shown, with the first <value of the variable> ones being filled.

### table

```yaml
# table or # table: horiz or table: horiz: nosplit
# /table
```

Formats the content inbetween as a table instead of using just divs.

Output when using # table

```html
<table class='table'>
    <tr><th class='lbl {{eo}} lbl-name'> Name </th><td class='var {{eo}} var-name'> {{variables.name|default}} </td></tr>
    <tr><th class='lbl {{eo}} lbl-species'> Species </th><td class='var {{eo}} var-species'> {{variables.species|default}} </td></tr>
    <tr><th class='lbl {{eo}} lbl-archetype'> Archetype </th><td class='var {{eo}} var-archetype'> {{variables.archetype|default}} </td></tr>
</table>
```

Output when using # table: horiz

```html
<table class='table'>
    <tr>
        <th class='lbl {{eo}} lbl-name'> Name </th><td class='var {{eo}} var-name'> {{variables.name|default}} </td>
        <th class='lbl {{eo}} lbl-species'> Species </th><td class='var {{eo}} var-species'> {{variables.species|default}} </td>
        <th class='lbl {{eo}} lbl-archetype'> Archetype </th><td class='var {{eo}} var-archetype'> {{variables.archetype|default}} </td>
    </tr>
</table>
```

Default output without usage of # table

```html
<div class='cBox'><div class='lbl lbl-name'> Name </div><div class='var var-name'> {{variables.name|default}} </div></div>
<div class='cBox'><div class='lbl lbl-species'> Species </div><div class='var var-species'> {{variables.species|default}} </div></div>
<div class='cBox'><div class='lbl lbl-archetype'> Archetype </div><div class='var var-archetype'> {{variables.archetype|default}} </div></div>
```

### width

```yaml
# width: <x px| x%>
    fieldname:
        label: fieldname
    ...
```

Defines the with in pixels or percent for the label of the next field. If that field is part of a table+iter list, the width works for the whole column in that table.

## Loops
### iter

```yaml
# iter
# /iter
```

```yaml
# iter: <count>
# /iter
```

```yaml
# iter: <start>: <count>
# /iter
```

Repeats the block inbetween iter and /iter <count> times and also adds _<count> to all variable names. Default for counter is 1..10.
If you give a count value , it is 1..<count>. if you hand over two numbers, it is <start>..<count>.
Output for <count> is two digits with a leading zero, so 01, 02 ... 09, 10, 11 ... Iter can work in tandem with table.
Iter lists also include setting a variable eo that is being used to tag the lines with ev(en) or od(d) class names so you can easily color the lines in two alternating colours etc.

Example input:

```yaml
# table: horiz
    # iter: 15
    item name:
        label: "name"
        input: string
    item weight:
        label: "Weight"
        input: integer
    item stowed:
        label: "Stowed"
        input: checkbox
    # /iter
# /table
```

Example output for iter and table: horiz combination:

```html
    <table class='table'>
    <tr>
    <th class='lbl od lbl-item-name'> Name </th>
    <th class='lbl od lbl-item-weight'> Weight </th>
    <th class='lbl od lbl-item-stowed'> Stowed </th>
    </tr>
    {% for i in 1..15 %}
        {% set id = i %}{% if id < 10 %}{% set id = '0' ~ id %}{% endif %}
        {% set eo = 'od' %}{% if id is even %}{% set eo = 'ev' %}{% endif %}
    <tr>
    <td class='var {{eo}} var-item-name'> {{attribute(variables, 'item_name_' ~ id)|default}} </td><td class='var {{eo}} var-item-weight'>{{attribute(variables, 'item_weight_' ~ id)|default}}</td><td class='var {{eo}} var-item-stowed'>{% if attribute(variables, 'item_stowed_' ~ id)|default|default == 1 %}<i class='fa-regular fa-square-check'></i>{% else %}<i class='fa-regular fa-square'></i>{% endif %}</td>
    </tr>
    {% endfor %}
    </table>
```

Full example for an enriched yaml file below. The indentation of the # comment lines is not necessary, it is just helpful to see which blocks are properly closed.

```yaml
fields:
# sheet: my mini sheet
    # row
        # col: col-12
            # card: personal: Personal Data
                # card-body
                    # table
    name:
        label: "Name"
        input: string
        required: true
        placeholder: "Name of the hero"
    class:
        label: "Class"
        input: select
        options:
            warrior: warrior
            mage: mage
            thief: thief
    level:
        label: "Level"
        input: number
    species:
        label: "Species"
        input: string
    profession:
        label: "Profession"
        input: string
    portrait:
        label: "Portrait"
        input: integer
        render: image
                    # /table
                # /card-body
            # /card
        # /col
    # /row
    # row
        # col: col-12 col-md-4
            # card: brawn
                # card-body
    # dots: 10
    brawn:
        label: "brawn"
        input: string
                # /card-body
            # /card
        # /col
    # dots: 10
        # col: col-12 col-md-4
            # card: agility
                # card-body
    agility:
        label: "agility"
        input: string
                # /card-body
            # /card
        # /col
    # dots: 10
        # col: col-12 col-md-4
            # card: vitality
                # card-body
    vitality:
        label: "vitality"
        input: string
                # /card-body
            # /card
        # /col
    # /row
    # row
        # col: col-12 col-md-6
            # card: belongings: Inventory
                # card-body
                    # table: horiz
                        # iter: 15
    item name:
        label: "item name"
        input: string
    item weight:
        label: "item weight"
        input: integer
    item stowed:
        label: "item stowed"
        input: checkbox
                        # /iter
                    # /table
                # /card-body
            # /card
        # /col
        # col: col-12 col-md-6
            # card: weapons: Weapons
                # card-body
                    # table: horiz: nosplit
                        # iter: 5
    weapon name:
        label: "weapon name"
        input: string
    weapon weight:
        label: "weapon weight"
        input: integer
    weapon stowed:
        label: "weapon stowed"
        input: checkbox
                        # /iter
                    # /table
                # /card-body
            # /card
            # card: armor: Armor
                # card-body
                    # table:
                        # iter: 5
    armor name:
        label: "armor name"
        input: string
    armor weight:
        label: "armor weight"
        input: integer
    armor stowed:
        label: "armor stowed"
        input: checkbox
                        # /iter
                    # /table
                # /card-body
            # /card
        # /col
        # col: col-12
            # card: notes: Character notes 
                # card-body: mention
    notes:
        label: "notes"
        input: text
        rows: 3
                # /card-body
            # /card
        # /col
    # /row
# /sheet
```

End of file. Stop reading here. :D
