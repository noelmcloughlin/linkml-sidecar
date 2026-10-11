---
name: linkml-author
description: 'Author and evolve the LinkML schema of a project: the `.linkml/` sidecar linkml-sidecar installs, a visible `linkml/` one, or a repository that is itself a linkml-project-copier project. Use when: someone asks to add, change or deprecate a class, slot, enum or type; to model a concept, map a specification, standard or document to a schema, or replace the dummy schema with the real model; to check schema conventions; or to run lint, gen-project, gen-doc or test. Not for installing or repairing the sidecar; that is linkml-sidecar. Keywords: LinkML, schema authoring, data model, classes, slots, enums, mappings, linkml-lint, gen-project, JSON Schema, Pydantic, OWL, LOKF domain schema, KTL.'
license: Apache-2.0
compatibility: 'Requires bash and uv; every LinkML tool runs through the project''s own environment (`uv run` inside the schema project), never a globally installed one. Works on any host that holds a linkml-project-copier project, with or without a `.lokf/` KTL bundle.'
---

# linkml-author

Turn a project's LinkML schema into the model its code, data and documents describe, and keep it linted, generated, documented and tested after every change. The schema is one YAML file (or a few modules) and everything else is generated from it, so this skill edits the schema and runs the recipes; it never edits a generated file.

> Sources: linkml.io is the canonical site for the language ([schemas](https://linkml.io/linkml/schemas/), [generators](https://linkml.io/linkml/generators/)). The metamodel detail this page leaves out is in [references/metamodel.md](references/metamodel.md); the pitfalls of particular generators, each stamped with the LinkML version it was seen on, are in [references/generators.md](references/generators.md).

> Model: keep this skill on the calling agent's normal model. Mapping a document to classes and slots is judgement, and a wrong mapping validates fine.

## Scope

- **linkml-sidecar** installs the project and its dummy schema, once.
- **This skill** replaces the dummy with the real model and evolves it, as often as the domain changes. A missing or broken sidecar file (the preflight, the README, a dummy data file) goes back to linkml-sidecar's `--repair`.

> Guardrails: never edit a template-owned file (`justfile`, `pyproject.toml`, `config.yaml`, most of `mkdocs.yml`); `just update` is how those change, and `project.justfile` takes the project's own recipes. Never edit anything under `project/`, `docs/elements/` or `src/<slug>/datamodel/`: those are generated, and the next recipe overwrites them. Never run `just setup` or `just deploy` in a sidecar. Never loosen a validator to admit data: fix the schema or the data.

## Step 0 - Find the project

Run the preflight the sidecar installed, `.linkml/scripts/linkml-preflight.sh`, or linkml-sidecar's `templates/scripts/linkml-preflight.sh` when none is installed; its `sidecar` and `project` lines name the project directory and the schema file. The layouts it knows, in the order it looks:

| Layout | Project directory | How to tell |
| --- | --- | --- |
| the sidecar | `.linkml/` | `.linkml/.copier-answers.yml` |
| a visible sidecar, made by hand | `linkml/` | `linkml/.copier-answers.yml` |
| the repository is the project | `.` | `.copier-answers.yml` at the root |

Inside the project directory, `config.public.mk` names the schema: `LINKML_SCHEMA_NAME` is the slug and `LINKML_SCHEMA_SOURCE_DIR` the folder, so the file is `<dir>/<slug>.yaml`. Read `README.md` there before editing: in a sidecar it says which files are the template's, which are the host's, and which recipes never to run.

Run every recipe with `just --justfile <project>/justfile <recipe>`; `just` changes into the project directory itself, so this works from the host's root. Without `just`, `uvx --from rust-just just --justfile <project>/justfile <recipe>` does the same. Run every LinkML tool through the project (`uv run linkml-lint ...` inside it, or the recipes), never a `linkml-lint` or `gen-project` found on the path: the versions in `uv.lock` are the ones the host tested with.

## The gate

After every schema edit, in this order:

```bash
just --justfile .linkml/justfile lint          # linkml-lint, the recommended rules: warnings fail it
just --justfile .linkml/justfile gen-project   # every generator in config.yaml, plus Python, Pydantic, Java, TypeScript, OWL
just --justfile .linkml/justfile test          # generate into tmp/, pytest, then the example runner (it does not lint)
```

`just test` runs no lint, so `lint` comes first. A generator that fails on a schema `lint` accepted is a schema error too; the message names the element. `just gen-doc` then `just testdoc` shows the docs site locally, and `just site` regenerates everything at once. When a project installs its tools for the first time, `just install` comes before the gate.

Example data sits beside the schema's tests: `tests/data/valid/<ClassName>-<anything>.yaml` must validate against `ClassName`, and `tests/data/invalid/<ClassName>-<anything>.yaml` must fail; the class is read from the file name. Every class that carries data in the host gets at least one valid example, and every constraint worth having gets one counter-example.

## Replacing the dummy

A fresh sidecar holds the `Person` example (or, beside a KTL bundle, `ExampleConcept`). Read the host first, then write the model in one pass and run the gate:

1. **Collect the sources.** The code's types and records (`src/`, `models/`, migrations, OpenAPI or GraphQL documents, JSON samples, database DDL), the documents that define the domain (a specification, a standard, a glossary), and any existing vocabulary the domain already publishes as LinkML or OWL, which is imported rather than redescribed.
2. **Map, do not transcribe.** [references/source-mapping.md](references/source-mapping.md) is the table: a persistent noun becomes a class, a controlled list an enum, a property a slot, a relationship a slot with an object range and an inverse, a containment root a `tree_root` class. Paraphrase descriptions; never paste a standard's text into the schema.
3. **Write the schema** in the header's namespace (`id`, `default_prefix` and the prefix's IRI stay as the sidecar set them), with every element described, every enum value given a `meaning` when a public term exists, and identifiers set where instances have them. Keep the dummy's data files only while its classes remain; replace them with the real model's examples.
4. **Run the gate**, then update `docs/index.md` and `docs/about.md` (host-owned) so the site says what the model is.
5. **Hand back** what was guessed: a class whose source was ambiguous, a slot whose range was inferred, a mapping left out for want of a sure match.

## Rules this skill follows

These settle the questions an author meets most, each stated once:

| Question | Rule |
| --- | --- |
| The schema header's `description` | `description: >-` on its own line, with the text indented beneath it; `\|-` on one line is invalid YAML |
| `name` of the schema | the slug, snake_case, the same as the file, the package and `LINKML_SCHEMA_NAME`; `title` carries the human name |
| Element names | classes and enums `PascalCase`, slots and types `snake_case`, enum values `snake_case`; `linkml-lint`'s `standard_naming` rule enforces this, and a project that wants `UPPER_CASE` values says so in a `.linkmllint.yaml` |
| Slots or attributes | a slot used by more than one class, or carrying a `slot_uri` identity, is a top-level `slots:` entry; a field only one class owns may be an `attributes:` entry of that class; never both for one name |
| `slot_usage` | refines a slot for one class (range, cardinality, description); it never changes the slot's identity |
| Annotation values | strings by default; a nested YAML value (LinkML 1.6+) only when a comment names the consumer that parses it, since generators ignore annotations |
| Dublin Core prefix | `dcterms: http://purl.org/dc/terms/` |
| Identity versus mappings | `class_uri` and `slot_uri` use the schema's own prefix (they render as the element's IRI); an upstream term goes in `exact_mappings` or `close_mappings` |
| Mappings | never guessed; a term with no sure match stays unmapped, or takes `related_mappings` with a comment |
| Deprecation | `deprecated:` with a reason, and `deprecated_element_has_exact_replacement:` when one exists; nothing is deleted while data may still carry it |
| Generated files | never edited; regenerate |
| An lmodel project | [references/lmodel-profile.md](references/lmodel-profile.md), opted into by the project's own conventions, never assumed |

