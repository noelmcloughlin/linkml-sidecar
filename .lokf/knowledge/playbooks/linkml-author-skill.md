---
type: Playbook
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/playbooks/linkml-author-skill
title: linkml-author skill
description: "The authoring skill: it adds, changes or deprecates LinkML classes, slots, enums and types, replaces the dummy schema with the host's real model, and runs lint, gen-project and test after every change, in any repository that holds a schema: the .linkml/ sidecar, a copier or cookiecutter project wherever it sits, or a schema file on its own."
genre: how-to
resource: skills/linkml-author/SKILL.md
tags:
  - linkml
  - schema authoring
  - data model
dependsOn:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/services/linkml-preflight
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/linkml
references:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/playbooks/linkml-sidecar-skill
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/glossary/the-gate
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/explanation/ktl-mode
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/schema-layouts
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/schema-design
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/publishing
definedBy:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/agent-skills-specification
sources:
  - resource: skills/linkml-author/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-22T10:56:45Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T11:13:31Z"
---

# Overview

**linkml-author** turns a project's LinkML schema into the model its code, data and documents describe, and keeps it linted, generated, documented and tested after every change. The schema is one YAML file, or a few modules, and everything else is generated from it. So the skill edits the schema and runs the recipes, and never edits a generated file.

## When to use it

Use it when someone asks to:

- add, change or deprecate a class, slot, enum or type;
- model a concept;
- map a specification, standard or document to a schema;
- replace the dummy schema with the real model;
- refactor or split a schema;
- check schema conventions;
- run lint, gen-project, gen-doc or test.

It is not for installing or repairing the sidecar: linkml-sidecar's `--repair` restores a missing or broken sidecar file.

## What it needs

The `compatibility` field asks for bash. Every LinkML tool runs through the host's own environment, in the first form that applies: the project's `justfile`, its `Makefile`, `uv run` or `poetry run` when the host's `pyproject.toml` names `linkml`, or else a pinned `uvx --from linkml`. It never runs a `linkml-lint` or `gen-project` found on the path. It works with or without a `.lokf/` KTL bundle.

## Where it works

A LinkML schema can live in any repository, so the skill finds it by what files say, never by the folder's name. It runs the preflight, or applies the same rule by hand:

- the sidecar, told by `.linkml/.copier-answers.yml`. Its `config.public.mk` names the schema, and an adopted schema sits outside `.linkml/`, where `LINKML_SCHEMA_SOURCE_DIR` points;
- a schema project at the root, in `linkml/`, one directory down or in the directory the skill was started in, told by copier answers whose `_src_path` names linkml-project-copier, or by a `config.public.mk`;
- a schema file on its own, told by its content.

A `.linkml/` that holds only configuration files is not a layout, and the skill looks on. When it finds several schemas, it asks the person which one, or lists them and stops when no person is there.

## What it follows

After every schema edit it runs the gate: `lint`, then `gen-project`, then `test`. A schema on its own has no recipes, so its gate runs `linkml-lint`, `gen-project` into a temporary folder and `linkml-validate` over the host's example data. Its rules table settles naming, slots versus attributes, modules, references between classes, variants of one thing, enum inheritance, versions, publishing, descriptions, mappings, deprecation and refactoring. An lmodel project follows `references/lmodel-profile.md`, opted into by the project's own conventions and never assumed. Beside a KTL bundle, the schema is the bundle's domain schema only when `.lokf/justfile` names it or it imports `.lokf/lokf.yaml`, and `lokf validate` then runs after the gate.

`generators.yaml`, the generators' settings moved out of `config.yaml`, is the project's to edit. When the preflight offers that move, the skill offers it to the person, and linkml-sidecar's `--repair generators.yaml` makes it.

The preflight's `authors` line says how many people have committed to the schema folder. The skill offers a refactor when that history is one or two people, never when it is a team's, and a known importer narrows the offer to the moves that touch no record. It never refactors unasked.

The procedure stays in `skills/linkml-author/SKILL.md`. Its `references/` hold the metamodel, generator pitfalls by version, source mapping, schema design for reuse, publishing and importing, the lmodel profile and the KTL rules.
