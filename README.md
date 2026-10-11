# linkml-sidecar

Two [Agent Skills](https://agentskills.io) that give a code repository a [LinkML](https://linkml.io) data model without touching its build: **linkml-sidecar** installs a hidden `.linkml/` folder holding a complete, pinned [linkml-project-copier](https://github.com/linkml/linkml-project-copier) project, and **linkml-author** turns its dummy schema into the model the code describes and keeps it linted, generated, documented and tested.

> **It is a sidecar.** One hidden folder, one visible doorway (`linkml_schema/`), one workflow, and a README inside that says which files are the template's and which are yours. Nothing in the host's build depends on it; `rm -rf .linkml linkml_schema` and one workflow file remove it. The schema is the source; the JSON Schema, the Pydantic and dataclass models, the OWL and SHACL, the TypeScript and the docs site are generated from it, one `just` recipe each.

## Two patterns

A repository that *is* a schema project, such as [lmodel/gist](https://github.com/lmodel/gist), runs copier at its root and needs nothing here. A domain codebase whose maintainers would resist a schema project landing in their root gets the sidecar. The template assumes a repository root in some twenty ways (its workflows render where GitHub never reads them, `just setup` nests a repository, `just deploy` pushes the host's Pages root, the README describes "the repository"); the skill catalogues every one and neutralises it, and the catalogue is what an upstream `layout: sidecar` answer would shrink.

## Install

```bash
npx skills add noelmcloughlin/linkml-sidecar --skill linkml-sidecar --skill linkml-author --yes
# or, in Claude Code:
claude plugin marketplace add noelmcloughlin/linkml-sidecar && claude plugin install linkml-sidecar@linkml-sidecar
```

Then ask your agent to set up a LinkML sidecar. It runs the preflight, gathers the project's facts from its manifests, README and git remote, runs one scaffold script, validates the result with the project's own tools, and hands off to linkml-author with a list of what it guessed. The hosts need `uv`; everything else (copier, just, LinkML) runs through it.

## With or without KTL

The sidecar stands alone. Beside a [Knowledge Trust Ladder](https://github.com/noelmcloughlin/knowledge-trust-ladder) bundle (`.lokf/`), its schema becomes the bundle's domain schema: it imports LOKF's core schema, each class in it that is `is_a: Concept` is a type the bundle's concepts may carry, and `lokf validate --schema` checks the bundle against both. The scaffold wires that in one run, and the skills say what the KTL plugins still need to be told.

## Layout

| Path | What it is |
| --- | --- |
| `skills/linkml-sidecar/` | The installer: `SKILL.md`, the scaffold under `scripts/`, every file it lays down under `templates/`, and the references (the assumption catalogue, portability, prerequisites, KTL, automation, the upstream proposal). |
| `skills/linkml-author/` | The author: `SKILL.md` and its references (the metamodel, generator pitfalls by version, source mapping, the lmodel profile, KTL). |
| `tests/` | The scaffold, the preflight and the workflow on throwaway hosts; `tests/conftest.py` says how to run them, with and without the network. |
| `scripts/validate-repository.sh` | The repository contract CI runs on every pull request. |

## Development

```bash
bash scripts/validate-repository.sh
uv run --no-project --with-requirements tests/requirements.txt pytest
git clone --branch v0.5.0 https://github.com/linkml/linkml-project-copier .template-cache/linkml-project-copier
LINKML_SIDECAR_SLOW=1 uv run --no-project --with-requirements tests/requirements.txt pytest -m slow
```

[CONTRIBUTING.md](CONTRIBUTING.md) is the checklist. The template pin lives in one place, `skills/linkml-sidecar/scripts/linkml-scaffold.sh`, and the contract holds every other mention to it.

## License

Apache-2.0. The generated projects carry the host's own license; linkml-project-copier is MIT.
