---
type: Playbook
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/playbooks/contributing
title: Contributing
description: "The contributor checklist: development setup, the fast tests, the slow tests and the clone of the pinned template they need, the install smoke test, what to run before a pull request, how to move the linkml-project-copier template pin, and how action pins in the GitHub and Forgejo workflow templates follow Dependabot."
genre: how-to
resource: CONTRIBUTING.md
tags:
  - contributing
  - tests
  - template pin
  - forgejo
dependsOn:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/services/repository-contract
references:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/glossary/template-pin
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/template-assumptions
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/policies/releasing
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/policies/ai-covenant
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/policies/code-of-conduct
sources:
  - resource: CONTRIBUTING.md
  - resource: .github/pull_request_template.md
  - resource: tests/conftest.py
  - resource: scripts/smoke-test-install.sh
generated:
  by: process:ktl-librarian
  at: "2026-10-22T18:19:05Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T15:14:26Z"
---

# Overview

There is no build step: the skills are Markdown, YAML, shell and Python. Clone the repository, then run the contract and the fast tests:

```bash
bash scripts/validate-repository.sh
uv run --no-project --with-requirements tests/requirements.txt pytest
```

The fast tests run the scaffold against `tests/fake_copier.py`, an offline stand-in for copier, and make no network call. The slow tests run the real template. Clone the pinned tag, then run pytest with `LINKML_SIDECAR_SLOW=1`. They need uv, just and the network:

```bash
git clone --branch v0.5.0 https://github.com/linkml/linkml-project-copier .template-cache/linkml-project-copier
LINKML_SIDECAR_SLOW=1 uv run --no-project --with-requirements tests/requirements.txt pytest -m slow
```

To try a change end to end, run `bash scripts/smoke-test-install.sh "$PWD"`. It installs the skills from your clone into a throwaway repository with `npx skills`, then runs the installed preflight and the scaffold's dry run from there.

## Before a pull request

- Run `bash scripts/validate-repository.sh` and `pytest`. CI runs both, plus ShellCheck, `actionlint`, markdownlint, lychee, codespell, the install smoke test and the slow tests.
- Run `gh skill publish --dry-run` if you have the GitHub CLI. It is the Agent Skills spec check that `validate.yml` runs.
- Add a line or two under `## [Unreleased]` in `CHANGELOG.md` when a change alters what a skill does.
- To move the template pin, change `LINKML_TEMPLATE_REF` and `LINKML_TEMPLATE_SHA` in the scaffold driver, re-walk `template-assumptions.md` against the new version and bump its heading, re-run the slow tests, and update the version in `SKILL.md`'s Sources note. The contract holds every mention to the one pin.
- A template file under `templates/github/` or `templates/forgejo/` names every action by commit SHA, with its version in a comment.
- Dependabot does not reach either folder, so copy each bump of the repository's own workflows into both in the same pull request. The contract fails until they agree.
- `actionlint` cannot read the Forgejo template, which names Codeberg's runner label and each action by its full address, so `tests/test_forgejo_workflow.py` holds its shape. Run a change to it once with `forgejo-runner exec --image ghcr.io/catthehacker/ubuntu:act-latest`, Codeberg's default image.

The pull request template's checklist is the short form of this list.

## Editing scope

A change to what an agent should do needs its reason in the pull request, and keeps the boundary: linkml-sidecar installs and repairs, linkml-author authors, and neither edits a generated file or a template-owned one.
