---
name: linkml-author
description: 'Author and evolve the LinkML schema of any repository that holds one: a linkml-project-copier or linkml-project-cookiecutter project wherever it sits, the `.linkml/` sidecar linkml-sidecar installs, or a schema file on its own. Use when: someone asks to add, change or deprecate a class, slot, enum or type; to model a concept, map a specification, standard or document to a schema, or replace the dummy schema with the real model; to check schema conventions; or to run lint, gen-project, gen-doc or test. Not for installing or repairing the sidecar; that is linkml-sidecar. Keywords: LinkML, schema authoring, data model, classes, slots, enums, mappings, linkml-lint, gen-project, JSON Schema, Pydantic, OWL, LOKF domain schema, KTL.'
license: Apache-2.0
compatibility: 'Requires bash; every LinkML tool runs through the host''s own environment (`just`, `make`, `uv run` or `poetry run` in the schema project), or through a pinned `uvx --from linkml` when the host has none, never a globally installed one. Works with or without a `.lokf/` KTL bundle.'
---

# linkml-author

Turn a project's LinkML schema into the model its code, data and documents describe, and keep it linted, generated, documented and tested after every change. The schema is one YAML file (or a few modules) and everything else is generated from it, so this skill edits the schema and runs the recipes; it never edits a generated file.

