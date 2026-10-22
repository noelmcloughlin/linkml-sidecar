---
type: GlossaryTerm
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/glossary/domain-schema
title: Domain schema
description: A LinkML schema that imports LOKF's core schema so its is_a Concept classes become types a .lokf/ bundle's concepts may carry, checked by lokf validate --schema; a schema is one only when .lokf/justfile names it or it imports lokf.yaml, as the sidecar's dummy does in KTL mode.
definition: A LinkML schema importing LOKF's core schema, whose classes that are is_a Concept the bundle's concepts may name in type, checked by lokf validate --schema.
resource: skills/linkml-sidecar/references/ktl.md
tags:
  - domain schema
  - lokf
sources:
  - resource: skills/linkml-sidecar/references/ktl.md
  - resource: skills/linkml-author/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-22T01:26:03Z"
status: draft
---

# Overview

A **domain schema** is a LinkML schema importing LOKF's, whose `is_a: Concept` classes the bundle's concepts may name in `type`, checked by `lokf validate --schema`. Every class is closed, so a concept carries only the slots its class declares, and a concept writes its class name in `type` exactly.

In KTL mode, the sidecar's dummy schema is the bundle's domain schema. A bundle beside any other schema does not make it one: a schema is a domain schema only when `.lokf/justfile` names it (`schema :=`) or it imports `.lokf/lokf.yaml`. An adopted schema is not made one, and its maintainers decide whether to connect it. ktl-librarian's domain-schema page is the authority on what the validator expects.
