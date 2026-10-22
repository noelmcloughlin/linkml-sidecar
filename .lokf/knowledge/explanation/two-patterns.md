---
type: Explanation
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/explanation/two-patterns
title: Three cases, one skill
description: "Why there are three ways to give a repository a LinkML schema: a repository that is itself a schema project runs copier at its root and needs nothing here, a domain codebase whose maintainers do not want a schema project in their root gets the hidden .linkml/ sidecar, and a repository holding a schema but no project gets the sidecar around that schema."
genre: explanation
resource: README.md
tags:
  - sidecar
  - copier at the root
  - adopt
about:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/glossary/sidecar
references:
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/playbooks/linkml-sidecar-skill
  - https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/template-assumptions
sources:
  - resource: README.md
  - resource: skills/linkml-sidecar/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-22T15:14:26Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T09:04:50Z"
---

# Overview

A repository that *is* a schema project, such as [lmodel/gist](https://github.com/lmodel/gist), runs copier at its root itself, in one command, and needs no sidecar. linkml-author works there as it is.

A domain codebase whose maintainers do not want a schema project in their root folder gets the sidecar: one hidden folder, one visible doorway (`linkml_schema/`), one workflow, and a README inside that says how to remove it. Nothing in the host's build depends on it.

A repository that holds a LinkML schema but no project gets the sidecar around that schema (`--adopt`). It gains the pinned lock, the recipes, the tests, the workflow and the docs site, and the schema is neither moved nor changed.

Both skills find the schema by its files (copier answers, a `config.public.mk`, or a YAML file that imports `linkml:types`), never by the folder's name, and linkml-author works on the schema in every case.

## Why the sidecar needs a skill

linkml-project-copier renders a repository root: its workflows, governance files, README and `setup` recipe all assume one. In a sidecar each of those is wrong, inert or harmful, so the skill neutralises them one by one, from a catalogue of the assumptions.