> Sources: linkml.io is the canonical site for the language ([schemas](https://linkml.io/linkml/schemas/), [generators](https://linkml.io/linkml/generators/)). The metamodel detail this page leaves out is in [references/metamodel.md](references/metamodel.md); the reasons behind the design rules below, for a schema others will import or extend, are in [references/schema-design.md](references/schema-design.md); the pitfalls of particular generators, each stamped with the LinkML version it was seen on, are in [references/generators.md](references/generators.md).

> Model: keep this skill on the calling agent's normal model. Mapping a document to classes and slots is judgement, and a wrong mapping validates fine.

## Scope

- **linkml-sidecar** installs the project once, with a dummy schema, or adopting a schema the host already holds.
- **This skill** writes and evolves the model, as often as the domain changes, wherever the schema lives. A missing or broken sidecar file (the preflight, the README, a dummy data file) goes back to linkml-sidecar's `--repair` when the project is the `.linkml/` sidecar; another project's files come back through its own `copier update` or history.

> Guardrails: never edit a template-owned file (`justfile`, `pyproject.toml`, `config.yaml`, most of `mkdocs.yml`); `just update` is how those change, and `project.justfile` takes the project's own recipes. Never edit anything under `project/`, `docs/elements/` or `src/<slug>/datamodel/`: those are generated, and the next recipe overwrites them. Never run `just setup` or `just deploy` in a sidecar. Never loosen a validator to admit data: fix the schema or the data. Never move a schema into a sidecar unasked; it is authored where it is.

## Step 0 - Find the schema

A LinkML schema can live in any repository, and most were never made from a template, so the schema is found by what files say, never by where they sit. Run the preflight: the copy a sidecar installed, `.linkml/scripts/linkml-preflight.sh`, or linkml-sidecar's `templates/scripts/linkml-preflight.sh` when that skill is installed beside this one. Its `sidecar`, `project`, `schema` and `tools` lines name the layout, the schema file and the way to run the tools. Without either copy, apply the same rule by hand ([layouts.md](https://github.com/noelmcloughlin/linkml-sidecar/blob/main/skills/linkml-sidecar/references/layouts.md) is the full statement):

| Layout | How to tell | Where the schema is |
| --- | --- | --- |
| the sidecar | `.linkml/.copier-answers.yml` | `config.public.mk` in `.linkml/` names it; an adopted schema sits where `LINKML_SCHEMA_SOURCE_DIR` points, outside `.linkml/` |
| a schema project elsewhere: the root, `linkml/`, any directory one level down, or the one you were started in | a `.copier-answers.yml` whose `_src_path` names `linkml-project-copier`, or a `config.public.mk` (the older cookiecutter renders it too; upstream may retire it, and then the answers' `project_slug` names the schema) | `<dir>/<slug>.yaml` from `config.public.mk`, else `src/<slug>/schema/<slug>.yaml` |
| a schema file on its own | a `*.yaml` that imports `linkml:types` or names the `linkml:` prefix and has a top-level `classes:`, `slots:`, `enums:`, `types:` or `imports:` key, outside `docs/`, `tests/`, `project/` and the other folders that hold copies and output | where it is |
| `.linkml/` holding only configuration files | no answers file and no project files in it | not a layout: leave it alone and look on |

One schema: work on it. Several, in a project that names none or in a repository with no project: ask the person which one when the session is attended, and list them and stop when it is not. Read the project's `README.md` before editing: in a sidecar it says which files are the template's, which are the host's, and which recipes never to run.

**The tools.** Run everything through the host's own environment, in the first form that applies: the project's `justfile` (`just --justfile <project>/justfile <recipe>`; `just` changes into the project directory itself, and `uvx --from rust-just just` stands in without `just`), its `Makefile` (`make -C <project> <target>`, the same names), `uv run` or `poetry run` when the host's `pyproject.toml` names `linkml`, else `uvx --from linkml linkml-lint` and `uvx --from linkml gen-project`, naming the version uvx resolved in the hand-off. Never a `linkml-lint` or `gen-project` found on the path: the versions the host tested with are the ones that count.

## The gate

After every schema edit, in this order:

```bash
just --justfile <project>/justfile lint          # linkml-lint, the recommended rules: warnings fail it
just --justfile <project>/justfile gen-project   # every generator in config.yaml, plus Python, Pydantic, Java, TypeScript, OWL
just --justfile <project>/justfile test          # generate into tmp/, pytest, then the example runner (it does not lint)
```

`just test` runs no lint, so `lint` comes first. A generator that fails on a schema `lint` accepted is a schema error too; the message names the element. `just gen-doc` then `just testdoc` shows the docs site locally, and `just site` regenerates everything at once. When a project installs its tools for the first time, `just install` comes before the gate. A project with a `Makefile` runs the same targets through `make`.

A schema on its own has no recipes: the gate is `linkml-lint <schema>`, then `gen-project -d <a temporary folder> <schema>`, then `linkml-validate -s <schema> -C <Class> <file>` over whatever example data the host keeps, each through the environment Step 0 named. Say in the hand-off that the host has no test harness, and that linkml-sidecar `--adopt <schema>` would give it one.

Example data sits beside the schema's tests: `tests/data/valid/<ClassName>-<anything>.yaml` must validate against `ClassName`, and `tests/data/invalid/<ClassName>-<anything>.yaml` must fail; the class is read from the file name. Every class that carries data in the host gets at least one valid example, and every constraint worth having gets one counter-example. An adopted schema's sidecar starts with none; add them first.

## Replacing the dummy

A fresh sidecar holds the `Person` example (or, beside a KTL bundle, `ExampleConcept`); an adopted or found schema is already the model, so this section is skipped and the next applies. Read the host first, then write the model in one pass and run the gate:

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
| Element descriptions | one or two plain sentences saying what the element is, fit for a form field's hint or an API field's help text, since JSON Schema, Pydantic and OpenAPI copy the description and nothing else; a caveat for users goes in `comments`, a decision or an open question in `notes`, a clause reference in an annotation |
| `name` of the schema | the slug, snake_case, the same as the file, the package and `LINKML_SCHEMA_NAME`; `title` carries the human name |
| Element names | classes and enums `PascalCase`, slots and types `snake_case`, enum values `snake_case`; `linkml-lint`'s `standard_naming` rule enforces this, and a project that wants `UPPER_CASE` values says so in a `.linkmllint.yaml`. In a schema meant to be imported, class names carry a schema-specific prefix (`PIDInstOwner`), a mixin ends in `Mixin`, and an enum is singular with no `Enum` suffix |
| Permissible values | one style throughout; a value that must carry punctuation, start with a digit or differ from another only by case gets a `title` free of them |
| Slots or attributes | every field starts as an `attributes:` entry of its class; it becomes a top-level `slots:` entry only when a second class needs the same field with the same meaning, or it carries a `slot_uri` identity; fields unrelated classes share go in a mixin; never both forms for one name |
| `slot_usage` | refines a slot for one class (range, cardinality, description); it never changes the slot's identity |
| References between classes | `identifier: true` on the target's key and `range: <Class>` on the referring field, never a string key described in prose; where the objects live, `inlined: true` with `inlined_as_list: true` |
| Variants of one thing | a hierarchy whose base carries a `designates_type: true` field, never one class with a kind enum and fields that apply "only when"; a holder takes one multivalued field of the base class, not a field per kind |
| Enum inheritance | none: `is_a` and `inherits` are unsettled upstream and the generators do not apply them; repeat the values, or share their `meaning` terms |
| Versions | `version:` carries the full version; element IRIs carry only the part that breaks compatibility; a minor release only adds, never removes, renames or tightens, and a tightening is a major release |
| Annotation values | strings by default; a nested YAML value (LinkML 1.6+) only when a comment names the consumer that parses it, since generators ignore annotations; a fact the metamodel has no metaslot for goes in a structured annotation the schema declares as a metamodel extension (`instantiates:`), not in a description |
| Dublin Core prefix | `dcterms: http://purl.org/dc/terms/` |
| Identity versus mappings | `class_uri` and `slot_uri` use the schema's own prefix (they render as the element's IRI); an upstream term goes in `exact_mappings` or `close_mappings` |
| Mappings | never guessed; a term with no sure match stays unmapped, or takes `related_mappings` with a comment |
| Deprecation | `deprecated:` with a reason, and `deprecated_element_has_exact_replacement:` when one exists; nothing is deleted while data may still carry it |
| Generated files | never edited; regenerate |
| An lmodel project | [references/lmodel-profile.md](references/lmodel-profile.md), opted into by the project's own conventions, never assumed |

## Evolving the model

- **Add** a class, slot, enum or type by the patterns in [references/metamodel.md](references/metamodel.md); then the gate.
- **Change** a range or cardinality only in the direction the existing data allows; a narrowing is a major-version change and goes with a counter-example that shows what it now rejects.
- **Rename** by adding the new element, marking the old one deprecated with its replacement, and removing the old one in a later release.
- **Split** a growing schema into modules under the same folder, imported by the main file (`imports: [./module]`), without redeclaring an imported element.
- **Update the template** with `just update` on a clean tree, then the gate, then commit `uv.lock` and `.copier-answers.yml` with the diff.

## Beside a KTL bundle

The schema is the bundle's *domain schema* when `.lokf/justfile` names it (`schema :=`; the preflight's `lokf` line says `wired`) or it imports `.lokf/lokf.yaml`. A `.lokf/` beside a schema that is neither is a bundle *about* the repository, as in a schema repository that documents itself, and the schema stays what it is; wiring it is its maintainers' decision, made by adding the import, the lint config and the justfile variable, never assumed from the bundle's presence. For a domain schema (linkml-sidecar's [references/ktl.md](https://github.com/noelmcloughlin/linkml-sidecar/blob/main/skills/linkml-sidecar/references/ktl.md), and ktl-librarian's [domain-schema.md](https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/skills/ktl-librarian/references/domain-schema.md), which is the authority):

- a class the bundle's concepts may use is `is_a: Concept`, or a subclass of a LOKF built-in whose meaning fits; its concepts write that class name in `type`, exactly;
- every class is closed, so a concept carries only the slots its class declares; a built-in plus one key of its own is not valid, which is why the subclass exists;
- keep the `imports:` line and `.lokf/lokf.yaml` as the sidecar set them; when the `lokf` floor in `.lokf/pyproject.toml` moves, refresh the pinned copy and regenerate the project's `.linkmllint.yaml` (in a sidecar, linkml-sidecar `--repair .linkmllint.yaml`);
- a valid example goes under `tests/data/problem/valid/`, not `tests/data/valid/`: the example runner cannot instantiate beside LOKF's `from` slot, and the validator-based `tests/test_data.py` reads both folders; counter-examples stay under `tests/data/invalid/`;
- after the gate, `cd .lokf && just lokf-validate && just lokf-check-refs`: the bundle against both schemas;
- never loosen the validator to admit a concept; add the class, or fit the concept to a built-in;
- a new class is one more name for the KTL plugins' "Known LOKF types" setting; say so in the hand-off.

[references/ktl-domain-schema.md](references/ktl-domain-schema.md) carries the rest: what the generated dataclasses cannot do beside LOKF, and why the data test validates instead of loading them.

## Hand-off

After a change, tell the person: which layout Step 0 found and which tools ran (and, through uvx, which LinkML version); which elements were added, changed or deprecated; what was guessed and from which source; whether the gate passed, and `lokf validate` beside a wired bundle; which docs pages were updated; and anything left for linkml-sidecar (a broken sidecar file, or a schema that could be adopted) or for the KTL plugins (a new type).
