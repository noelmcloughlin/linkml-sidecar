---
type: Service
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/services/linkml-sidecar-workflow
title: linkml-sidecar workflow
description: "The one GitHub Actions workflow the sidecar installs at .github/workflows/linkml-sidecar.yaml: lint and test in .linkml/ from the locked environment, build the docs site on the default branch, and publish it under the linkml/ subpath of gh-pages only while LINKML_DOCS_ENABLED is true."
resource: skills/linkml-sidecar/templates/github/linkml-sidecar.yaml
tags:
  - github actions
  - workflow
  - gh-pages
  - LINKML_DOCS_ENABLED
isPartOf:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/playbooks/linkml-sidecar-skill
references:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/template-assumptions
sources:
  - resource: skills/linkml-sidecar/templates/github/linkml-sidecar.yaml
  - resource: skills/linkml-sidecar/references/automation.md
generated:
  by: process:ktl-librarian
  at: "2026-10-21T22:30:32Z"
status: draft
---

# Overview

`templates/github/linkml-sidecar.yaml` is installed in Step 5 at `.github/workflows/linkml-sidecar.yaml`. It has no placeholders, so every host carries the same bytes. The template's own workflows under `.linkml/.github/` stay as inert copies, because GitHub reads `.github/workflows/` at the root only.

## Jobs

- `lint-and-test` runs on a pull request or a push to any branch that touches `.linkml/**`, `.lokf/lokf.yaml` or the workflow, and on dispatch. In `.linkml/` it runs `uv sync --locked --group dev`, `just lint` and `just test` on Python 3.12.
- `docs` runs on the same events, on the default branch only, after the gate. It runs `just gen-doc` and `mkdocs build`, and keeps the site as the `linkml-docs` artifact.
- `publish-docs` runs after `docs`, only while the repository variable `LINKML_DOCS_ENABLED` is `true`. It publishes the artifact under the `linkml/` subpath of the host's `gh-pages` branch and replaces that subpath and nothing else.

`--locked` means the lock the host committed is what runs, so a sidecar whose `uv.lock` is not in git fails at the install step.

## Pins

Every `uses:` names a commit, with the version in a trailing comment. Dependabot reaches this repository's own workflows only, so the contract fails until a bump is copied into the template too.

## Other forges

The install, lint, test and `mkdocs build` steps are plain shell in `.linkml/` and port unchanged. Publishing has to be rewritten: GitLab Pages serves a `public/` artifact, and Forgejo and Gitea have no Pages of their own.
