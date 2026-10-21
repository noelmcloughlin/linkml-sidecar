---
type: Service
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/services/repository-contract
title: Repository contract
description: "scripts/validate-repository.sh and the validate.yml workflow: the checks every pull request runs on this repository, covering skill shape, links, word budgets, the one template pin, shared action pins, prerequisites rows, the changelog, invisible characters, plus pytest, ShellCheck, actionlint, markdownlint, lychee, codespell and the install smoke test."
resource: scripts/validate-repository.sh
tags:
  - ci
  - validate
  - contract
references:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/glossary/template-pin
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/services/linkml-sidecar-workflow
sources:
  - resource: scripts/validate-repository.sh
  - resource: .github/workflows/validate.yml
  - resource: .github/dependabot.yml
generated:
  by: process:ktl-librarian
  at: "2026-10-21T22:30:32Z"
status: draft
---

# Overview

`scripts/validate-repository.sh` is the repository contract. Its numbered checks are:

1. exactly the intended skill directories exist;
2. each `SKILL.md` exists with that exact filename, and
3. its declared name matches its directory; each skill states `compatibility`, and each description ends in a `Keywords:` list;
4. no duplicate `SKILL.md` under `skills/`, and none under `templates/`;
5. relative references resolve from each linking file's own directory;
6. shell scripts pass ShellCheck, and Python scripts compile;
7. word budgets, for each `SKILL.md` and for `CONTRIBUTING.md`;
8. the one template pin, held in the scaffold driver, and every other mention of it;
9. every action in the workflow template and this repository's own workflows is pinned to a commit, and an action both use carries the same commit in both;
10. every line the preflight can print as missing or a warning has a row in `prerequisites.md`;
11. `CHANGELOG.md` never carries two headings for one released version;
12. no tracked file holds a character a reader cannot see;
13. the lokf fixture's justfile is ktl-sidecar's template, rendered.

Check 9 leaves the `knowledge-*.yaml` workflows out of the shared-pin comparison, because they are ktl-sidecar's copies and carry the pinned KTL release's pins.

## The workflow

`.github/workflows/validate.yml` runs on every pull request, every push to `main`, weekly on Mondays at 06:00 UTC, and on demand. Each concern is its own job: the contract and the Agent Skills spec check (`gh skill publish --dry-run`), the fast and slow tests, ShellCheck, actionlint, the install smoke test, and markdownlint, lychee, a GitHub issue and pull request link check through the API, and codespell.
