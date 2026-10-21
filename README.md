# linkml-sidecar

Two [Agent Skills](https://agentskills.io) that give a code repository a [LinkML](https://linkml.io) data model without touching its own build: **linkml-sidecar** installs a hidden `.linkml/` folder holding a complete, pinned [linkml-project-copier](https://github.com/linkml/linkml-project-copier) project, and **linkml-author** turns its dummy schema into the model the code describes and keeps it linted, generated, documented and tested.

> **It is a sidecar.** One hidden folder, one visible doorway (`linkml_schema/`), one workflow, and a README inside that says how to remove it. Nothing in the host's build depends on it. The schema is the source: the JSON Schema, Pydantic and dataclass models, OWL and SHACL, TypeScript and the docs site are generated from it, one `just` recipe each.

> **Two ways in.** This README is one; the other is a docent, a museum's name for a guide. Install [`ktl-docent`](https://github.com/noelmcloughlin/knowledge-trust-ladder) into whatever agent you already use, by a route from [the install page](https://w3id.org/ktl/docs/install/), and ask it anything about this project, such as what linkml-sidecar changes in a host's root folder. It answers from `.lokf/knowledge/`, the checked part of what the project knows, and says how far each answer has been trusted (still a draft, checked by automation only, or confirmed by a named person). It opens the source for exact values, and records what it could not answer so the gap gets filled. The same docent serves a person at a prompt, an agent reading this file, or a chatbot that can load a skill.
>
> **Agents:** if `.lokf/knowledge/index.md` exists, read it first. `llms.txt` says how to weigh it.

## Two patterns

A repository that *is* a schema project, such as [lmodel/gist](https://github.com/lmodel/gist), runs copier at its root and needs nothing here.

A domain codebase whose maintainers do not want a schema project in their root folder gets the sidecar.

## Install

```bash
npx skills add noelmcloughlin/linkml-sidecar --skill linkml-sidecar --skill linkml-author --yes
# or, in Claude Code:
claude plugin marketplace add noelmcloughlin/linkml-sidecar && claude plugin install linkml-sidecar@linkml-sidecar
```

Then ask your agent to set up a LinkML sidecar. It runs the preflight, gathers the project's facts from its manifests, README and git remote, runs one scaffold script, validates the result with the project's own tools, and hands off to linkml-author with a list of what it guessed. The hosts need `git` and `uv`; everything else (copier, just, LinkML) runs through uv.

## Run it yourself

The skill's two scripts work without an agent. From the host's root, with this repository cloned beside it:

```bash
bash ../linkml-sidecar/skills/linkml-sidecar/templates/scripts/linkml-preflight.sh .
export PROJ_NAME="Acme Platform" PROJ_DESC="One sentence." GITHUB_ORG=acme \
  REPO_URL=https://github.com/acme/platform FULL_NAME="A Person" EMAIL=a.person@acme.example \
  LICENSE_ID=Apache-2.0 SCHEMA_ID=https://w3id.org/acme/platform DOCS_URL=https://acme.github.io/platform/linkml/
bash ../linkml-sidecar/skills/linkml-sidecar/scripts/linkml-scaffold.sh --dry-run
bash ../linkml-sidecar/skills/linkml-sidecar/scripts/linkml-scaffold.sh
```

Step 0 of [the skill](skills/linkml-sidecar/SKILL.md) says where each fact comes from, and Step 1 lists the exit codes, `--repair` and `--pointers-only`.

## Layout

| Path | What it is |
| --- | --- |
| `skills/linkml-sidecar/` | The installer: `SKILL.md`, the scaffold under `scripts/`, every file it lays down under `templates/`, and the references (the assumption catalogue, portability, prerequisites, KTL, automation, the upstream proposal). |
| `skills/linkml-author/` | The author: `SKILL.md` and its references (the metamodel, generator pitfalls by version, source mapping, the lmodel profile, KTL). |
| `tests/` | The scaffold, the preflight and the workflow on throwaway hosts; `tests/conftest.py` says how to run them, with and without the network. |
| `scripts/validate-repository.sh` | The repository contract CI runs on every pull request. |

## With or without KTL

The sidecar stands alone. Beside a [Knowledge Trust Ladder](https://github.com/noelmcloughlin/knowledge-trust-ladder) bundle (`.lokf/`), its schema becomes the bundle's domain schema: it imports LOKF's core schema, each class in it that is `is_a: Concept` is a type the bundle's concepts may carry, and `lokf validate --schema` checks the bundle against both. The scaffold sets that up in one run, and the skills say what the KTL plugins still need to be told.

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
