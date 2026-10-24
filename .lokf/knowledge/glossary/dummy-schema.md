---
type: GlossaryTerm
id: https://w3id.org/ktl/linkml-sidecar/knowledge/glossary/dummy-schema
title: Dummy schema
description: The small placeholder schema a fresh sidecar holds, a Person example or, beside a KTL bundle, ExampleConcept, which lints clean and which linkml-author replaces with the host's real model.
definition: The skill-owned placeholder schema the scaffold writes in a fresh sidecar, Person or, in KTL mode, ExampleConcept, which linkml-author replaces with the host's real model.
resource: skills/linkml-sidecar/templates/linkml/schema/plain/schema.yaml
tags:
  - dummy
  - placeholder
sources:
  - resource: skills/linkml-author/SKILL.md
  - resource: skills/linkml-sidecar/SKILL.md
  - resource: skills/linkml-sidecar/references/template-assumptions.md
  - resource: skills/linkml-sidecar/templates/linkml/schema/plain/schema.yaml
  - resource: skills/linkml-sidecar/templates/linkml/schema/lokf/schema.yaml
generated:
  by: process:ktl-librarian
  at: "2026-10-22T01:26:03Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T18:19:05Z"
---

# Overview

A fresh sidecar holds a **dummy schema**: the `Person` example, or, beside a KTL bundle, `ExampleConcept`. It comes from `templates/linkml/schema/plain/` or `templates/linkml/schema/lokf/`, not from the template, because the upstream example fails `just lint`. The scaffold answers `add_example: false` so copier never generates that example, and writes a dummy that lints clean.

linkml-author's first run replaces the dummy with the host's model, keeping the dummy's data files only while its classes remain.

An adopted schema gets no dummy. The scaffold refuses to write the dummy beside a schema the host already holds unless `--dummy` asks for it.
