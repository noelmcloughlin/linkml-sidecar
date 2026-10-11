> **The data model is a sidecar.** `.linkml/` holds <PROJ_NAME>'s schema in
> [LinkML](https://linkml.io), and the JSON Schema, Pydantic models, OWL and
> documentation are generated from it; nothing in the build depends on it.
> `linkml_schema/` at the root is the same schema folder under a visible
> name. Edit the schema with the
> [`linkml-author`](https://github.com/noelmcloughlin/linkml-sidecar) skill
> (`npx skills add noelmcloughlin/linkml-sidecar --skill linkml-author --yes`)
> and run `just --justfile .linkml/justfile lint` before committing;
> `.linkml/README.md` says what is generated and what is hand-written.
> **Agents:** read `.linkml/src/<PROJ_SLUG>/schema/<PROJ_SLUG>.yaml` before
> the code it describes.
