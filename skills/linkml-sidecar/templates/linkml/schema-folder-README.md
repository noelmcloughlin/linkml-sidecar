# The schema is not here

<PROJ_NAME>'s schema lives at `<SCHEMA_DIR>/<PROJ_SLUG>.yaml` in the repository, where it was before this sidecar existed. `config.public.mk` names that folder (`LINKML_SCHEMA_SOURCE_DIR`), so every recipe reads it there. This folder exists because the template expects it; it holds nothing else, and copier leaves it alone (`_skip_if_exists`).
