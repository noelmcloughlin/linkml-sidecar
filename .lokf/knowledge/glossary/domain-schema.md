---
type: GlossaryTerm
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/glossary/domain-schema
title: Domain schema
description: A LinkML schema that imports LOKF's core schema so its is_a Concept classes become types a .lokf/ bundle's concepts may carry, checked by lokf validate --schema; beside a KTL bundle the sidecar's schema is one.
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
  at: "2026-10-21T22:30:32Z"
status: draft
---

# Overview

A **domain schema** is a LinkML schema importing LOKF's, whose `is_a: Concept` classes the bundle's concepts may name in `type`, checked by `lokf validate --schema`. Every class is closed, so a concept carries only the slots its class declares, and a concept writes its class name in `type` exactly.

Beside a KTL bundle, the sidecar's schema is the bundle's domain schema. ktl-librarian's domain-schema page is the authority on what the validator expects.
