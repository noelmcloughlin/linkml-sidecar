## Where the schema is

This sidecar was given a schema the repository already had: `<SCHEMA_DIR>/<PROJ_SLUG>.yaml`. `config.public.mk` names that folder (`LINKML_SCHEMA_SOURCE_DIR`), so every recipe above reads the schema where it is; nothing was moved, copied or linked. Edit it there, and keep its example data here under `tests/data/`. `src/<PROJ_SLUG>/schema/` holds only a README that says the same, because the template expects the folder.
