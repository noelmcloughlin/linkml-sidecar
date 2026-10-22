---
type: Reference
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/knowledge-trust-ladder
title: Knowledge Trust Ladder
description: The Knowledge Trust Ladder (KTL), whose bundle is a .lokf/ folder in the host; beside one, the sidecar's schema becomes the bundle's domain schema, and ktl-librarian's domain-schema page is the authority on what lokf validate expects.
genre: reference
resource: https://w3id.org/ktl
tags:
  - ktl
  - lokf
  - knowledge bundle
sources:
  - resource: README.md
  - resource: docs/architecture.md
  - resource: skills/linkml-sidecar/references/ktl.md
generated:
  by: process:ktl-librarian
  at: "2026-10-22T18:19:05Z"
status: draft
verified:
  - by: process:ktl-librarian
    at: "2026-10-22T15:14:26Z"
---

# Overview

A [Knowledge Trust Ladder](https://w3id.org/ktl) (KTL) bundle is a `.lokf/` folder in the host. The sidecar stands alone, and beside a KTL bundle its schema becomes the bundle's domain schema. A schema the host already held (`--adopt`) is not made the domain schema.

ktl-librarian's [domain-schema page](https://github.com/noelmcloughlin/knowledge-trust-ladder/blob/main/skills/ktl-librarian/references/domain-schema.md) is the recipe and the authority on what the validator expects. linkml-sidecar's `references/ktl.md` says how the scaffold sets it up.
