# Beside a KTL bundle: what the author keeps in mind

The authority for a domain schema that `lokf validate --schema` checks is ktl-librarian's [domain-schema.md](https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/skills/ktl-librarian/references/domain-schema.md). linkml-sidecar's [ktl.md](https://github.com/noelmcloughlin/linkml-sidecar/blob/main/skills/linkml-sidecar/references/ktl.md) says how the sidecar sets one up. This page is the author's short form, and applies when the schema is the bundle's domain schema: `.lokf/justfile` names it (`schema :=`) or a copy `lokf adapt` wrote from it, or it imports `.lokf/lokf.yaml`. A `.lokf/` beside a schema that is neither is a bundle about the repository, and nothing here applies until its maintainers make the schema the domain schema.

## Two routes: import or adapt

**Import.** A schema written for the bundle imports `.lokf/lokf.yaml`, and its classes descend from `Concept`. The sidecar's dummy takes this route, and the rest of this page assumes it unless a line says otherwise.

**Adapt.** A schema that is also published on its own, for importers that never see LOKF, cannot import `lokf.yaml`. LinkML merges the two files into one namespace, and a name both define (`id`, `name`, `description`, `version`) keeps one definition without a warning. slsa and gist are such schemas. Leave the published schema as it is. Let lokf's `adapt` write a copy into `.lokf/` that imports `lokf.yaml` ([publishing.md](publishing.md) lists its moves), and set `schema := "<slug>.yaml"` in `.lokf/justfile` to name the copy. The preflight's `lokf` line then says `a copy lokf adapt wrote`.

On the adapt route:

- **The source is the schema.** Edit the published schema where it lives and run the gate there, then adapt again. The copy is generated: never edit it. Keep the `lokf adapt` command, with its flags, in one recipe beside a second that adds `--check`, which fails in CI when the source or the `lokf` floor has moved and the copy has not. The copy's `notes` record what the flags did, not the flags.
- **The project's own tests stay as they are.** The source does not import LOKF, so `tests/data/valid/`, the generated dataclasses and the lint config need none of the workarounds below. `cd .lokf && just lokf-validate` checks the bundle against the copy.
- **The renamed keys are what a concept writes.** `adapt` renames each slot the source shares with LOKF to `<prefix>_<name>` and keeps its IRI, so a concept writes `slsa_id`, not `id`. The copy's `notes` list every rename; name them in the hand-off for the librarian.
- **A duplicate pair has one half left empty.** A source slot that means the same as one of LOKF's, but carries no IRI that `adapt` can match, survives beside it under its own or a renamed key: slsa's `slsa_name` beside `title`, and `slsa_description` beside LOKF's `description`. A concept writes LOKF's slot and leaves the other empty. lokf pull request 142 proposes `--fold name=title`, which merges the pair in the copy; once a release carries it, adapt again with the fold.
- **The plugins' types are the re-rooted classes.** The copy's `notes` name the classes `adapt` re-rooted on `Concept`; they and their descendants are the names for the KTL plugins' "Known LOKF types" setting.

## What the validator expects

- **Every class is closed.** A concept fails its class on any key the class does not declare. A built-in LOKF class plus one key of your own is not valid: subclass it and declare the key.
- **`type` names the class exactly.** A concept of a subclass writes the subclass name, not the parent's; the validator matches concepts against every class at once.
- **The import stays.** On the import route, `imports: [linkml:types, ../../../../.lokf/lokf]` is how the schema sees `Concept`, `Reference`, `Playbook` and the rest. The path is relative to the schema file and the pinned copy lives in `.lokf/`.

## What to write

```yaml
classes:
  Module:                      # a concept LOKF has no class for
    is_a: Concept
    description: One unit of a degree programme.
    slots: [module_code, ects, semester]
  SourceSnapshotReference:     # a built-in that fits, plus keys it lacks
    is_a: Reference
    description: A reference to a snapshot of a source, with when it was reviewed.
    slots: [source_kind, reviewed_at]
```

A class `is_a: Concept` joins the bundle's concept union, and so does any descendant of it. Subclass a built-in whose meaning fits; give a class of its own to what no built-in describes. A published vocabulary the domain schema needs comes in beside `lokf.yaml` through lokf's `adapt` ([publishing.md](publishing.md)), never by a raw import: its `id`, `type` and `name` would merge silently with LOKF's.

## What the generators cannot do here

These limits apply on the import route, where the project's own schema imports LOKF.

- The generated dataclasses (`src/<slug>/datamodel/<slug>.py`) do not compile beside LOKF, because LOKF's `from` slot is a Python keyword and `gen-python` does not escape it. The example runner at the end of `just test` instantiates every file under `tests/data/valid/` through the same dataclasses. So valid examples live under `tests/data/problem/valid/`, which the runner skips, and `tests/test_data.py` validates the files of both folders with `linkml.validator`, loading the schema through `SchemaView` so the relative import resolves. Counter-examples stay under `tests/data/invalid/`. The Pydantic models compile. linkml 1.12.0 escapes the field name. Move the valid examples to `tests/data/valid/` once a release also loads data that uses `from` (PR 4083).
- `linkml-lint` lints LOKF's camelCase slot names through the import closure; the project's `.linkmllint.yaml` excuses exactly those names. Regenerate it when `.lokf/lokf.yaml` changes (in a sidecar, linkml-sidecar `--repair .linkmllint.yaml`).
- `gen-doc` renders LOKF's pages too (`--render-imports`), so the docs site shows the whole vocabulary a concept may use.

## After each change

```bash
just --justfile <project>/justfile lint && just --justfile <project>/justfile gen-project && just --justfile <project>/justfile test
cd .lokf && just lokf-validate && just lokf-check-refs
```

On the adapt route, run the recipe that writes the copy between the two lines, so the bundle is checked against the new copy. Then tell the person which classes are new, so the KTL plugins' "Known LOKF types" setting can list them, and whether any concept in the bundle now needs its `type` changed to a class that declares its keys.
