---
type: GlossaryTerm
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/glossary/template-pin
title: Template pin
description: "The one place the linkml-project-copier version is fixed: LINKML_TEMPLATE_REF and LINKML_TEMPLATE_SHA in the scaffold driver, a tag verified against its commit before copier runs with --trust."
definition: The tag and commit of linkml-project-copier the sidecar is made from, held as LINKML_TEMPLATE_REF and LINKML_TEMPLATE_SHA in skills/linkml-sidecar/scripts/linkml-scaffold.sh and recorded in .copier-answers.yml as _commit.
resource: skills/linkml-sidecar/scripts/linkml-scaffold.sh
tags:
  - pin
  - v0.5.0
  - LINKML_TEMPLATE_REF
sources:
  - resource: skills/linkml-sidecar/scripts/linkml-scaffold.sh
  - resource: CONTRIBUTING.md
  - resource: skills/linkml-sidecar/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-21T22:30:32Z"
status: draft
---

# Overview

The **template pin** is held in one place, the scaffold driver: `LINKML_TEMPLATE_REF` (the tag, `v0.5.0`) and `LINKML_TEMPLATE_SHA` (the commit it names). Before copier runs with `--trust`, the scaffold checks with `git ls-remote` that the tag still names that commit, so a moved tag stops the scaffold. A finished sidecar records the pin in `.copier-answers.yml` as `_commit: v0.5.0`.

The repository contract holds every other mention under `skills/` and in `README.md` to these two values. Moving the pin is a contributor's checklist item: change both values, re-walk the assumptions catalogue, re-run the slow tests, and update the Sources note in `SKILL.md`. In a host, `cd .linkml && just update` on a clean tree moves the template.
