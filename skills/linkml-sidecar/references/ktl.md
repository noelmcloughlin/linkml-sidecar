# KTL mode: the sidecar's schema as the bundle's domain schema

This page is for the **scaffold** and for whoever reads its KTL hand-off lines. When the host carries a `.lokf/` bundle, the sidecar's dummy schema is the *domain schema* that ktl-librarian's [domain-schema.md](https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/skills/ktl-librarian/references/domain-schema.md) describes: a LinkML schema importing LOKF's, whose `is_a: Concept` classes the bundle's concepts may name in `type`, checked by `lokf validate --schema`. That page is the recipe and the authority on what the validator expects (every class is closed; `type` names the class exactly). This page says how the sidecar meets it.

A schema the host already held (`--adopt`) is not made the domain schema: the scaffold runs in plain mode beside the bundle and says so in the hand-off. A bundle beside a schema may be a bundle *about* the repository, as in a schema repository that documents itself, and the schema is not changed until its maintainers decide otherwise. Then linkml-author adds, by hand, the import, the lint config and the justfile variable that the scaffold writes in KTL mode. A schema that is also published on its own takes the adapt route instead: it stays as it is, `lokf adapt` writes a copy into `.lokf/` that imports `lokf.yaml`, and the justfile names the copy. linkml-author's [ktl-domain-schema.md](../../linkml-author/references/ktl-domain-schema.md) says when each route applies.

## What the scaffold does in KTL mode

