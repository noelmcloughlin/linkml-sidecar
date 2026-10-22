---
type: GlossaryTerm
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/glossary/sidecar
title: Sidecar
description: A hidden folder, .linkml/, that holds a complete schema project beside a host's own code, around a dummy schema or a schema the host already holds, with nothing in the host's build depending on it.
definition: A hidden .linkml/ folder holding a complete, pinned linkml-project-copier project inside a host repository, with one visible doorway, one workflow and a README that says how to remove it, and nothing in the host's build depending on it.
resource: README.md
tags:
  - sidecar
  - .linkml
sources:
  - resource: README.md
  - resource: skills/linkml-sidecar/references/layouts.md
  - resource: skills/linkml-sidecar/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-22T01:26:03Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T09:04:50Z"
---

# Overview

A **sidecar** is one hidden folder, `.linkml/`, holding a complete, pinned linkml-project-copier project, around a dummy schema or around a schema the repository already holds. It has one visible doorway (`linkml_schema/`), one workflow, and a README inside that says how to remove it. Nothing in the host's build depends on it. The schema is the source, and every other artefact is generated from it. An adopted schema gets no doorway, because it is already visible where it lies.

Upstream LinkML may also name `.linkml/` for its configuration files. Only `.linkml/.copier-answers.yml` marks a sidecar, and the scaffold installs around any other files it finds there.
