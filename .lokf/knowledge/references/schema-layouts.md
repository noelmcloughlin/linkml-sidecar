---
type: Document
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/schema-layouts
title: Where a LinkML schema lives
description: "The rule both skills apply to find a LinkML schema in any repository: copier answers naming linkml-project-copier, a config.public.mk, or a schema file found by content; where the preflight looks; and how --adopt gives a found schema the toolchain in place."
genre: reference
resource: skills/linkml-sidecar/references/layouts.md
tags:
  - layouts
  - schema discovery
  - adopt
  - config.public.mk
references:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/services/linkml-preflight
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/services/linkml-scaffold
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/playbooks/linkml-author-skill
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/playbooks/linkml-sidecar-skill
sources:
  - resource: skills/linkml-sidecar/references/layouts.md
generated:
  by: process:ktl-librarian
  at: "2026-10-22T01:26:03Z"
status: draft
---

# Overview

`skills/linkml-sidecar/references/layouts.md` states where a LinkML schema may live and how both skills find it. Most schemas were never made with linkml-project-copier or its predecessor, linkml-project-cookiecutter, and a project's folder has no fixed name. So both skills find the schema by what files say, never by where they sit. The preflight applies the rule in shell, and the scaffold applies it in Python.

## The signals

- A `.copier-answers.yml` whose `_src_path` names `linkml-project-copier` marks a copier project, for as long as copier is used.
- A `config.public.mk` marks a project from copier or from the older cookiecutter, and names the schema. Upstream may retire the file, and the answers' `project_slug` then names the schema.
- A `*.yaml` or `*.yml` file that imports `linkml:types` or names the `linkml:` prefix, and has a top-level `classes:`, `slots:`, `enums:`, `types:`, `subsets:` or `imports:` key, is a schema on its own.

A `.linkml/` folder shows that LinkML is in use, but not what it holds: upstream LinkML may name it for configuration files, and the sidecar names it for a whole project. Only `.linkml/.copier-answers.yml` means the sidecar, and anything else there is left alone.

## Where the preflight looks

It looks in `.linkml/`, at the repository root, in the directory it was started in, and then in every directory one level down, and the first match wins. A second project is reported as `also`, and a person says which one is meant. With no project anywhere, it finds schema files by content among the files git tracks or would track. It skips the folders that by convention hold copies, fixtures or rendered output, such as `docs`, `tests`, `project` and `.lokf`.

## Adoption

`--adopt <file>` gives a schema found outside any project the sidecar's toolchain without moving it. It points `config.public.mk`'s `LINKML_SCHEMA_SOURCE_DIR` at the file's folder, so every recipe reads the schema where it is, and the file is never moved, copied, linked or edited. The file must be named `<slug>.yaml`. Beside a `.lokf/` bundle, the adopted schema is not made the domain schema.