1. **Pins the core schema beside the bundle.** `.lokf/lokf.yaml` is copied out of the installed `lokf` toolkit (`uv sync` in `.lokf/`, then the package's `data/lokf.yaml`), at the floor `.lokf/pyproject.toml` names. This is domain-schema.md's step 1. The copy is the one the schema imports, and the one `lokf convert`, `serve` and `query` read from `.lokf/`.
2. **Writes a dummy that imports it.** `src/<slug>/schema/<slug>.yaml` carries `imports: [linkml:types, ../../../../.lokf/lokf]` and one class, `ExampleConcept`, `is_a: Concept`, with one slot of its own; `tests/data/problem/valid/ExampleConcept-001.yaml` is a concept of it under the bundle's `base_iri`, and the invalid example lacks `type`. LinkML resolves the import relative to the schema file, so `just lint`, `just gen-project`, `just gen-doc` and `just test` all see LOKF's classes.
3. **Excuses LOKF's own names in the linter.** `linkml-lint`'s `standard_naming` rule walks the import closure, and LOKF's relation slots are camelCase (`isPartOf`, `dependsOn`, ...). `.linkml/.linkmllint.yaml` extends the recommended rules and lists those names under `exclude`, read from the pinned copy, and nothing else: the host's own slots are still held to snake_case. Regenerate it with `--repair .linkmllint.yaml` when the floor moves.
4. **Renders LOKF's pages in the docs.** `config.public.mk` gets `LINKML_GENERATORS_DOC_ARGS="--render-imports"`, so `is_a: Concept` links to a page that exists.
5. **Edits `.lokf/justfile`** (domain-schema.md's step 4): `schema := "../.linkml/src/<slug>/schema/<slug>.yaml"` after `bundle := "knowledge"`, and `lokf-validate` and `lokf-check-refs` pass `--schema`. The edit matches ktl-sidecar's template lines exactly; a justfile that differs gets the edit printed instead of patched.
6. **Writes the same path as `[tool.lokf] schema`** in `.lokf/pyproject.toml`, once the justfile names it, so a `lokf` command given no `--schema` (lokf 0.9.0 or later) reads the schema too. KTL's preflight warns when the two differ, and so does this sidecar's. A table that already names another schema is printed, not patched.

## The one workaround, for a lokf 0.8.0 floor

On a justfile from before the `schema :=` variable, the scaffold makes the two recipes run from the schema's directory rather than from `.lokf/`:

```just
lokf-validate:
    cd {{ parent_directory(schema) }} && uv run --project {{ justfile_directory() }} lokf validate --schema {{ file_name(schema) }} {{ justfile_directory() }}/{{ bundle }}
```

On lokf 0.8.0, `lokf validate` passes the schema path to `linkml.validator.validate()`, which loads the file into a `SchemaDefinition` without its `source_file`, so the schema's relative import resolves from the working directory, not from the file. From the schema's own directory the same string resolves to the same place for both the validator and `SchemaView`, so lint, the generators and the validator agree. lokf 0.9.0 requires linkml-runtime 1.12, which resolves the import from the schema's own folder, so ktl-sidecar's template from KTL 0.60.0 passes `--schema` from `.lokf/` with no `cd`. The `cd` form works on both floors, and only a `.lokf/` still at lokf 0.8.0 needs it.

On a `.lokf/` from a ktl-sidecar release that predates the `schema := ""` variable, the three KTL workflows (`knowledge-registrar.yaml`, `knowledge-librarian.yaml`, `knowledge-release.yaml`) run `uv run lokf validate --check-refs` inline in `.lokf/`. The hand-off then asks that each workflow's validate step run `uvx --from rust-just==1.47.0 just lokf-check-refs`, so the recipes stay in one place. The runners have no `just`, so the step runs it through `uvx`. A `.lokf/justfile` that already carries `schema := ""` (ktl-sidecar's template from the follow-up that added it, whose workflows run that line) needs only the variable set, and the scaffold sets it.

## Two more upstream limits the dummy works around

- **The generated dataclasses do not compile, and the example runner needs them.** LOKF has a slot named `from` (`UsageWindow`'s start date), and linkml's Python generator writes it as a field name, which is a Python keyword. `just gen-project` and `just gen-python` still run, but `src/<slug>/datamodel/<slug>.py` cannot be imported on linkml 1.11.1. linkml 1.12.0 escapes the field as `from_` ([PR 3317](https://github.com/linkml/linkml/pull/3317)), but its loaders still reject data that uses `from` ([PR 4083](https://github.com/linkml/linkml/pull/4083) is open).

  The template's example runner, the last part of `just test`, instantiates every file under `tests/data/valid/` through dataclasses it compiles the same way, so a valid example there fails too. Counter-examples under `tests/data/invalid/` fail validation first and never reach that step. So KTL mode keeps its valid example under `tests/data/problem/valid/`, the folder the runner skips, and its `tests/test_data.py` validates the files of both folders through `linkml.validator.validate()` with the schema loaded by `SchemaView` (which keeps the file-relative import working today). The Pydantic models compile. Once a linkml release also maps `from` to `from_` when loading, the examples move to `tests/data/valid/`.

- **`copier update --pretend` fails in a subproject.** Copier runs its dry-run diff with the subproject path as a git pathspec from the wrong directory. `just update` (a real update) works from `.linkml/`, and so does `copier update --trust --skip-answered .linkml` from the host root; read the diff afterwards instead of a dry run.

## What the host still does by hand

- **The plugins.** KTL Registrar and KTL Curator each carry a *Known LOKF types* setting; add each domain class to both (domain-schema.md, step 5). The skills need no telling: ktl-librarian's Rule 3 reads the schema the justfile names.
- **The floor.** When `.lokf/pyproject.toml`'s `lokf` floor moves, refresh `.lokf/lokf.yaml` from the new toolkit in the same change, regenerate `.linkmllint.yaml`, and re-run both gates. A copy older than the toolkit validates against classes and slots the toolkit no longer means.
- **Removal.** When the sidecar is removed, a `.lokf/justfile` that names the schema is reset to `schema := ""` (on an older justfile, to `uv run lokf validate {{ bundle }}` in both validate recipes), and `[tool.lokf] schema` is removed from `.lokf/pyproject.toml`. `.lokf/lokf.yaml` may stay.
