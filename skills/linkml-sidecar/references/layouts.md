# Where a LinkML schema lives, and how the skills find it

A LinkML schema can live in any repository. Most were never made with linkml-project-copier or its predecessor, linkml-project-cookiecutter, and the folder a project sits in has no fixed name. So both skills find the schema by what files say, never by where they sit, and the preflight (`templates/scripts/linkml-preflight.sh`, or the copy a sidecar installs under `.linkml/scripts/`) does the looking. This page is the rule it applies; the scaffold applies the same one in Python.

## The signals, and how long each lasts

| Signal | What it tells | Lifetime |
| --- | --- | --- |
| `.copier-answers.yml` whose `_src_path` names `linkml-project-copier` | a copier project | as long as copier does |
| `config.public.mk` | a project from copier or from the older cookiecutter, which both render it; it names the schema (`LINKML_SCHEMA_NAME`, `LINKML_SCHEMA_SOURCE_DIR`) | a convenience file upstream may retire; when it is gone, the answers' `project_slug` names the schema (`src/<slug>/schema/<slug>.yaml`) |
| a `*.yaml` or `*.yml` file that imports `linkml:types` or names the `linkml:` prefix and has a top-level `classes:`, `slots:`, `enums:`, `types:`, `subsets:` or `imports:` key | a schema on its own | the language's own |

A `.linkml/` directory is a strong sign that LinkML is in use, but not of what it holds: upstream LinkML may name it for configuration files, and the sidecar names it for a whole project. The two uses coexist by files. `.linkml/.copier-answers.yml` means the sidecar; anything else in there is left alone. Both uses keep the generators' settings at `.linkml/generators.yaml`: a sidecar renames the template's `config.yaml` to that, and `--repair generators.yaml` moves a root project's file there.

## Where the preflight looks

The candidates, in the order the first match wins: `.linkml/`, the repository root, the directory the preflight was started in, then every directory one level down, hidden or not. A second project found is reported as `also`, and a person says which one is meant.

With no project anywhere, the preflight finds the schema files by content, among what git tracks or would track, or else in the whole tree. It skips the folders that by convention hold copies, fixtures or rendered output: `.git`, `.github`, `.venv`, `node_modules`, `tmp`, `site`, `project`, `docs`, `tests`, `test`, `fixtures`, `templates`, `.lokf` and `.linkml`.

## What each line means for each skill

| The preflight says | linkml-author | linkml-sidecar |
| --- | --- | --- |
| `ok sidecar .linkml/ from <template> at <tag>` | works there | nothing to do; `--repair` rewrites one file |
| `info sidecar <dir>/ is a LinkML schema project`, or `this repository is itself one` | works there, with the project's own recipes | refuses: the project has the toolchain already |
| `info sidecar .linkml/ holds configuration files` | looks on | installs around them; a name both hold is refused, never overwritten |
| `warn sidecar .linkml/ holds <project files> but no answers` | works there if it is a project | refuses until a person says which it is |
| `ok schema <file>` (one or more) | works on the file in place | `--adopt <file>` gives it the toolchain; several files: a person chooses |
| `info authors schema folder <dir>/: <n> people, <m> commits (<names>); repository: <r> people`, or `no person, only <k> bot commits`, or `history not weighed` | weighs whether to offer a refactor, by its [schema-design.md](https://github.com/noelmcloughlin/linkml-sidecar/blob/main/skills/linkml-author/references/schema-design.md); the line is a fact, not a verdict | nothing |
| `missing sidecar no LinkML project or schema` | waits for one | installs the sidecar with the dummy |

## How the tools run

Always through the host's own environment, never through a `linkml-lint` or `gen-project` found on the path: the versions the host tested with are the ones that count. The `tools` line names the first that applies: the project's `justfile` (`just --justfile <project>/justfile <recipe>`, or `uvx --from rust-just just` without `just`), its `Makefile` (`make -C <project> <target>`), `uv run` or `poetry run` when the host's `pyproject.toml` names `linkml`, else `uvx --from linkml <tool>` with the version uvx resolved named in the hand-off.

## Adoption

A schema found outside any project can be given the sidecar's toolchain without moving it. `--adopt <file>` installs the sidecar with no dummy, sets the slug from the file's stem and the id from the file, and points `config.public.mk`'s `LINKML_SCHEMA_SOURCE_DIR` at the file's folder, relative to `.linkml/`. Every recipe derives its paths from that one line, so lint, the generators, the docs and the tests read the schema where it is. The file is never moved, copied, linked or edited.

The folder the template expects, `src/<slug>/schema/`, holds a README that says where the schema is, and no data: the host's classes are not the dummy's, so the hand-off asks for one example per class. The file must be `<slug>.yaml`, because the template names the schema after the slug and reads `.yaml`. Beside a `.lokf/` bundle the adopted schema is not made the domain schema. That is a decision for its maintainers, and linkml-author's work afterwards.
