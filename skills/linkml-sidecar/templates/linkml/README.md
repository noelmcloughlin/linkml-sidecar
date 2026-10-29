# `.linkml/`: <PROJ_NAME>'s schema sidecar

This is a small **sidecar** that holds <PROJ_NAME>'s data model as a [LinkML](https://linkml.io) schema and generates from it what each consumer reads: JSON Schema, Python dataclasses and Pydantic models, OWL and SHACL, TypeScript, and a documentation site. It does not touch the host's build. Nothing in the repository depends on it, and deleting it leaves the host as it was.

## The 60-second version

- **A LinkML schema** is one YAML file (or a few) that names the classes, their slots (fields), enums and types of a domain, with each term mapped to a public vocabulary where one exists.
- **The generators** turn that one file into every other representation, so the schema is the source and the rest is build output.
- **This folder** is a standard [linkml-project-copier](https://github.com/linkml/linkml-project-copier) project (template <TEMPLATE_REF>) with the parts that assume a repository root switched off. `copier update` keeps it current.

## What's in here

```text
.linkml/
|-- src/<PROJ_SLUG>/schema/<PROJ_SLUG>.yaml   # the schema: the one file to edit
|-- src/<PROJ_SLUG>/datamodel/               # generated Python (dataclasses, Pydantic)
|-- project/                                 # generated artefacts, gitignored (JSON Schema, OWL, SHACL, ...)
|-- docs/                                    # mkdocs site; docs/elements/ is generated
|-- tests/data/{valid,invalid}/              # example data the tests and the example runner check
|-- justfile, project.justfile               # the recipes (below); your own recipes go in project.justfile
|-- pyproject.toml, uv.lock                  # the Python project uv installs into .linkml/.venv
|-- config.public.mk, generators.yaml        # the schema's name and path; the generators' settings
|-- mkdocs.yml                               # the docs site
|-- scripts/linkml-preflight.sh              # what this machine can do; the skills run it first
|-- .copier-answers.yml                      # what the template was told; `just update` reads it
`-- .github/, .pre-commit-config.yaml        # the template's copies: inert here (GitHub and pre-commit read the root only)
```

## Who owns what

| Files | Owner | Change them by |
| --- | --- | --- |
| `justfile`, `pyproject.toml`, `mkdocs.yml` (all but two lines), `.github/`, `.pre-commit-config.yaml`, `.gitignore`, `.editorconfig`, `.yamllint.yaml`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `src/<PROJ_SLUG>/__init__.py`, `_version.py`, `tests/__init__.py` | the template | `just update` from this folder; never by hand |
| `README.md` (this file), `LICENSE`, `docs/index.md`, `docs/about.md`, `src/<PROJ_SLUG>/schema/`, `tests/test_data.py`, `tests/data/` | <PROJ_NAME> | editing; copier never touches them (`_skip_if_exists`) |
| `project.justfile`, `config.public.mk`, the `site_url` and `repo_url` lines of `mkdocs.yml` | both | editing; `copier update` merges |
| `generators.yaml`, the template's `config.yaml` renamed | <PROJ_NAME> | editing; `just update` no longer changes it, so carry over what the template's changelog says changed in `config.yaml` |
| `scripts/linkml-preflight.sh`, `.linkmllint.yaml` when present | the `linkml-sidecar` skill | its repair |

`CODE_OF_CONDUCT.md` and `CONTRIBUTING.md` here are the template's; the host's own govern.

## The doorway

`linkml_schema` at the repository root is `src/<PROJ_SLUG>/schema/` under an ordinary, visible name, for folder pickers and file managers that hide dot-folders. Git carries the link; a sync service does not, so `just linkml-link` recreates it on a machine where it is missing (Windows: `mklink /J linkml_schema .linkml\src\<PROJ_SLUG>\schema`). Everything below works without it.

## Use it

[`uv`](https://docs.astral.sh/uv/) is required; [`just`](https://just.systems/) is optional (`uvx --from rust-just just` does the same). From the repository root, `just` runs every recipe inside this folder:

```bash
just --justfile .linkml/justfile install      # one-time: uv sync --group dev
just --justfile .linkml/justfile lint         # linkml-lint on the schema
just --justfile .linkml/justfile gen-project  # regenerate project/ and the Python datamodel
just --justfile .linkml/justfile test         # generate into tmp/, pytest, run the examples (does not lint)
just --justfile .linkml/justfile gen-doc      # docs/elements/ from the schema
just --justfile .linkml/justfile testdoc      # the docs site on a local server
just --justfile .linkml/justfile site         # gen-project and gen-doc
just --justfile .linkml/justfile              # every recipe
```

Or `cd .linkml` and drop `--justfile .linkml/justfile`. Without `just`:

```bash
cd .linkml
uv sync --group dev
uv run linkml-lint src/<PROJ_SLUG>/schema
uv run gen-project --config-file generators.yaml -d project src/<PROJ_SLUG>/schema/<PROJ_SLUG>.yaml
```

Use these, not a `linkml-lint` or `gen-project` installed elsewhere: the versions are pinned in `uv.lock`.

## Edit the schema

The gate after every change: `lint`, then `gen-project`, then `test`. Example data lives under `tests/data/valid/` and `tests/data/invalid/` as `<ClassName>-<anything>.yaml`; the class is read from the name. Beside a knowledge bundle, valid examples go under `tests/data/problem/valid/` instead (the section below says why). The `linkml-author` skill ([noelmcloughlin/linkml-sidecar](https://github.com/noelmcloughlin/linkml-sidecar)) edits the schema this way and knows the metamodel; install it with `npx skills add noelmcloughlin/linkml-sidecar --skill linkml-author --yes`.

## Never run here

- `just setup`: it runs `git init` and commits, which would nest a repository inside this one.
- `just deploy`: it pushes the host's `gh-pages` branch root. The host's workflow, `linkml-sidecar.yaml` in `.github/workflows/` (or the folder Forgejo reads), runs `lint` and `test`, builds the site, and publishes it under the `linkml/` subpath only when the repository variable `LINKML_DOCS_ENABLED` is `true`.

## Keep it current

```bash
cd .linkml && just update       # copier update --trust --skip-answered, then uv lock --upgrade-package linkml
```

Run it on a clean tree, read the diff, and commit `uv.lock` and `.copier-answers.yml` with it. The template's own files change; yours do not. There is no dry run: `copier update --pretend` fails inside a subfolder of a repository, so the diff is the preview.

## With a knowledge bundle (`.lokf/`)

When the host carries a [KTL](https://github.com/noelmcloughlin/knowledge-trust-ladder) bundle, this schema imports LOKF's core schema (`.lokf/lokf.yaml`, pinned at the toolkit's floor) and every class here that is `is_a: Concept` is a type the bundle's concepts may carry. `.lokf/justfile` names this schema as `schema :=`, so `just lokf-validate` and `just lokf-check-refs` check the bundle against both. Keep `.lokf/lokf.yaml` in step with the `lokf` floor, and tell the KTL plugins' "Known LOKF types" setting about each class. LOKF has a slot named `from`, which the template's example runner cannot compile as a dataclass field, so valid examples live under `tests/data/problem/valid/`, the folder the runner skips, and `tests/test_data.py` validates both folders through `linkml.validator`.

## Remove it

Three deletions and two edits, nothing else references it: `rm -rf .linkml linkml_schema` and the workflow `linkml-sidecar.yaml`, then drop the sidecar aside from `README.md` and the `## Schema` section from `llms.txt`. A `.lokf/justfile` that names the schema is reset to `schema := ""` (or, on an older justfile, to `uv run lokf validate {{ bundle }}` in both validate recipes), and `[tool.lokf] schema` is removed from `.lokf/pyproject.toml`.

## Learn more

- LinkML: <https://linkml.io/linkml/>; the schema language reference: <https://linkml.io/linkml/schemas/>
- The template this folder came from: <https://github.com/linkml/linkml-project-copier>
- The documentation site this folder builds: <<DOCS_URL>>
- The host project: <<REPO_URL>>
