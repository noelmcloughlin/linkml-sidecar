# About the <PROJ_NAME> schema

The schema is hand-written YAML at `.linkml/src/<PROJ_SLUG>/schema/<PROJ_SLUG>.yaml` in the <PROJ_NAME> repository (<<REPO_URL>>). Everything else in the sidecar is generated from it: the JSON Schema, the Python dataclasses and Pydantic models, the OWL and SHACL files, the TypeScript types, and these pages.

The sidecar is a [linkml-project-copier](https://github.com/linkml/linkml-project-copier) project installed beside the host's code by the `linkml-sidecar` skill, with the template's root-only parts switched off. `.linkml/README.md` says which files are the template's, which are the host's, and how to update the template.

Schema identifier: <<SCHEMA_ID>>. License: <LICENSE_ID>.
