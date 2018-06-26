

# Newcomers Guide
## ...but first a speech
Hi,   
Welcome and thank you.  
If you read this it's because you want to help us make WA even greater and thus you are awesome.  
You made the first step in becoming a contributor, so let me help you make the few next one.

# Making a RPG-stat-block
## What is this RPG-stat-thingy
Well, RPG-stat-blocks are templates to create object in a RPG game system, if you have something containing game data and used by the system (like character sheet, object stat, npc, spell ...) it's a RPG-stat-block.
Or at least it should be one.  
The problem is there is quite a few RPG system out there and WA dev (our beloved **_Dimitris_**) is a just a tad occupied as we speak ( you know doing things like, building WA) so we, **_the community_**, need to do it.  
Feel up to the challenge ? 

## Recquirements 
To make a RPG-stat block you will need to :
- Know the unique identifier for the system you want to create templates for (for example dnd5e). If you don't know the Identifier of the system you can ask Dimitris (see Getting Help bellow) 
- Read the documentation 
- Have some knowledge of YAML (basic)
- Have some knoeledge of HTML 
- Have some knowledge of CSS (optional)
- Have done some very basic programming (we are talking if else and variables here)

You will need some sort of text editor (Dimitris highly recommend [SublimeText2 or 3](www.sublimetext.com)),  
Another good candidate is [VSCode](https://code.visualstudio.com/)

## How do i create a RPG-block
A RPG-block is only three files :

- a yml data model, which store the info needed for defining the data your block will hold and manipulate. it's look like this   
```YAML
version: 0.5
system: dnd35e
author: 
  username: GorkamWorka
unique_reference: character_dnd35e
name: Character Sheet
description: Character sheet for Dungeons and Dragons 3.5e
instructions: "The character sheet is meant to be used for the NOT trackable resources. Things like Curent HP, XP, Temporary HP, Ammunition, Class Resource, Spells remaining etc. will be tracked and used via the Campaign manager and the Digital Storyteller Screen (DSTS)"
fields:
  player_name:
    input: string
    label: "Player Name"
    placeholder: "Victor Hugo"
    required: false
```
ok i admit it's look hard but if you read it you'll see it's not that hard.  
it's mainly plain text english and when you understand the basic synstax it's pretty simple. (see the [Statblock-Cheatsheet](./statblock-cheatsheet.md) for more info on yaml syntax).  
WorldAnvil will use this to build the form in which someone fill the data and to know how to store the data of your block

- a HTML twig template, which define how the block will be printed for other user (frontend part of your block), so go creative and do a great digital design for your block 
```XML
<div class="row">
    <h1>{{ variables.name }}</h1>
</div>
<div class="row">
    <div class="char-img"></div>
</div>
<div class="row part-title">
    <h2>Character Infos</h2>
</div>
<div class="row">
    <div class="col char-info-table">
        <div class="row">
            <div class="col-6">
                <div class="row">
                    <div class="col-4 label">Character Name : </div>                    
                    <div class="col-8 value">{{ variables.name }}</div>                    
                </div>
            </div>
```
- a css file, which define the style applied to your block. It's where you can go full on creative.
```css
.system-dnd5e h1 p, 
.system-dnd5e h2 p, 
.system-dnd5e h3 p, 
.system-dnd5e h4 p,
.system-dnd5e h5 p, 
.system-dnd5e h6 p {
    margin:0;
}

.system-dnd5e.statblock {
    background-color: #e3dbc6;
    border: 1px solid #760809;
    padding: 20px;
    position: relative;
}

.system-dnd5e hr {
    margin: 0;
    color: #770808;
    border: 1px #c9ad6a solid;
    margin-top: 12px;
    margin-bottom: 12px;
}
```

## How to hit the ground running
1. First of read the Newcomers Guide ! 
1. Since that one seem already in the bag, go read [Contributions Guidelines](./CONTRIBUTING.md).
1. Sign in / Sign up to github (it's free)
1. come to **#rpg-statblock-help** on [WA-discord](https://discord.gg/cxKYPrD)
1. Say "Hi"
1. Ask if someone already as work ongoing on the block you wanna make  
 (Collaborative work is way better than doing things twice)
1. Go on and fork the repository.  
You now are the proud owner of your very own repo containing code done by the rest of community.
1. Look at the Dnd5e directory for reference
2. Read the [Statblock-cheatsheet](./statblock-cheatsheet.md)
1. Ask **@Dimitris#0041** for the identifier for your system, eventually ask for him to add a new one if your system is not yet on the list.
1. feel free to let us now of any question you may have on **#rpg-statblock-help**
4. Go and make your very own first block.

# Making a Skin for WA
_//-- Contribution needed --//_