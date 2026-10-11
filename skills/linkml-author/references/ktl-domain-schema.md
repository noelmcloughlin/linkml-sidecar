# Beside a KTL bundle: what the author keeps in mind

The authority for a domain schema that `lokf validate --schema` checks is ktl-librarian's [domain-schema.md](https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/skills/ktl-librarian/references/domain-schema.md); the sidecar's wiring of it is linkml-sidecar's [ktl.md](../../linkml-sidecar/references/ktl.md). This page is the author's short form.

## What the validator expects

- **Every class is closed.** A concept fails its class on any key the class does not declare. A built-in LOKF class plus one key of your own is not valid: subclass it and declare the key.
- **`type` names the class exactly.** A concept of a subclass writes the subclass name, not the parent's; the validator matches concepts against every class at once.
- **The import stays.** `imports: [linkml:types, ../../../../.lokf/lokf]` is how the schema sees `Concept`, `Reference`, `Playbook` and the rest. The path is relative to the schema file and the pinned copy lives in `.lokf/`.

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

A class `is_a: Concept` joins the bundle's concept union, and so does any descendant of it. Subclass a built-in whose meaning fits; give a class of its own to what no built-in describes; never leave extra keys on a built-in unchanged.

## What the generators cannot do here

- The generated dataclasses (`src/<slug>/datamodel/<slug>.py`) do not compile beside LOKF, because LOKF's `from` slot is a Python keyword and `gen-python` does not escape it, and the example runner at the end of `just test` instantiates every file under `tests/data/valid/` through the same dataclasses. So valid examples live under `tests/data/problem/valid/`, which the runner skips, and `tests/test_data.py` validates the files of both folders with `linkml.validator`, loading the schema through `SchemaView` so the relative import resolves. Counter-examples stay under `tests/data/invalid/`. The Pydantic models compile. Move the valid examples to `tests/data/valid/` once linkml escapes keyword slot names.
- `linkml-lint` lints LOKF's camelCase slot names through the import closure; `.linkml/.linkmllint.yaml` excuses exactly those names. Regenerate it when `.lokf/lokf.yaml` moves (linkml-sidecar `--repair .linkmllint.yaml`).
- `gen-doc` renders LOKF's pages too (`--render-imports`), so the docs site shows the whole vocabulary a concept may use.

## After each change

```bash
just --justfile .linkml/justfile lint && just --justfile .linkml/justfile gen-project && just --justfile .linkml/justfile test
cd .lokf && just lokf-validate && just lokf-check-refs
```

Then tell the person which classes are new, so the KTL plugins' "Known LOKF types" setting can list them, and whether any concept in the bundle now needs its `type` changed to a class that declares its keys.
