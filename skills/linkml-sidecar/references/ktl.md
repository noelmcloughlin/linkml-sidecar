# KTL mode: the sidecar's schema as the bundle's domain schema

This page is for the **scaffold** and for whoever reads its KTL hand-off lines. When the host carries a `.lokf/` bundle, the sidecar's schema is the *domain schema* that ktl-librarian's [domain-schema.md](https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/skills/ktl-librarian/references/domain-schema.md) describes: a LinkML schema importing LOKF's, whose `is_a: Concept` classes the bundle's concepts may name in `type`, checked by `lokf validate --schema`. That page is the recipe and the authority on what the validator expects (every class is closed; `type` names the class exactly). This page says how the sidecar meets it.

## What the scaffold does in KTL mode

1. **Pins the core schema beside the bundle.** `.lokf/lokf.yaml` is copied out of the installed `lokf` toolkit (`uv sync` in `.lokf/`, then the package's `data/lokf.yaml`), at the floor `.lokf/pyproject.toml` names. This is domain-schema.md's step 1. The copy is the one the schema imports, and the one `lokf convert`, `serve` and `query` read from `.lokf/`.
2. **Lays down a dummy that imports it.** `src/<slug>/schema/<slug>.yaml` carries `imports: [linkml:types, ../../../../.lokf/lokf]` and one class, `ExampleConcept`, `is_a: Concept`, with one slot of its own; `tests/data/problem/valid/ExampleConcept-001.yaml` is a concept of it under the bundle's `base_iri`, and the invalid example lacks `type`. LinkML resolves the import relative to the schema file, so `just lint`, `just gen-project`, `just gen-doc` and `just test` all see LOKF's classes.
3. **Excuses LOKF's own names in the linter.** `linkml-lint`'s `standard_naming` rule walks the import closure, and LOKF's relation slots are camelCase (`isPartOf`, `dependsOn`, ...). `.linkml/.linkmllint.yaml` extends the recommended rules and lists those names under `exclude`, read from the pinned copy, and nothing else: the host's own slots are still held to snake_case. Regenerate it with `--repair .linkmllint.yaml` when the floor moves.
4. **Renders LOKF's pages in the docs.** `config.public.mk` gets `LINKML_GENERATORS_DOC_ARGS="--render-imports"`, so `is_a: Concept` links to a page that exists.
5. **Wires `.lokf/justfile`** (domain-schema.md's step 4): `schema := "../.linkml/src/<slug>/schema/<slug>.yaml"` after `bundle := "knowledge"`, and `lokf-validate` and `lokf-check-refs` pass `--schema`. The edit matches ktl-sidecar's template lines exactly; a justfile that differs gets the edit printed instead of patched.

## The one workaround, and when it ends

The two recipes run from the schema's directory rather than from `.lokf/`:

```just
lokf-validate:
    cd {{ parent_directory(schema) }} && uv run --project {{ justfile_directory() }} lokf validate --schema {{ file_name(schema) }} {{ justfile_directory() }}/{{ bundle }}
```

`lokf validate` hands the schema path to `linkml.validator.validate()`, which loads the file into a `SchemaDefinition` without its `source_file`, so the schema's relative import resolves from the working directory, not from the file. From the schema's own directory the same string resolves to the same place for both the validator and `SchemaView`, so lint, the generators and the validator agree. [linkml PR 3855](https://github.com/linkml/linkml/pull/3855) changes how imports are tracked and shipped in linkml 1.12.0. The `cd` form works on 1.11.x and on 1.12.0 alike, so it stays while a `.lokf/uv.lock` may still hold 1.11.x; once `uv run lokf validate --schema ../.linkml/src/<slug>/schema/<slug>.yaml knowledge` passes from `.lokf/` on the locked version, the recipes can lose the `cd`.

On a `.lokf/` from a ktl-sidecar release that predates the `schema := ""` variable, the three KTL workflows (`knowledge-registrar.yaml`, `knowledge-librarian.yaml`, `knowledge-release.yaml`) run `uv run lokf validate --check-refs` inline in `.lokf/`, and the scaffold edits the two recipes by exact match on the template's lines. The hand-off then asks that each workflow's validate step run `uvx --from rust-just==1.47.0 just lokf-check-refs`, so the recipes stay in one place. The runners have no `just`, so the step runs it through `uvx`. A `.lokf/justfile` that already carries `schema := ""` (ktl-sidecar's template from the follow-up that added it, whose workflows run that line) needs only the variable set, and the scaffold sets it.

## Two more upstream limits the dummy works around

- **The generated dataclasses do not compile, and the example runner needs them.** LOKF has a slot named `from` (`UsageWindow`'s start date), and linkml's Python generator writes it as a field name, which is a Python keyword. `just gen-project` and `just gen-python` still run, but `src/<slug>/datamodel/<slug>.py` cannot be imported on linkml 1.11.1. linkml 1.12.0 escapes the field as `from_` ([PR 3317](https://github.com/linkml/linkml/pull/3317)), but its loaders still reject data that uses `from` ([PR 4083](https://github.com/linkml/linkml/pull/4083) is open). The template's example runner, the last part of `just test`, instantiates every file under `tests/data/valid/` through dataclasses it compiles the same way, so a valid example there fails too; counter-examples under `tests/data/invalid/` fail validation first and never reach that step. So KTL mode keeps its valid example under `tests/data/problem/valid/`, the folder the runner skips, and its `tests/test_data.py` validates the files of both folders through `linkml.validator.validate()` with the schema loaded by `SchemaView` (which keeps the file-relative import working today). The Pydantic models compile. Once a linkml release also maps `from` to `from_` when loading, the examples move to `tests/data/valid/`.
- **`copier update --pretend` fails in a subproject.** Copier runs its dry-run diff with the subproject path as a git pathspec from the wrong directory. `just update` (a real update) works from `.linkml/`, and so does `copier update --trust --skip-answered .linkml` from the host root; read the diff afterwards instead of a dry run.

## What the host still does by hand

- **The plugins.** KTL Registrar and KTL Curator each carry a *Known LOKF types* setting; add each domain class to both (domain-schema.md, step 5). The skills need no telling: ktl-librarian's Rule 3 reads the schema the justfile names.
- **The floor.** When `.lokf/pyproject.toml`'s `lokf` floor moves, refresh `.lokf/lokf.yaml` from the new toolkit in the same change, regenerate `.linkmllint.yaml`, and re-run both gates. A copy older than the toolkit validates against classes and slots the toolkit no longer means.
- **Removal.** A `.lokf/justfile` that names the schema goes back to `schema := ""` when the sidecar is removed (on an older justfile, to `uv run lokf validate {{ bundle }}` in both validate recipes); `.lokf/lokf.yaml` may stay.
