---
type: Service
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/services/linkml-sidecar-workflow
title: linkml-sidecar workflow
description: The workflow the sidecar installs in Step 5. On GitHub, templates/github/linkml-sidecar.yaml at .github/workflows/linkml-sidecar.yaml lints and tests in .linkml/ from the locked environment, builds the docs site on the default branch, and publishes it under the linkml/ subpath of gh-pages only while LINKML_DOCS_ENABLED is true. On Forgejo and Codeberg, templates/forgejo/linkml-sidecar.yaml runs the same gate and publishes to Codeberg Pages.
resource: skills/linkml-sidecar/templates/github/linkml-sidecar.yaml
tags:
  - github actions
  - forgejo actions
  - codeberg
  - workflow
  - gh-pages
  - LINKML_DOCS_ENABLED
isPartOf:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/playbooks/linkml-sidecar-skill
references:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/template-assumptions
sources:
  - resource: skills/linkml-sidecar/templates/github/linkml-sidecar.yaml
  - resource: skills/linkml-sidecar/templates/forgejo/linkml-sidecar.yaml
  - resource: skills/linkml-sidecar/references/automation.md
  - resource: skills/linkml-sidecar/SKILL.md
  - resource: CONTRIBUTING.md
generated:
  by: process:ktl-librarian
  at: "2026-10-22T18:19:05Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T15:14:26Z"
---

# Overview

On GitHub, `templates/github/linkml-sidecar.yaml` is installed in Step 5 at `.github/workflows/linkml-sidecar.yaml`. On Forgejo and Codeberg, `templates/forgejo/linkml-sidecar.yaml` takes its place. Neither template has placeholders, so every host carries the same bytes. The template's own workflows under `.linkml/.github/` stay as inert copies, because GitHub reads `.github/workflows/` at the root only.

## Jobs

- `lint-and-test` runs on a pull request or a push to any branch that touches `.linkml/**`, `.lokf/lokf.yaml` or the workflow, and on dispatch. In `.linkml/` it runs `uv sync --locked --group dev`, `just lint` and `just test` on Python 3.12.
- `docs` runs on the same events, on the default branch only, after the gate. It runs `just gen-doc` and `mkdocs build`, and keeps the site as the `linkml-docs` artifact.
- `publish-docs` runs after `docs`, only while the repository variable `LINKML_DOCS_ENABLED` is `true`. It publishes the artifact under the `linkml/` subpath of the host's `gh-pages` branch and replaces that subpath and nothing else.

`--locked` means the lock the host committed is what runs, so a sidecar whose `uv.lock` is not in git fails at the install step.

With `--adopt`, the schema sits outside `.linkml/`, so Step 5 adds its folder (`"<dir>/**"`) to both `paths:` lists, and an edit to the schema runs the gate too.

## Pins

Every `uses:` names a commit, with the version in a trailing comment. Dependabot reaches this repository's own workflows only, so the contract fails until a bump is copied into both templates too.

## Forgejo and Codeberg

`templates/forgejo/linkml-sidecar.yaml` runs the same gate on Forgejo Actions, as Codeberg runs them. Step 5 puts it in the folder the preflight's `workflows` line names. Forgejo reads only the first of `.forgejo/workflows/`, `.gitea/workflows/` and `.github/workflows/` that exists, so a new `.forgejo/workflows/` beside an existing `.github/workflows/` would hide every workflow there from it.

It differs from the GitHub template only where Forgejo does:

- Both jobs run on Codeberg's `codeberg-small` runner. On a self-hosted Forgejo, the two `runs-on` lines name one of its runners' labels, and the host owns that copy from then on.
- It has no harden-runner and no permissions block.
- Each action is named by its full address, so the file does not depend on the instance's default action mirror.
- The `docs` job builds the site and publishes it in one job, because the stock upload-artifact and download-artifact actions fail on Forgejo.
- It publishes with Codeberg's git-pages action under the `linkml/` subpath of `https://<owner>.codeberg.page/<repo>/`, once `LINKML_DOCS_ENABLED` is `true`. A self-hosted Forgejo has no Pages, so the variable stays unset there, and the job builds the site and stops.

On Codeberg, Actions are off by default. They are turned on in the repository's settings, under Units, Overview.

## Other forges

On GitLab, Gitea or a forge with no CI of its own, the install, lint, test and `mkdocs build` steps are plain shell in `.linkml/` and port unchanged. They run as a job of the host's existing CI, with `.linkml` as its working directory. GitLab Pages serves a `public/` folder from the pipeline, so the host's own Pages job copies `.linkml/site` to `public/linkml/`. Gitea runs the GitHub Actions syntax, so the Forgejo template is the nearer start there, but it has not been run on Gitea.
