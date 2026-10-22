---
type: Explanation
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/explanation/two-patterns
title: Three cases, one skill
description: "Why there are three ways to give a repository a LinkML schema: a schema project runs copier at its root and needs no sidecar, a codebase whose maintainers do not want a schema project in their root folder gets the hidden .linkml/ sidecar around a dummy schema, and a repository holding a schema but no project gets the sidecar around that schema (--adopt)."
genre: explanation
resource: docs/architecture.md
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
  - resource: docs/architecture.md
  - resource: skills/linkml-sidecar/SKILL.md
  - resource: skills/linkml-sidecar/references/layouts.md
  - resource: skills/linkml-sidecar/references/template-assumptions.md
generated:
  by: process:ktl-librarian
  at: "2026-10-22T18:19:05Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T09:04:50Z"
---

# Overview

A repository that *is* a schema project, such as [lmodel/gist](https://github.com/lmodel/gist), runs copier at its root itself, in one command, and needs no sidecar. linkml-author works there as it is.

A codebase whose maintainers do not want a schema project in their root folder gets the sidecar, around a small dummy schema that linkml-author replaces. The sidecar is one hidden folder, one visible doorway (`linkml_schema`), one workflow, and a README inside that says how to remove it. Nothing in the host's build depends on it.

A repository that holds a LinkML schema but no project gets the sidecar around that schema (`--adopt`), and the schema is neither moved nor changed. Lint, the generators, the docs and the tests read the schema where it is.

Both skills find a schema by its files, never by its folder's name: copier answers that name linkml-project-copier, a `config.public.mk`, or a YAML file that imports `linkml:types` or names the `linkml:` prefix and has a top-level schema key. `skills/linkml-sidecar/references/layouts.md` sets out the rule.

## Why the sidecar needs a skill

linkml-project-copier assumes it owns a repository root, so it renders workflows, governance files, a `setup` recipe and a `deploy` recipe that are inert or harmful in a subfolder. The scaffold switches each of them off, and `skills/linkml-sidecar/references/template-assumptions.md` says how, row by row.
