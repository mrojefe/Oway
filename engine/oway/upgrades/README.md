# Oway change lists

One JSON file per release that moves or renames project files: `<from>-to-<to>.json`, read by `oway upgrade`. A release with no file moves nothing; `oway upgrade` then only updates the version in `_oway/config.json`.
