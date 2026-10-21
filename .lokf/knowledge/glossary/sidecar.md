---
type: GlossaryTerm
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/glossary/sidecar
title: Sidecar
description: A hidden folder, .linkml/, that holds a complete schema project beside a host's own code, with nothing in the host's build depending on it.
definition: A hidden .linkml/ folder holding a complete, pinned linkml-project-copier project inside a host repository, with one visible doorway, one workflow and a README that says how to remove it, and nothing in the host's build depending on it.
resource: README.md
tags:
  - sidecar
  - .linkml
sources:
  - resource: README.md
generated:
  by: process:ktl-librarian
  at: "2026-10-21T22:30:32Z"
status: draft
---

# Overview

A **sidecar** is one hidden folder, `.linkml/`, holding a complete, pinned linkml-project-copier project, with one visible doorway (`linkml_schema/`), one workflow, and a README inside that says how to remove it. Nothing in the host's build depends on it. The schema is the source, and every other artefact is generated from it.
