---
type: Document
id: https://w3id.org/ktl/linkml-sidecar/knowledge/references/template-assumptions
title: Template assumptions catalogue
description: The catalogue, at template v0.5.0, of the twenty things linkml-project-copier assumes of a repository root (just setup, just deploy, nested workflows, the governance files, mkdocs URLs, --trust, just update, config.public.mk, the generators' settings and more), what the scaffold does about each, and which an upstream layout answer would remove.
genre: reference
resource: skills/linkml-sidecar/references/template-assumptions.md
tags:
  - copier
  - root assumptions
  - just setup
  - just deploy
about:
  - https://w3id.org/ktl/linkml-sidecar/knowledge/references/linkml-project-copier
references:
  - https://github.com/linkml/linkml-project-copier/issues/187
sources:
  - resource: skills/linkml-sidecar/references/template-assumptions.md
generated:
  by: process:ktl-librarian
  at: "2026-10-22T17:44:49Z"
status: draft
---

# Overview

`skills/linkml-sidecar/references/template-assumptions.md` is the catalogue the scaffold implements, row by row, at template **v0.5.0**. It is for whoever maintains the skill. Each row names one root-install assumption, what the skill does about it, and whether an upstream `layout: sidecar` answer would remove it.

Some of the rows:

- `just setup` runs `git init`, `git add .` and a commit, so it is never run, and the scaffold fails if `.linkml/.git` appears.
- `just deploy` pushes the host's `gh-pages` branch root, so it is never run; the Step 5 docs job publishes under the `linkml/` subpath only.
- The template's workflows render inside the project, where GitHub never reads them, so a hoisted workflow runs the gate from the root.
- The upstream example fails `just lint`, so the answer is `add_example: false`, and a skill-owned dummy that lints clean takes its place.
- `--trust` is required, so the tag and its commit are verified before copier runs.
- `config.public.mk` names the schema, every recipe derives its paths from it, and upstream calls the file a convenience it may retire. Adoption points `LINKML_SCHEMA_SOURCE_DIR` at the host's folder, and the preflight falls back to the answers' `project_slug` when the file is absent.
- `config.yaml` holds the generators' settings and `config.public.mk` names it. A new sidecar renames it `generators.yaml`, and `--repair generators.yaml` moves an existing project's file. After the move, `copier update` no longer carries the template's changes to the settings.

Rows marked *no* are facts about LinkML, uv or git rather than about the template, and stay whatever upstream does. When the pin moves, bump the page's heading and re-walk the rows.
