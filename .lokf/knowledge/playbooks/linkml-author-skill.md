---
type: Playbook
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/playbooks/linkml-author-skill
title: linkml-author skill
description: "The authoring skill: it adds, changes or deprecates LinkML classes, slots, enums and types, replaces the dummy schema with the host's real model, and runs lint, gen-project and test after every change, in a .linkml/ sidecar, a visible linkml/ one or a copier project at the root."
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
definedBy:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/agent-skills-specification
sources:
  - resource: skills/linkml-author/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-21T22:30:32Z"
status: draft
---

# Overview

**linkml-author** turns a project's LinkML schema into the model its code, data and documents describe, and keeps it linted, generated, documented and tested after every change. The schema is one YAML file, or a few modules, and everything else is generated from it. So the skill edits the schema and runs the recipes, and never edits a generated file.

## When to use it

Use it when someone asks to add, change or deprecate a class, slot, enum or type; to model a concept; to map a specification, standard or document to a schema; to replace the dummy schema with the real model; to check schema conventions; or to run lint, gen-project, gen-doc or test. It is not for installing or repairing the sidecar: a missing or broken sidecar file goes back to linkml-sidecar's `--repair`.

## What it needs

The `compatibility` field asks for bash and `uv`. Every LinkML tool runs through the project's own environment (`uv run` inside the schema project), never a globally installed one. It works on any host that holds a linkml-project-copier project, with or without a `.lokf/` KTL bundle.

## Where it works

The skill finds the project through the preflight, in this order:

- the sidecar, `.linkml/`, told by `.linkml/.copier-answers.yml`;
- a visible sidecar made by hand, `linkml/`, told by `linkml/.copier-answers.yml`;
- the repository itself, told by `.copier-answers.yml` at the root.

## What it follows

After every schema edit it runs the gate: `lint`, then `gen-project`, then `test`. Its rules table settles the questions an author meets most, such as naming, slots versus attributes, mappings and deprecation. An lmodel project follows `references/lmodel-profile.md`, opted into by the project's own conventions and never assumed. Beside a KTL bundle the schema is the bundle's domain schema, and `lokf validate` runs after the gate.

The procedure itself stays in `skills/linkml-author/SKILL.md`, with the metamodel, generator pitfalls by version, source mapping, the lmodel profile and the KTL rules in its `references/`.
