---
type: Document
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/template-assumptions
title: Template assumptions catalogue
description: The catalogue, at template v0.5.0, of the eighteen things linkml-project-copier assumes of a repository root (just setup, just deploy, nested workflows, the governance files, mkdocs URLs, --trust, just update and more), what the scaffold does about each, and which an upstream layout answer would remove.
genre: reference
resource: skills/linkml-sidecar/references/template-assumptions.md
tags:
  - copier
  - root assumptions
  - just setup
  - just deploy
about:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/linkml-project-copier
references:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/upstream-proposal
sources:
  - resource: skills/linkml-sidecar/references/template-assumptions.md
generated:
  by: process:ktl-librarian
  at: "2026-10-21T22:30:32Z"
status: draft
---

# Overview

`skills/linkml-sidecar/references/template-assumptions.md` is the catalogue the scaffold implements, row by row, at template **v0.5.0**. It is for whoever maintains the skill. Each row names one root-install assumption, what the skill does about it, and whether an upstream `layout: sidecar` answer would remove it.

Some of the rows:

- `just setup` runs `git init`, `git add .` and a commit, so it is never run, and the scaffold fails if `.linkml/.git` appears.
- `just deploy` pushes the host's `gh-pages` branch root, so it is never run; the Step 5 docs job publishes under the `linkml/` subpath only.
- The template's workflows render inside the project, where GitHub never reads them, so a hoisted workflow runs the gate from the root.
- The upstream example fails `just lint`, so `add_example: false` and a skill-owned dummy that lints clean.
- `--trust` is required, so the tag and its commit are verified before copier runs.

Rows marked *no* are facts about LinkML, uv or git rather than about the template, and stay whatever upstream does. When the pin moves, bump the page's heading and re-walk the rows.
