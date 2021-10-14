# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [1.5.0] - 2021-10-13
### Added
 - Support for WorldAnvil's `imgblock` bbcode.
 - `inline` code branch for power users. See the Inline section of `ABOUT.MD` for details.
 - `galaxies-end` code branch as a clone of the Galaxies End version of GalaxyAnvil.
 - `flex-block` class, which can be used to wrap `[tagged:tag-name|block]` bbcode to automatically size and organize article blocks.
    - Example code: `[container:flex-block][tagged:matari|block|Matari][/container]`
    - Example with `flex-block` container: [Example with class](https://i.imgur.com/M6SfDKH.jpeg)
    - Example without `flex-block` container: [Example without class](https://i.imgur.com/zI7vXJI.jpeg)

### Changed
 - Tweaked comment box font sizes to be more inline with the rest of the theme's sizes.
 - Updated `ABOUT.MD`.


## [1.4.0]
### Added
 - Support for WorldAnvil's new world presentation front page
 - Support for Organization Tree
 - Support for article tooltipster previews

### Changed
 - Tweaked small and muted text color to improve readability.

### Fixed
 - Search icon color not overriding default WA styles in inline version.
 - Tag labels in timelines not being colored.

## [1.3.0] - 2018-07-14
### Added
 - New Inline version of GalaxyAnvil, intended for copy+pasta use in your world's CSS box if preferred over the WorldAnvil theme selection. See Releases for CSS file and more details.
 - Support for `.card-box` classes
 - borderRadius variables for easier customization

### Fixed
 - Buttons in world header cover not rendering correctly
 - Image background not rendering
 - Artist credit links using wrong color

### Changed
 - Various tweaks and changes to incorporate the 2018 theme update's changes.
 - World menu and map boxes now use accent colors instead of primary.
 - Tweaked font sizes of various elements to improve readability.
 - Restyled timeline panels

## [1.2.5] - 2018-05-14
### Fixed
 - Fixed the 'Follow' button in world headers displaying as a big, empty green box.

## [1.2.4] - 2018-01-22
### Added
 - This changelog.
 - Support for `.col-md-12` to `.row-border-group`
   - This allows borders to be added to `[container:col-md-12]` blocks that span an entire row.
 - Support for `.panel-npcsheet`

### Changed
 - Colors used for horizontal rules (`[hr]`)
   - `hr` now uses `default` color
   - `hr` contained in `.panel-primary` and `.panel-npcsheet` now uses `primary` color
 - Darkened the background for `.aloud` (`[aloud]`) blocks
   - Improves readability of tooltip and link text with certain color schemes

### Fixed
 - Background gradient was stronger on some pages
