---
type: Reference
id: https://noelmcloughlin.github.io/linkml-sidecar/knowledge/references/linkml
title: LinkML
description: LinkML, the modelling language the sidecar's schema is written in; linkml.io is the canonical site for what it means, its schemas and its generators (JSON Schema, Pydantic, OWL, SHACL, TypeScript, docs).
genre: reference
resource: https://linkml.io
tags:
  - linkml
  - schema language
  - generators
sources:
  - resource: skills/linkml-sidecar/SKILL.md
  - resource: skills/linkml-author/SKILL.md
generated:
  by: process:ktl-librarian
  at: "2026-10-21T22:30:32Z"
status: draft
---

# Overview

[LinkML](https://linkml.io) is the language the sidecar's schema is written in. Both skills name linkml.io as the canonical site for what LinkML means: [schemas](https://linkml.io/linkml/schemas/) for the language and [generators](https://linkml.io/linkml/generators/) for what is generated from it.

In a sidecar the schema is one YAML file, or a few modules, and everything else is generated from it: the JSON Schema, Pydantic and dataclass models, OWL and SHACL, TypeScript and the docs site, one `just` recipe each.
