# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [UNRELEASED]
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
