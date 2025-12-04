# Changelog

## [0.2.0] – 2025-12-05

### Added
- `.update()` method to update parts of the configuration.
- `.replace()` method to safely replace the entire configuration.
- Automatic creation of nested keys if they don’t exist.
- Schema validation for keys and types.
- Support for nested schema dictionaries.

### Changed
- Improved internal handling of dictionaries and lists for auto-wrapping.
- Enhanced dotted-path `.set()` and `.get()` methods with schema enforcement.

### Fixed
- Fixed type validation for primitive values when schema is provided.
- Fixed auto-creation errors for nested dictionaries when schema is not defined.

## [0.1.0] – 2025-12-03

### Added
- Initial release of `loadstructure`.
- Loading and saving configurations in **JSON, YAML, XML, TOML, INI/DEF** formats.
- Attribute-style access (`cfg.app.name`) and dictionary-style access (`cfg["app"]["name"]`).
- Merging multiple configuration files with precedence.
- Nested key access via dotted-path (`cfg.get("app.ui.theme")`, `cfg.set("app.ui.theme", "dark")`).