## Evolving the model

- **Add** a class, slot, enum or type by the patterns in [references/metamodel.md](references/metamodel.md); then the gate.
- **Change** a range or cardinality only in the direction the existing data allows; a narrowing goes with a counter-example that shows what it now rejects.
- **Rename** by adding the new element, marking the old one deprecated with its replacement, and removing the old one in a later release.
- **Split** a growing schema into modules under the same folder, imported by the main file (`imports: [./module]`), without redeclaring an imported element.
- **Update the template** with `just update` on a clean tree, then the gate, then commit `uv.lock` and `.copier-answers.yml` with the diff.

## Beside a KTL bundle

When the host carries `.lokf/`, the schema is the bundle's domain schema (linkml-sidecar's [references/ktl.md](https://github.com/noelmcloughlin/linkml-sidecar/blob/main/skills/linkml-sidecar/references/ktl.md), and ktl-librarian's [domain-schema.md](https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/skills/ktl-librarian/references/domain-schema.md), which is the authority):

- a class the bundle's concepts may use is `is_a: Concept`, or a subclass of a LOKF built-in whose meaning fits; its concepts write that class name in `type`, exactly;
- every class is closed, so a concept carries only the slots its class declares; a built-in plus one key of its own is not valid, which is why the subclass exists;
- keep the `imports:` line and `.lokf/lokf.yaml` as the sidecar set them; when the `lokf` floor in `.lokf/pyproject.toml` moves, refresh the pinned copy and regenerate `.linkml/.linkmllint.yaml` (linkml-sidecar `--repair .linkmllint.yaml`);
- a valid example goes under `tests/data/problem/valid/`, not `tests/data/valid/`: the example runner cannot instantiate beside LOKF's `from` slot, and the validator-based `tests/test_data.py` reads both folders; counter-examples stay under `tests/data/invalid/`;
- after the gate, `cd .lokf && just lokf-validate && just lokf-check-refs`: the bundle against both schemas;
- never loosen the validator to admit a concept; add the class, or fit the concept to a built-in;
- a new class is one more name for the KTL plugins' "Known LOKF types" setting; say so in the hand-off.

[references/ktl-domain-schema.md](references/ktl-domain-schema.md) carries the rest: what the generated dataclasses cannot do beside LOKF, and why the data test validates instead of loading them.

## Hand-off

After a change, tell the person: which elements were added, changed or deprecated; what was guessed and from which source; whether the gate passed, and `lokf validate` beside a bundle; which docs pages were updated; and anything left for linkml-sidecar (a broken sidecar file) or for the KTL plugins (a new type).
