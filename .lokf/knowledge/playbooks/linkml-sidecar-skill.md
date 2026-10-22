---
type: Playbook
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/playbooks/linkml-sidecar-skill
title: linkml-sidecar skill
description: "The installer skill: it runs once to put a hidden .linkml/ LinkML schema project from linkml-project-copier into a host repository, around a dummy schema or around a schema the host already holds (--adopt), without touching the host's build, repairs one file it owns, and hands off to linkml-author."
genre: how-to
resource: skills/linkml-sidecar/SKILL.md
tags:
  - linkml
  - sidecar
  - copier
  - scaffold
dependsOn:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/services/linkml-scaffold
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/services/linkml-preflight
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/linkml-project-copier
references:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/playbooks/linkml-author-skill
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/services/linkml-sidecar-workflow
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/template-assumptions
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/explanation/ktl-mode
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/schema-layouts
definedBy:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/agent-skills-specification
sources:
  - resource: skills/linkml-sidecar/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-22T01:26:03Z"
status: draft
---

# Overview

**linkml-sidecar** creates a `.linkml/` sidecar inside the repository it is invoked from. The sidecar is a complete [LinkML](https://linkml.io) schema project made by linkml-project-copier, with the schema in one file, every generator one recipe away, and a small dummy schema. Nothing in the host's build changes. A schema the repository already holds gets the same toolchain around it, where it is (`--adopt`). The skill then hands off to **linkml-author**, which replaces the dummy with the real model.

## Three cases

- A repository that is itself a schema project, such as lmodel/gist, runs copier at its root and needs nothing from this skill.
- A domain codebase whose maintainers would resist a schema project in their root folder gets the sidecar: one hidden folder, one visible doorway, one workflow, and a README that says so.
- A repository that holds a schema but no project, which is most of them, gets the sidecar around that schema, untouched where it lies.

## When to use it

Use it when a repository has no LinkML schema project yet and someone asks to add, scaffold, bootstrap or set up a LinkML sidecar, schema project, data model or domain schema. It works with or without a KTL `.lokf/` bundle. Use it also to repair a missing or broken sidecar file (`--repair`), or to re-add the root pointers (`--pointers-only`). It never authors classes.

A `.linkml/.copier-answers.yml` means a sidecar exists, so use linkml-author instead. A schema project anywhere else, told by copier answers naming the template or by a `config.public.mk`, is reported and never migrated unasked. A `.linkml/` that holds only configuration files is installed around and never emptied, and a name both hold is refused.

## What it needs

The `compatibility` field asks for bash (Git for Windows on Windows) and `uv`, which runs copier, just and the project's own Python. The scaffold needs one network run to github.com and pypi.org, and the project needs Python 3.10 or later. Any forge works, or none. The Step 5 workflow is GitHub Actions.

## How it runs

1. Step 0 runs the preflight and gathers the host's facts from real sources: the name, description, owner, licence, `SCHEMA_ID` and `DOCS_URL`. It also decides between the dummy and adoption: one schema file found means `--adopt <file>`, and several mean the person chooses.
2. One script, `scripts/linkml-scaffold.sh`, does Steps 1 to 3. It scaffolds into a staging directory, moves the files into `.linkml/`, adds the root pointers and the `linkml_schema` doorway, and prints the hand-off facts. An adopted schema gets none of the root pointers, because it is already visible where it lies.
3. Step 4 runs `just install`, `just lint` and `just test` inside `.linkml/`, and in KTL mode `lokf validate` too.
4. Step 5 optionally installs one workflow at `.github/workflows/linkml-sidecar.yaml`.
5. Step 6 hands off to linkml-author, naming every guessed value, `SCHEMA_ID` above all.

The skill never runs `just setup`, which runs `git init` and commits, or `just deploy`, which pushes the host's `gh-pages` branch root. It never edits a template-owned file by hand. `just update` changes those.

The procedure stays in `skills/linkml-sidecar/SKILL.md`.
