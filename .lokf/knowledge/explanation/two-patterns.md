---
type: Explanation
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/explanation/two-patterns
title: Two patterns, one skill
description: "Why there are two ways to give a repository a LinkML schema: a repository that is itself a schema project runs copier at its root and needs nothing here, while a domain codebase whose maintainers do not want a schema project in their root gets the hidden .linkml/ sidecar."
genre: explanation
resource: README.md
tags:
  - sidecar
  - copier at the root
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
  at: "2026-10-21T22:30:32Z"
status: draft
---

# Overview

A repository that *is* a schema project, such as [lmodel/gist](https://github.com/lmodel/gist), runs copier at its root itself, in one command, and needs nothing here.

A domain codebase whose maintainers do not want a schema project in their root folder gets the sidecar: one hidden folder, one visible doorway (`linkml_schema/`), one workflow, and a README inside that says how to remove it. Nothing in the host's build depends on it.

The linkml-sidecar skill does the sidecar only. linkml-author works in both shapes, and in a visible `linkml/` sidecar made by hand.

## Why the sidecar needs a skill

linkml-project-copier renders a repository root: its workflows, governance files, README and `setup` recipe all assume one. In a sidecar each of those is wrong, inert or harmful, so the skill neutralises them one by one, from a catalogue of the assumptions.
