---
type: GlossaryTerm
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/glossary/sidecar
title: Sidecar
description: A hidden folder, .linkml/, that holds a complete schema project beside a host's own code, around a dummy schema or a schema the host already holds, with nothing in the host's build depending on it.
definition: A hidden .linkml/ folder holding a complete, pinned linkml-project-copier project inside a host repository, with one visible doorway, one workflow and a README that says how to remove it, and nothing in the host's build depending on it.
resource: docs/architecture.md
tags:
  - sidecar
  - .linkml
sources:
  - resource: docs/architecture.md
  - resource: README.md
  - resource: skills/linkml-sidecar/references/layouts.md
  - resource: skills/linkml-sidecar/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-22T18:19:05Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T15:14:26Z"
---

# Overview

A **sidecar** is one hidden folder, `.linkml/`, beside the host's code. It holds a complete, pinned linkml-project-copier project, around a dummy schema or around a schema the repository already holds. The project keeps the schema in one file, and a `just` recipe for every generator, from JSON Schema and Pydantic models to OWL, SHACL, TypeScript and a documentation site.

One visible doorway, `linkml_schema`, links to the schema's folder for file managers that hide dot-folders. An adopted schema gets no doorway, because it is already visible in place.

One workflow checks the schema on every pull request that touches it. Nothing in the host's build depends on any of it, and the README inside says how to remove it.

The schema is the source: everything the generators write is build output.

Upstream LinkML may also name `.linkml/` for its configuration files. Only `.linkml/.copier-answers.yml` marks a sidecar, and the scaffold installs around any other files it finds there.
