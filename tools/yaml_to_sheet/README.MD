# Creating a sheet

- Go to https://www.worldanvil.com/world/<your world>/edit and add the system of your choice to your world. Save.
- If the system is not existing yet, contact the DEV team and request a new system. Provide a name and optionally a logo.
- Go to https://www.worldanvil.com/studio/sheets and create a new sheet for your system (right sidebar)
- Give a name and a short description to the sheet. Can be the same, shouldn't be too long. Avoid special characters. Click "Create Template".
- Create a file schema.yml on your PC as required by the parts importer.
- Import the script to WA using the parts importer.
- Click "Share with Players" in the sidebar, so the sheet will be visible to the players in your world.
- Add comment lines to schema.yml which get parsed by the script and will create the "basic sheet" and the "edit form" code.
- Execute the python script: python gen.py
- In WA, click "Switch to Display Mode".
- Copy the content of the generated basic sheet file into the input field of the "Basic Sheet" tab.
- Copy the content of the generated edit form file into the input field of the "Edit Form" tab.
- Add any CSS you want to use into the field of the "CSS" tab.
- Click "Save Changes".

That's it, now you can already create a first sheet by clicking the big "+" at the top right.

# Script Usage

See a full example in the example/ folder. Possible commands:

## Layout
### sheet

```
# sheet: <name of the sheet>
# /sheet
```

This will create the sheet wrapper around the whole sheet with "sheet-name-of-the-sheet" as css class.

```
<div class="container-fluid sheet-name-of-the-sheer">
```

### row

```
# row
# /row
```

Adds a bootstrap row to the sheet.

```
<div class="row">
</div>
```

### col

```
# col: <col params>
# /col
```

Adds a bootstrap col(umn) to the sheet, <col params> can be "col-12 col-md-6 col-lg 4" for example.

```
<div class="col params">
</div>
```

### card

```
# card: <class name> : <card title>
# /card
```

Adds a bootstab card to the sheet, with "class-name" as css class and a card-header with the given title.

```
<div class="card class-name" id="class-name">
    <div class="card-header class-name">card title</div>
</div>
```

### card-body

```
# card-body
# /card-body
```

Adds the card body to the sheet.

```
<div class="card-body">
</div>
```

### table

```
# table or # table: horiz
# /table
```

Formats the content inbetween as a table instead of using divs.

Output when using # table

```
<table class='table'>
    <tr><th class='lbl {{eo}} lbl-name'> Name </th><td class='var {{eo}} var-name'> {{variables.name|default}} </td></tr>
    <tr><th class='lbl {{eo}} lbl-species'> Species </th><td class='var {{eo}} var-species'> {{variables.species|default}} </td></tr>
    <tr><th class='lbl {{eo}} lbl-archetype'> Archetype </th><td class='var {{eo}} var-archetype'> {{variables.archetype|default}} </td></tr>
</table>
```

Output when using # table: horiz

```
<table class='table'>
    <tr>
        <th class='lbl {{eo}} lbl-name'> Name </th><td class='var {{eo}} var-name'> {{variables.name|default}} </td>
        <th class='lbl {{eo}} lbl-species'> Species </th><td class='var {{eo}} var-species'> {{variables.species|default}} </td>
        <th class='lbl {{eo}} lbl-archetype'> Archetype </th><td class='var {{eo}} var-archetype'> {{variables.archetype|default}} </td>
    </tr>
</table>
```

Default output without usage of # table

```
<div class='cContainer'><div class='lbl lbl-name'> Name </div><div class='var var-name'> {{variables.name|default}} </div></div>
<div class='cContainer'><div class='lbl lbl-species'> Species </div><div class='var var-species'> {{variables.species|default}} </div></div>
<div class='cContainer'><div class='lbl lbl-archetype'> Archetype </div><div class='var var-archetype'> {{variables.archetype|default}} </div></div>
```

## Loops
### iter

```
# iter: <count>
# /iter

```
Repeats the block inbetween <count> times and also adds _<count> to all variable names.
Output for <count> is two digits with a leading zero, so 01, 02 ... 09, 10, 11 ...
Iter can also work in tandem with table. Iter lists also include setting a variable eo
that is being used to tag the lines with ev(en) or od(d) class names so you can easily
color the lines in two alternating colours etc.

Example input:

```
# table: horiz
# iter: 3
weapon name:
    label: "weapon name"
    input: string
weapon damage:
    label: "weapon damage"
    input: string
weapon quality:
    label: "weapon quality"
    input: string
weapon attribute:
    label: "weapon attribute"
    input: string
# /iter
# /table
```

Example output:

```
<table class='table'>
    <tr>
        {% for i in 1..3 %}
            {% set id = i %}{% if id < 10 %}{% set id = '0' ~ id %}{% endif %}
            {% set eo = 'od' %}{% if id is even %}{% set eo = 'ev' %}{% endif %}
        <tr>
            <th class='lbl {{eo}} lbl-weapon-name'> Weapon Name </th><td class='var {{eo}} var-weapon-name'> {{attribute(variables, 'weapon_name_' ~ id)|default}} </td>
            <th class='lbl {{eo}} lbl-weapon-damage'> Weapon Damage </th><td class='var {{eo}} var-weapon-damage'> {{attribute(variables, 'weapon_damage_' ~ id)|default}} </td>
            <th class='lbl {{eo}} lbl-weapon-quality'> Weapon Quality </th><td class='var {{eo}} var-weapon-quality'> {{attribute(variables, 'weapon_quality_' ~ id)|default}} </td>
            <th class='lbl {{eo}} lbl-weapon-attribute'> Weapon Attribute </th><td class='var {{eo}} var-weapon-attribute'> {{attribute(variables, 'weapon_attribute_' ~ id)|default}} </td>
        </tr>
        {% endfor %}
    </tr>
</table>
```

End of file. Stop reading here. :D