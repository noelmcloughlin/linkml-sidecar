## Schema

The data model of this repository is a LinkML schema at
`.linkml/src/<PROJ_SLUG>/schema/<PROJ_SLUG>.yaml`, also reachable as
`linkml_schema/`. Read it before the code it describes: every class, field
and enum is defined once there, with its meaning mapped to public
vocabularies, and the JSON Schema, OWL and the rest under `.linkml/project/`
and the Pydantic models under `.linkml/src/<PROJ_SLUG>/datamodel/` are
generated from it, never edited. Change the schema
through the `linkml-author` skill (`npx skills add
noelmcloughlin/linkml-sidecar --skill linkml-author --yes`), and run
`just --justfile .linkml/justfile lint` and `test` before committing.

The `.lokf/` knowledge bundle validates its concepts against this schema
too (`lokf validate --schema`): a concept whose `type` names a class
defined here carries only the fields that class declares.
