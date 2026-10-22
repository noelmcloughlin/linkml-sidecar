# Contributing to linkml-sidecar

*This file is a checklist, not a design log. Each rule is a line or two that links to where its reasoning lives: a script header, a reference page, a workflow comment. `bash scripts/validate-repository.sh` fails when the file outgrows its word budget, so it stays that way.*

## Development setup

There is no build step: the skills are Markdown, YAML, shell and Python.

```bash
git clone https://github.com/noelmcloughlin/linkml-sidecar.git
cd linkml-sidecar
bash scripts/validate-repository.sh
uv run --no-project --with-requirements tests/requirements.txt pytest
```

The slow tests run the real template: clone the pinned tag into `.template-cache/linkml-project-copier` (the README has the command) and run pytest with `LINKML_SIDECAR_SLOW=1`. To try a change end to end, install from your clone into a throwaway consumer repository: `bash scripts/smoke-test-install.sh "$PWD"` does exactly that, then runs the installed preflight and the scaffold's dry run.

## Layout

| Path | Responsibility |
| --- | --- |
| `skills/linkml-sidecar/SKILL.md` | One-shot install: Step 0 gathers facts, the scaffold does Steps 1 to 3. Router only; its `references/` carry the detail. |
| `skills/linkml-sidecar/scripts/` | The scaffold, driver and Python half. The driver holds the one template pin. |
| `skills/linkml-sidecar/templates/` | Every file the sidecar writes that the template does not: the sidecar README, the dummies, the pointers, the workflow, the preflight. |
| `skills/linkml-sidecar/references/template-assumptions.md` | The catalogue: what the template assumes of a root, what the scaffold does, what upstream could remove. |
| `skills/linkml-author/SKILL.md` | Day to day: replace the dummy, evolve the model, run the gate. Its `references/` hold the metamodel and the pitfalls. |
| `tests/` | The scripts on throwaway hosts; `tests/fake_copier.py` stands in for copier offline. |
| `scripts/validate-repository.sh` | The contract: skill shape, links, lint, budgets, the pin, the pins in the workflow, prerequisites rows, invisible characters. |
| `scripts/smoke-test-install.sh` | The install path: the skills installed into a throwaway repository with `npx skills`, then run from there. |

## Before opening a pull request

- Run `bash scripts/validate-repository.sh` and `pytest`. CI runs both plus ShellCheck, `actionlint`, markdownlint, lychee, codespell, the install smoke test and the slow tests.
- Run `gh skill publish --dry-run` if you have the GitHub CLI: the Agent Skills spec check `validate.yml` runs.
- If a change alters what a skill *does*, add a line or two under `## [Unreleased]` in `CHANGELOG.md`. The reasoning belongs beside the code.
- Moving the template pin: change `LINKML_TEMPLATE_REF` and `LINKML_TEMPLATE_SHA` in the scaffold driver, re-walk `template-assumptions.md` against the new version and bump its heading, re-run the slow tests, and update the version in `SKILL.md`'s Sources note. The contract holds every mention to the one pin.
- A template file under `templates/github/` or `templates/forgejo/` names every action by commit SHA with its version in a comment; Dependabot does not reach either, so copy each bump of the repository's own workflows into both in the same pull request. The contract fails until they agree.
- `actionlint` cannot read the Forgejo template, which names Codeberg's runner label and each action by its full address, so `tests/test_forgejo_workflow.py` holds its shape. Run a change to it once with `forgejo-runner exec --image ghcr.io/catthehacker/ubuntu:act-latest`, Codeberg's default image.
- The pull request template's checklist is the short form of this list.

## Editing scope

This repository packages and distributes the two skills. A change to what an agent should *do*, such as a different scaffold step or a new rule in linkml-author, needs its *why* in the pull request. Every change keeps the boundary: linkml-sidecar installs and repairs, linkml-author authors, and neither edits a generated file or a template-owned one.

## Code of conduct

Participation here is covered by the [Contributor Covenant](CODE_OF_CONDUCT.md).

## Using AI tools

AI assistance is welcome; these skills exist for agents to run. You are still the author of whatever you submit, responsible for understanding and defending it in review, and an agent may not take part in discussion on your behalf. The full rules are in [AI_COVENANT.md](AI_COVENANT.md).

## Releasing (maintainers)

Each merge to `main` that carries a `feat:`, `fix:`, `security:` or breaking commit waits in `semantic-release.yml` for a reviewer of the `release` environment; once approved, it promotes `## [Unreleased]` to the next version. Then run `publish.yml` by hand with that version: it checks the contract and the tests again, and `gh skill publish` creates the tag and the release, so both skills release together under that tag. A pull request whose commits would release needs a typed title, since a squash merge takes its subject from it. Installers read the tag; the plugin marketplace reads `main`, and `plugin.json` carries no `version` so that it always does.
